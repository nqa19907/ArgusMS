"""Week-1 construction boundary. A pose preview is not a fall detector."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from backend.ai.interface import FallDetector
from backend.ai.mock import MockDetector
from backend.ai.pose import PROJECT_ROOT, PoseEstimator


def load_settings(path: str | Path = "configs/ai.yaml") -> dict[str, Any]:
    path = Path(path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    with path.open(encoding="utf-8") as stream:
        settings = yaml.safe_load(stream)
    if not isinstance(settings, dict):
        raise ValueError("AI configuration must be a YAML mapping")
    if settings.get("pose_schema", "COCO17") != "COCO17":
        raise ValueError("Only pose_schema=COCO17 is supported")
    return settings


def create_pose_estimator(settings: Mapping[str, Any]) -> PoseEstimator:
    return PoseEstimator(**{key: settings[key] for key in (
        "pose_weights", "device", "image_size", "tracker", "keypoint_confidence"
    ) if key in settings})


def create_detector(settings: Mapping[str, Any]) -> FallDetector:
    """Create once at startup. Week 1 provides mock; scorer arrives in week 2.

    Fail explicitly for pretrained rather than silently substituting test
    output or presenting skeleton tracking as completed fall recognition.
    """
    mode = settings.get("mode", "pretrained")
    if mode == "mock":
        return MockDetector()
    if mode == "pretrained":
        raise NotImplementedError(
            "Pretrained fall scoring/state machine belongs to week 2. "
            "Use scripts/ai_smoke.py --mode pose for real pose estimation, "
            "or mode=mock for development integration."
        )
    raise ValueError(f"Unsupported detector mode: {mode!r}; expected mock or pretrained")
