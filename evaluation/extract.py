"""Extract resumable, timestamped COCO17 caches from manifest clips.

Run: python -m evaluation.extract --manifest data/manifests/clips.csv
One PoseEstimator is loaded for the entire run, reset between recordings.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import re
from collections.abc import Iterable, Iterator, Mapping

import cv2
import numpy as np

from backend.ai.buffer import PoseBuffer, PoseWindow
from backend.ai.factory import create_pose_estimator, load_settings
from backend.contracts import FramePacket
from evaluation.manifest import project_path, read_manifest, validate_groups


def natural_key(path: Path) -> list:
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r"(\d+)", path.name)]


class FrameSource:
    def __init__(self, source: str | Path | int, *, fps: float | None = None,
                 timestamps_path: Path | None = None):
        self.source = source
        self._capture = None
        self._files = None
        self._timestamps = None
        self.live = isinstance(source, int) or str(source).lower().startswith(("rtsp://", "http://", "https://"))
        if timestamps_path is not None:
            with timestamps_path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            values = [float(row["time_s"]) for row in rows]
            ids = [int(row["frame_id"]) for row in rows]
            if not values or ids != list(range(len(rows))):
                raise ValueError("timestamp frame_id must be contiguous, zero-based")
            if any(not math.isfinite(value) or value < 0 for value in values):
                raise ValueError("timestamps must be nonnegative and finite")
            if any(b <= a for a, b in zip(values, values[1:])):
                raise ValueError("timestamps must strictly increase")
            self._timestamps = values
        path = Path(str(source))
        if not self.live and path.is_dir():
            self._files = sorted((p for p in path.iterdir()
                                  if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}), key=natural_key)
            if not self._files:
                raise ValueError(f"No image frames in {path}")
            if self._timestamps is not None and len(self._files) != len(self._timestamps):
                raise ValueError("image/timestamp counts differ")
        else:
            if not self.live and not path.is_file():
                raise FileNotFoundError(path)
            self._capture = cv2.VideoCapture(source if self.live else str(path))
            if not self._capture.isOpened():
                self.close()
                raise OSError("Unable to open frame source")
            if fps is None:
                fps = self._capture.get(cv2.CAP_PROP_FPS)
        self.fps = fps
        if not self.live and self._timestamps is None and (fps is None or not math.isfinite(fps) or fps <= 0):
            self.close()
            raise ValueError("Verified positive FPS or timestamps CSV is required")

    def __iter__(self) -> Iterator[tuple[int, float, np.ndarray]]:
        from time import monotonic

        index = 0
        while True:
            if self._files is not None:
                if index >= len(self._files):
                    break
                image = cv2.imread(str(self._files[index]))
                if image is None:
                    raise OSError(f"Unreadable image: {self._files[index]}")
            else:
                ok, image = self._capture.read()
                if not ok:
                    if self.live:
                        raise OSError("Live source stopped delivering frames")
                    break
            if self._timestamps is not None:
                if index >= len(self._timestamps):
                    raise ValueError("video has more frames than timestamp rows")
                timestamp = self._timestamps[index]
            else:
                timestamp = monotonic() if self.live else index / self.fps
            yield index, timestamp, image
            index += 1
        if index == 0:
            raise ValueError("Source contained no decodable frames")
        if self._timestamps is not None and index != len(self._timestamps):
            raise ValueError("video/timestamp counts differ")

    def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def __enter__(self) -> FrameSource:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


FEATURE_VERSION = 1
INPUT_DIM = 54


def normalize_window(window: PoseWindow) -> tuple[np.ndarray, np.ndarray]:
    """Return [T,54] float32 features and [T,54] boolean validity mask."""
    features = np.zeros((len(window.samples), INPUT_DIM), dtype=np.float32)
    mask = np.zeros(features.shape, dtype=bool)
    valid = [sample for sample in window.samples if sample.valid]
    if not valid:
        return features, mask
    hips = valid[0].pose.keypoints[[11, 12], :2].mean(axis=0)
    lengths = [np.linalg.norm(sample.pose.keypoints[[5, 6], :2].mean(axis=0)
                              - sample.pose.keypoints[[11, 12], :2].mean(axis=0))
               for sample in valid]
    scale = float(np.median(lengths))
    if not np.isfinite(scale) or scale < 1e-6:
        return features, mask
    for row, sample in enumerate(window.samples):
        pose = sample.pose
        if pose is None:
            continue
        usable = pose.valid_keypoints & np.isfinite(pose.keypoints).all(axis=1)
        usable &= pose.keypoints[:, 2] > 0
        points = features[row, :51].reshape(17, 3)
        points[usable, :2] = (pose.keypoints[usable, :2] - hips) / scale
        points[usable, 2] = pose.keypoints[usable, 2]
        mask[row, :51] = np.repeat(usable, 3)
        if sample.valid:
            shoulder = pose.keypoints[[5, 6], :2].mean(axis=0)
            hip = pose.keypoints[[11, 12], :2].mean(axis=0)
            vector = shoulder - hip
            features[row, 51] = hip[1] / sample.image_height
            mask[row, 51] = True
            if np.linalg.norm(vector) > 1e-6:
                features[row, 52] = np.arctan2(abs(vector[0]), abs(vector[1])) / (np.pi / 2)
                mask[row, 52] = True
        x1, y1, x2, y2 = pose.bbox_xyxy
        if np.isfinite(pose.bbox_xyxy).all() and x2 > x1 and y2 > y1:
            features[row, 53] = min(float((x2 - x1) / (y2 - y1)), 4.0) / 4
            mask[row, 53] = True
    return features, mask


BUFFER_KEYS = ("sample_hz", "window_samples", "max_pose_gap_seconds", "min_valid_window_fraction")
LABELS = {"fall", "adl", "hard_negative", "lying", "occlusion"}


def read_intervals(path: str | Path, clip_ids: set[str]) -> list[dict]:
    with project_path(path).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    result = []
    for row in rows:
        if row["clip_id"] not in clip_ids:
            raise ValueError(f"Label references unknown clip: {row['clip_id']}")
        if row["label"] not in LABELS:
            raise ValueError(f"Unknown label: {row['label']}")
        start, end = float(row["onset_s"]), float(row["end_s"])
        impact = float(row["impact_s"]) if row.get("impact_s") else None
        if not (math.isfinite(start) and math.isfinite(end) and 0 <= start < end):
            raise ValueError("Intervals require finite 0 <= onset_s < end_s")
        if row["label"] == "fall" and (impact is None or not math.isfinite(impact) or not start <= impact <= end):
            raise ValueError("fall requires onset_s <= impact_s <= end_s")
        item = {"clip_id": row["clip_id"], "onset_s": start, "impact_s": impact,
                "end_s": end, "label": row["label"]}
        if any(other["clip_id"] == item["clip_id"]
               and max(other["onset_s"], start) < min(other["end_s"], end) for other in result):
            raise ValueError("Overlapping annotation intervals are ambiguous")
        result.append(item)
    return result


def label_at(timestamp: float, intervals: Iterable[Mapping]) -> str:
    for interval in intervals:
        if float(interval["onset_s"]) <= timestamp < float(interval["end_s"]):
            return str(interval["label"])
    return "unknown"


def artifact_hash(path: str | Path) -> str:
    """Hash actual source/model content, including filenames in image sequences."""
    path = project_path(path)
    files = sorted(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else [path]
    digest = hashlib.sha256()
    for item in files:
        if path.is_dir():
            name = item.relative_to(path).as_posix().encode()
            digest.update(len(name).to_bytes(8, "big"))
            digest.update(name)
            digest.update(item.stat().st_size.to_bytes(8, "big"))
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def save_features(path: str | Path, arrays: Mapping[str, np.ndarray], metadata: Mapping) -> None:
    """Atomic write: interruption must not leave a completed-looking cache."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(suffix=".npz", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            np.savez_compressed(stream, **arrays, metadata_json=np.array(json.dumps(dict(metadata), sort_keys=True)))
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _cache_matches(path: Path, cache_key: str) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path, allow_pickle=False) as cache:
            metadata = json.loads(str(cache["metadata_json"]))
            count = len(cache["timestamps"])
            return (metadata["cache_key"] == cache_key and count > 0
                    and cache["features"].shape == cache["validity"].shape == (count, INPUT_DIM)
                    and cache["keypoints"].shape == (count, 17, 3)
                    and all(len(cache[key]) == count for key in (
                        "labels", "frame_ids", "track_ids", "segment_ids", "window_ready",
                        "valid_keypoints", "bboxes", "image_heights", "window_start")))
    except (OSError, ValueError, KeyError, EOFError):
        return False


def extract_clip(record: Mapping, estimator, settings: Mapping, *, output: Path,
                 model_hash: str, intervals: Iterable[Mapping] = (), resume: bool = True) -> str:
    """Save causal rolling features and raw poses; return written or skipped.

    Each row is one sampled timestamp/track. Multiple tracks can share a time;
    track_id=-1 represents an empty sampled frame. Segment changes forbid
    joining pose history across gaps. Unknown annotations remain unknown.
    """
    source_path = project_path(record["path"])
    intervals = [dict(row) for row in intervals if row["clip_id"] == record["clip_id"]]
    metadata = {"schema_version": 1, "feature_version": FEATURE_VERSION,
                "input_dim": INPUT_DIM, "pose_schema": "COCO17",
                "clip": dict(record), "settings": dict(settings),
                "source_sha256": artifact_hash(source_path), "model_sha256": model_hash,
                "intervals": intervals, "feature_layout": "causal_window_last_row"}
    timestamps_path = project_path(record["timestamps_path"]) if record.get("timestamps_path") else None
    metadata["timestamps_sha256"] = artifact_hash(timestamps_path) if timestamps_path else None
    cache_key = hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest()
    metadata["cache_key"] = cache_key
    output = Path(output)
    if resume and _cache_matches(output, cache_key):
        return "skipped"

    buffer = PoseBuffer(**{key: settings[key] for key in BUFFER_KEYS if key in settings})
    rows: list[dict] = []
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    estimator.reset()
    try:
        with FrameSource(source_path, fps=float(record["fps"]) if record.get("fps") else None,
                         timestamps_path=timestamps_path) as source:
            for frame_id, timestamp, image in source:
                packet = FramePacket(str(record["camera_id"]), str(record["clip_id"]), frame_id,
                                     timestamp, (epoch + timedelta(seconds=timestamp)).isoformat(), image)
                poses = estimator.estimate(image)
                if not buffer.add(packet, poses):
                    continue
                # Include empty frames so missing detections do not disappear from time.
                tracks = buffer.track_ids or (-1,)
                for track in tracks:
                    window = buffer.window(track)
                    pose = window.samples[-1].pose if window else None
                    features, validity = normalize_window(window) if window else (
                        np.zeros((1, INPUT_DIM), np.float32), np.zeros((1, INPUT_DIM), bool))
                    rows.append({
                        "timestamps": timestamp, "frame_ids": frame_id, "track_ids": track,
                        "segment_ids": window.segment_id if window else 0,
                        "features": features[-1], "validity": validity[-1],
                        "labels": label_at(timestamp, intervals),
                        "window_ready": window.ready if window else False,
                        "window_start": window.samples[0].timestamp if window else timestamp,
                        "keypoints": pose.keypoints if pose else np.full((17, 3), np.nan, np.float32),
                        "valid_keypoints": pose.valid_keypoints if pose else np.zeros(17, bool),
                        "bboxes": pose.bbox_xyxy if pose else np.full(4, np.nan, np.float32),
                        "image_heights": image.shape[0],
                    })
    finally:
        estimator.reset()
    if not rows:
        raise ValueError(f"No samples extracted from {record['clip_id']}")
    dtypes = {"timestamps": np.float64, "frame_ids": np.int64, "track_ids": np.int64,
              "segment_ids": np.int64, "features": np.float32, "validity": bool,
              "labels": "U32", "window_ready": bool, "window_start": np.float64,
              "keypoints": np.float32, "valid_keypoints": bool, "bboxes": np.float32,
              "image_heights": np.int32}
    arrays = {key: np.asarray([row[key] for row in rows], dtype=dtype) for key, dtype in dtypes.items()}
    save_features(output, arrays, metadata)
    return "written"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="data/manifests/clips.csv")
    parser.add_argument("--labels", default="data/labels/intervals.csv")
    parser.add_argument("--splits", default="data/splits.json")
    parser.add_argument("--config", default="configs/ai.yaml")
    parser.add_argument("--output-dir", default="data/features")
    parser.add_argument("--clip-id", action="append", help="Repeat to select clips")
    parser.add_argument("--overwrite", action="store_true", help="Re-extract even a matching cache")
    args = parser.parse_args()
    records = read_manifest(args.manifest)
    if not records:
        parser.error("Manifest has no verified clips; see README.md")
    with project_path(args.splits).open(encoding="utf-8") as stream:
        validate_groups(records, json.load(stream))
    intervals = read_intervals(args.labels, {row["clip_id"] for row in records})
    if args.clip_id:
        unknown = set(args.clip_id) - {row["clip_id"] for row in records}
        if unknown:
            parser.error(f"Unknown clip IDs: {sorted(unknown)}")
        records = [row for row in records if row["clip_id"] in args.clip_id]
    settings = load_settings(args.config)
    model_hash = artifact_hash(settings.get("pose_weights", "models/yolo11n-pose.pt"))
    with create_pose_estimator(settings) as estimator:
        for record in records:
            output = project_path(args.output_dir) / f"{record['clip_id']}.npz"
            state = extract_clip(record, estimator, settings, output=output, model_hash=model_hash,
                                 intervals=intervals, resume=not args.overwrite)
            print(f"{record['clip_id']}: {state}")


if __name__ == "__main__":
    main()
