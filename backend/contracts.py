from dataclasses import dataclass, field
from typing import Literal, Protocol
import numpy as np


@dataclass(frozen=True)
class FramePacket:
    camera_id: str
    stream_session_id: str
    frame_id: int
    captured_mono: float
    captured_at_utc: str
    image_bgr: np.ndarray


@dataclass(frozen=True)
class FallCandidate:
    track_id: int
    score: float
    score_kind: Literal["rule_score", "uncalibrated_model_score"]
    valid_pose: bool
    onset_observed: bool
    low_posture: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DetectionUpdate:
    camera_id: str
    stream_session_id: str
    frame_id: int
    candidates: tuple[FallCandidate, ...]
    inference_ms: float
    model_id: str
    warmup_remaining_samples: int = 0
    ai_state: Literal["LOADING", "WARMUP", "READY", "DEGRADED", "ERROR"] = "READY"


@dataclass(frozen=True)
class StateTransition:
    state: Literal["WARMUP", "NORMAL", "SUSPECTED", "CONFIRMED", "LATCHED", "RECOVERY", "UNKNOWN"]
    just_confirmed: bool
    episode_id: str
    camera_id: str
    stream_session_id: str
    track_id: int
    occurred_at_utc: str
    confirmed_at_utc: str
    score: float
    score_kind: Literal["rule_score", "uncalibrated_model_score"]
    model_id: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class FallEventRecord:
    cursor: int
    event_id: str
    episode_id: str
    installation_id: str
    camera_id: str
    stream_session_id: str
    track_id: int
    occurred_at: str
    confirmed_at: str
    score: float
    score_kind: str
    model_id: str
    message: str
    reasons: list[str]
    is_test: bool
    ack_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "schema_version": 1,
            "type": "fall.confirmed",
            "event_id": self.event_id,
            "episode_id": self.episode_id,
            "installation_id": self.installation_id,
            "camera_id": self.camera_id,
            "stream_session_id": self.stream_session_id,
            "track_id": self.track_id,
            "occurred_at": self.occurred_at,
            "confirmed_at": self.confirmed_at,
            "score": round(self.score, 4),
            "score_kind": self.score_kind,
            "model_id": self.model_id,
            "message": self.message,
            "reasons": list(self.reasons),
            "is_test": self.is_test,
        }


class FallDetector(Protocol):
    def process(self, packet: FramePacket) -> DetectionUpdate: ...
    def reset(self, stream_session_id: str) -> None: ...
    def close(self) -> None: ...