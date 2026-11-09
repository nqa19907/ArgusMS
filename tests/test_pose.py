import unittest
from types import SimpleNamespace
from unittest.mock import Mock
import numpy as np
from backend.ai.pose import PoseEstimator

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

if __name__ == '__main__': unittest.main()
