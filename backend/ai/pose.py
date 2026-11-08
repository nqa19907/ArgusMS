"""YOLO pose adapter for one sequential camera stream.

Coordinates are pixels in the original BGR image, in COCO-17 order.
Call reset() on reconnect or camera changes; track IDs are session-local.
Use one instance from one inference worker (the adapter is not thread-safe).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
COCO17_NAMES = (
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
)


@dataclass(frozen=True)
class TrackedPose:
    """One detection; only keypoints with valid_keypoints=True are usable.

    keypoints is float32 (17, 3): x, y, confidence. Invalid coordinates
    are NaN, with confidence retained for diagnostics. A missing track ID
    must not be used to accumulate fall evidence.
    """

    track_id: int | None
    bbox_xyxy: np.ndarray
    confidence: float
    keypoints: np.ndarray
    valid_keypoints: np.ndarray


class PoseEstimator:
    """Load local pose weights once; infer boxes, joints and ByteTrack IDs.

    Defaults correspond to configs/ai.yaml. Pass its pose_weights, device,
    image_size and tracker fields as keyword arguments when wiring config.
    Supports a .pt file or an exported OpenVINO model directory.
    """

    def __init__(
        self,
        pose_weights: str | Path = "models/yolo11n-pose.pt",
        *,
        device: str = "cpu",
        image_size: int = 480,
        tracker: str = "bytetrack.yaml",
        keypoint_confidence: float = 0.5,
    ) -> None:
        if isinstance(image_size, bool) or not isinstance(image_size, int) or image_size <= 0:
            raise ValueError("image_size must be a positive integer")
        if not 0 <= keypoint_confidence <= 1:
            raise ValueError("keypoint_confidence must be between 0 and 1")
        weights = Path(pose_weights).expanduser()
        if not weights.is_absolute():
            weights = PROJECT_ROOT / weights
        if not weights.exists():
            raise FileNotFoundError(f"Pose weights not found: {weights}")
        from ultralytics import YOLO

        self._model = YOLO(str(weights), task="pose")
        self.device = device
        self.image_size = image_size
        self.tracker = tracker
        self.keypoint_confidence = keypoint_confidence

    def estimate(self, image_bgr: np.ndarray) -> list[TrackedPose]:
        """Estimate one uint8 H×W×3 frame; return [] when nobody is detected.

        Missing joints remain invalid; missing IDs remain None. Runtime/model
        errors propagate to the caller rather than becoming an empty detection.
        """
        if self._model is None:
            raise RuntimeError("PoseEstimator is closed")
        if (
            not isinstance(image_bgr, np.ndarray)
            or image_bgr.dtype != np.uint8
            or image_bgr.ndim != 3
            or image_bgr.shape[2] != 3
            or min(image_bgr.shape[:2]) == 0
        ):
            raise ValueError("image_bgr must be a nonempty uint8 H×W×3 array")
        results = self._model.track(
            image_bgr,
            persist=True,
            tracker=self.tracker,
            device=self.device,
            imgsz=self.image_size,
            classes=[0],
            verbose=False,
        )
        if not results:
            return []
        result = results[0]
        if result.boxes is None or len(result.boxes) == 0:
            return []
        boxes = result.boxes.cpu().numpy()
        joints = None
        if result.keypoints is not None:
            joints = result.keypoints.cpu().numpy().data

        poses = []
        for index, bbox in enumerate(boxes.xyxy):
            keypoints = np.full((17, 3), np.nan, dtype=np.float32)
            keypoints[:, 2] = 0
            if joints is not None and index < len(joints):
                row = joints[index]
                if row.shape == (17, 3):
                    keypoints[:] = row
            valid = (
                np.isfinite(keypoints).all(axis=1)
                & (keypoints[:, 2] >= self.keypoint_confidence)
                & (keypoints[:, 2] > 0)
                & np.any(keypoints[:, :2] != 0, axis=1)
            )
            keypoints[~valid, :2] = np.nan
            track_id = None
            if boxes.id is not None:
                value = float(boxes.id[index])
                if np.isfinite(value) and value >= 0 and value.is_integer():
                    track_id = int(value)
            poses.append(TrackedPose(
                track_id=track_id,
                bbox_xyxy=np.array(bbox, dtype=np.float32, copy=True),
                confidence=float(boxes.conf[index]),
                keypoints=keypoints,
                valid_keypoints=valid,
            ))
        return poses

    def reset(self) -> None:
        """Clear tracking history without reloading weights (also safe before inference)."""
        if self._model is None:
            return
        predictor = getattr(self._model, "predictor", None)
        for tracker in getattr(predictor, "trackers", ()):
            tracker.reset()
        if predictor is not None and hasattr(predictor, "vid_path"):
            predictor.vid_path = [None] * len(predictor.vid_path)

    def close(self) -> None:
        """Release this adapter's model reference; repeated calls are safe."""
        self.reset()
        self._model = None

    def __enter__(self) -> PoseEstimator:
        if self._model is None:
            raise RuntimeError("PoseEstimator is closed")
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
