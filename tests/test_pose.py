import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import cv2
import numpy as np

from backend.ai.buffer import PoseBuffer
from backend.ai.factory import create_detector, load_settings
from backend.ai.interface import FallDetector
from backend.ai.pose import PoseEstimator, TrackedPose
from backend.contracts import FramePacket
from evaluation.extract import FrameSource, extract_clip, label_at, normalize_window, read_intervals
from evaluation.manifest import build_manifest, read_manifest, split_groups, validate_groups


class ArrayResult(SimpleNamespace):
    def cpu(self): return self
    def numpy(self): return self
    def __len__(self): return len(self.xyxy)

class PoseTests(unittest.TestCase):
    def test_missing_id_joints_reset_and_close(self):
        estimator = PoseEstimator.__new__(PoseEstimator)
        estimator.device = 'cpu'
        estimator.image_size = 480
        estimator.tracker = 'bytetrack.yaml'
        estimator.keypoint_confidence = 0.5
        boxes = ArrayResult(xyxy=np.array([[1, 2, 30, 40]]), conf=np.array([0.8]), id=None)
        joints = np.ones((1, 17, 3), dtype=np.float32)
        joints[0, 0] = [0, 0, 0.9]
        joints[0, 1] = [10, 20, 0.1]
        result = SimpleNamespace(boxes=boxes, keypoints=ArrayResult(data=joints))
        tracker = Mock()
        estimator._model = Mock(predictor=SimpleNamespace(trackers=[tracker], vid_path=['old']))
        estimator._model.track.return_value = [result]
        frame = np.zeros((10, 10, 3), dtype=np.uint8)
        pose = estimator.estimate(frame)[0]
        self.assertIsNone(pose.track_id)
        self.assertTrue(np.isnan(pose.keypoints[:2, :2]).all())
        self.assertEqual(int(pose.valid_keypoints.sum()), 15)
        boxes.id = np.array([7.0])
        result.keypoints = None
        pose = estimator.estimate(frame)[0]
        self.assertEqual(pose.track_id, 7)
        self.assertFalse(pose.valid_keypoints.any())
        result.boxes = None
        self.assertEqual(estimator.estimate(frame), [])
        with self.assertRaises(ValueError): estimator.estimate(frame.astype(float))
        estimator.reset()
        tracker.reset.assert_called_once()
        self.assertEqual(estimator._model.predictor.vid_path, [None])
        estimator.close()
        estimator.close()
        with self.assertRaises(RuntimeError): estimator.estimate(frame)


def packet(index=0, time=0.0, session="s1", camera="cam0"):
    return FramePacket(camera, session, index, time, "2026-11-09T00:00:00+00:00",
                       np.zeros((100, 100, 3), dtype=np.uint8))


def pose(track=1, descent=0.0, valid=True):
    joints = np.ones((17, 3), np.float32)
    joints[:, :2] = [50, 50 + descent]
    joints[:, 2] = 0.9
    joints[[5, 6], :2] = [[40, 20 + descent], [60, 20 + descent]]
    joints[[11, 12], :2] = [[40, 60 + descent], [60, 60 + descent]]
    mask = np.ones(17, bool)
    if not valid:
        joints[[5, 6, 11, 12], :2] = np.nan
        mask[[5, 6, 11, 12]] = False
    return TrackedPose(track, np.array([30, 10 + descent, 70, 90 + descent], np.float32),
                       0.9, joints, mask)


class IntegrationTests(unittest.TestCase):
    def test_mock_three_fixtures_json_and_repeated_frame(self):
        detector = create_detector({"mode": "mock"})
        self.assertIsInstance(detector, FallDetector)
        first = detector.process(packet())
        self.assertIs(first, detector.process(packet()))
        self.assertFalse(first.candidates)
        upright = detector.process(packet(1, 0.1))
        invalid = detector.process(packet(2, 0.2))
        self.assertTrue(upright.candidates[0].valid_pose)
        self.assertFalse(invalid.candidates[0].valid_pose)
        payload = json.loads(json.dumps(invalid.to_dict(), allow_nan=False))
        self.assertTrue(payload["is_test"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertIsInstance(payload["candidates"][0]["reasons"], list)
        self.assertNotIn("image_bgr", payload)
        self.assertFalse(detector.process(packet(0, 0, "s2")).candidates)
        detector.close()
        detector.close()
        with self.assertRaises(RuntimeError):
            detector.process(packet())

    def test_factory_does_not_disguise_missing_scorer(self):
        settings = load_settings()
        with self.assertRaisesRegex(NotImplementedError, "week 2"):
            create_detector({**settings, "mode": "pretrained"})
        with self.assertRaises(ValueError):
            create_detector({"mode": "typo"})


class BufferTests(unittest.TestCase):
    def test_sampling_dedup_bounded_window_and_snapshots(self):
        buffer = PoseBuffer(window_samples=3)
        observed = pose()
        self.assertTrue(buffer.add(packet(), [observed]))
        self.assertFalse(buffer.add(packet(), [observed]))
        observed.keypoints[:] = np.nan
        self.assertTrue(buffer.window(1).samples[0].valid)
        self.assertFalse(buffer.add(packet(1, 0.03), [pose()]))
        for index, time in enumerate([0.1, 0.2, 0.3], 2):
            buffer.add(packet(index, time), [pose()])
        window = buffer.window(1)
        self.assertEqual(len(window.samples), 3)
        self.assertTrue(window.ready)
        self.assertEqual([sample.frame_id for sample in window.samples], [2, 3, 4])

    def test_missing_pose_gap_requires_new_segment_and_session_resets(self):
        buffer = PoseBuffer(window_samples=3)
        buffer.add(packet(), [pose()])
        initial_segment = buffer.window(1).segment_id
        buffer.add(packet(1, 0.1), [])
        self.assertIsNone(buffer.window(1).samples[-1].pose)
        self.assertFalse(buffer.window(1).ready)
        buffer.add(packet(2, 0.5), [pose()])
        self.assertNotEqual(buffer.window(1).segment_id, initial_segment)
        self.assertEqual(len(buffer.window(1).samples), 1)
        buffer.add(packet(0, 0, "s2"), [pose(2)])
        self.assertIsNone(buffer.window(1))
        self.assertEqual(len(buffer.window(2).samples), 1)
        buffer.reset()
        self.assertFalse(buffer.track_ids)

    def test_invalid_joint_gap_cannot_hide_in_a_long_track(self):
        buffer = PoseBuffer(window_samples=3)
        buffer.add(packet(), [pose()])
        segment = buffer.window(1).segment_id
        for index in range(1, 5):
            buffer.add(packet(index, index / 10), [pose(valid=False)])
        self.assertNotEqual(buffer.window(1).segment_id, segment)
        self.assertFalse(buffer.window(1).ready)

    def test_unassigned_ids_are_ignored_and_track_histories_are_separate(self):
        buffer = PoseBuffer()
        buffer.add(packet(), [pose(None), pose(1), pose(2)])
        self.assertEqual(buffer.track_ids, (1, 2))
        buffer.add(packet(1, 0.1), [pose(2)])
        self.assertIsNone(buffer.window(1).samples[-1].pose)
        self.assertTrue(buffer.window(2).samples[-1].valid)

    def test_time_regression_and_bad_settings_fail(self):
        buffer = PoseBuffer()
        buffer.add(packet(0, 1), [pose()])
        with self.assertRaises(ValueError):
            buffer.add(packet(1, 0.9), [pose()])
        for kwargs in ({"sample_hz": 0}, {"window_samples": 0},
                       {"max_pose_gap_seconds": -1}, {"min_valid_window_fraction": 1.2}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                PoseBuffer(**kwargs)

    def test_slow_source_cannot_fill_a_three_second_window_with_six_seconds(self):
        buffer = PoseBuffer(sample_hz=10, window_samples=30)
        for index in range(40):
            buffer.add(packet(index, index * 0.2), [pose()])
        window = buffer.window(1)
        self.assertFalse(window.ready)
        self.assertLess(len(window.samples), 30)
        self.assertLessEqual(window.samples[-1].timestamp - window.samples[0].timestamp, 3.0 + 1e-9)

    def test_normalization_preserves_descent_and_masks_missing_joints(self):
        buffer = PoseBuffer(window_samples=3)
        for index in range(3):
            buffer.add(packet(index, index / 10), [pose(descent=index * 10)])
        features, mask = normalize_window(buffer.window(1))
        self.assertEqual(features.shape, (3, 54))
        self.assertGreater(features[2, 11 * 3 + 1], features[0, 11 * 3 + 1])
        self.assertAlmostEqual(float(features[2, 51]), 0.8, places=5)
        self.assertEqual(float(features[2, 52]), 0)
        buffer.add(packet(3, 0.3), [pose(valid=False)])
        features, mask = normalize_window(buffer.window(1))
        self.assertFalse(mask[-1, 51])
        self.assertFalse(mask[-1, 5 * 3])
        self.assertTrue(np.isfinite(features).all())


class FakeEstimator:
    def __init__(self):
        self.calls = 0
        self.resets = 0

    def reset(self):
        self.resets += 1

    def estimate(self, image):
        self.calls += 1
        joints = np.ones((17, 3), np.float32)
        joints[:, :2] = [15, 20]
        joints[[5, 6], :2] = [[10, 10], [20, 10]]
        joints[[11, 12], :2] = [[10, 30], [20, 30]]
        return [TrackedPose(1, np.array([5, 5, 25, 35], np.float32),
                            0.9, joints, np.ones(17, bool))]


class DataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.images = self.root / "images"
        self.images.mkdir()
        for index in range(12):
            cv2.imwrite(str(self.images / f"frame{index}.png"), np.full((40, 40, 3), index, np.uint8))
        self.record = {"clip_id": "clip1", "path": str(self.images), "group_id": "g1",
                       "recording_id": "r1", "subject_id": "unknown", "camera_id": "cam0",
                       "fps": 10, "timestamps_path": "", "source": "synthetic unit test",
                       "license": "generated for tests"}

    def tearDown(self):
        self.temp.cleanup()

    def second_record(self):
        image = self.root / "other"
        image.mkdir(exist_ok=True)
        cv2.imwrite(str(image / "frame0.png"), np.zeros((40, 40, 3), np.uint8))
        return {**self.record, "clip_id": "clip2", "path": str(image), "recording_id": "r2", "group_id": "g2"}

    def test_natural_frame_order_and_source_time(self):
        with FrameSource(self.images, fps=10) as source:
            frames = list(source)
        self.assertEqual([int(image[0, 0, 0]) for _, _, image in frames], list(range(12)))
        self.assertEqual([timestamp for _, timestamp, _ in frames], [i / 10 for i in range(12)])
        with self.assertRaises(ValueError):
            FrameSource(self.images)

    def test_irregular_timestamps_are_preserved_and_validated(self):
        timestamps = self.root / "times.csv"
        values = [index / 10 + (0.01 if index % 2 else 0) for index in range(12)]
        timestamps.write_text("frame_id,time_s\n" + "".join(f"{i},{t}\n" for i, t in enumerate(values)), encoding="utf-8")
        with FrameSource(self.images, timestamps_path=timestamps) as source:
            self.assertEqual([t for _, t, _ in source], values)
        timestamps.write_text("frame_id,time_s\n0,0\n1,0\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            FrameSource(self.images, timestamps_path=timestamps)

    def test_manifest_roundtrip_split_lock_and_multi_camera_leakage(self):
        records = [self.record, self.second_record()]
        manifest = self.root / "clips.csv"
        build_manifest(records, manifest)
        restored = read_manifest(manifest)
        splits = split_groups(restored)
        self.assertEqual(splits, split_groups(restored))
        validate_groups(restored, splits)
        with self.assertRaises(ValueError):
            validate_groups(restored, {"val_groups": ["g1"], "test_groups": ["g1", "g2"]})
        with self.assertRaises(ValueError):
            validate_groups([self.record, {**records[1], "recording_id": "r1"}], splits)
        with self.assertRaises(ValueError):
            build_manifest([self.record, self.record], manifest)
        with self.assertRaises(ValueError):
            split_groups([self.record])

    def test_annotations_are_intervals_and_unknown_stays_unknown(self):
        labels = self.root / "labels.csv"
        labels.write_text("clip_id,onset_s,impact_s,end_s,label\nclip1,0.2,0.4,0.8,fall\n", encoding="utf-8")
        intervals = read_intervals(labels, {"clip1"})
        self.assertEqual(label_at(0, intervals), "unknown")
        self.assertEqual(label_at(0.3, intervals), "fall")
        self.assertEqual(label_at(0.8, intervals), "unknown")
        labels.write_text("clip_id,onset_s,impact_s,end_s,label\nclip1,0.4,0.2,0.8,fall\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            read_intervals(labels, {"clip1"})

    def test_extract_cache_resume_invalidation_and_runtime_feature_agreement(self):
        output = self.root / "cache.npz"
        estimator = FakeEstimator()
        settings = {"sample_hz": 10, "window_samples": 3}
        intervals = [{"clip_id": "clip1", "onset_s": 0.2, "impact_s": 0.4, "end_s": 0.8, "label": "fall"}]
        state = extract_clip(self.record, estimator, settings, output=output, model_hash="test-model", intervals=intervals)
        self.assertEqual(state, "written")
        self.assertEqual(estimator.calls, 12)
        self.assertEqual(estimator.resets, 2)
        with np.load(output, allow_pickle=False) as cache:
            self.assertEqual(cache["features"].shape, (12, 54))
            self.assertEqual(cache["validity"].dtype, np.bool_)
            np.testing.assert_allclose(cache["timestamps"], np.arange(12) / 10)
            self.assertEqual(cache["labels"][0], "unknown")
            self.assertEqual(cache["labels"][3], "fall")
            self.assertTrue(cache["window_ready"][2])
            metadata = json.loads(str(cache["metadata_json"]))
            self.assertEqual(metadata["model_sha256"], "test-model")
            buffer = PoseBuffer(**settings)
            frame = np.zeros((40, 40, 3), np.uint8)
            for index in range(12):
                observation = FramePacket("cam0", "clip1", index, index / 10, "", frame)
                buffer.add(observation, estimator.estimate(frame))
                features, mask = normalize_window(buffer.window(1))
                np.testing.assert_allclose(cache["features"][index], features[-1])
                np.testing.assert_array_equal(cache["validity"][index], mask[-1])
        before = estimator.calls
        self.assertEqual(extract_clip(self.record, estimator, settings, output=output,
                                     model_hash="test-model", intervals=intervals), "skipped")
        self.assertEqual(estimator.calls, before)
        self.assertEqual(extract_clip(self.record, estimator, settings, output=output,
                                     model_hash="changed-model", intervals=intervals), "written")
        self.assertEqual(estimator.calls, before + 12)
        # Edited annotations/source must also invalidate a cache.
        self.assertEqual(extract_clip(self.record, estimator, settings, output=output,
                                     model_hash="changed-model"), "written")
        cv2.imwrite(str(self.images / "frame0.png"), np.full((40, 40, 3), 42, np.uint8))
        self.assertEqual(extract_clip(self.record, estimator, settings, output=output,
                                     model_hash="changed-model"), "written")

    def test_empty_room_preserves_ticks_and_resets_on_failure(self):
        estimator = FakeEstimator()
        estimator.estimate = lambda image: []
        output = self.root / "empty.npz"
        extract_clip(self.record, estimator, {}, output=output, model_hash="test")
        with np.load(output, allow_pickle=False) as cache:
            self.assertEqual(len(cache["timestamps"]), 12)
            self.assertTrue((cache["track_ids"] == -1).all())
            self.assertFalse(cache["validity"].any())
        def fail(image):
            raise RuntimeError("inference failed")
        estimator.estimate = fail
        with self.assertRaises(RuntimeError):
            extract_clip(self.record, estimator, {}, output=self.root / "failure.npz", model_hash="test")
        self.assertEqual(estimator.resets, 4)
        self.assertFalse((self.root / "failure.npz").exists())


if __name__ == "__main__":
    unittest.main()
