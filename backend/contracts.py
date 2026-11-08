"""Shared data contracts from docs/plan.md, sections 3.1 and 3.2.

FramePacket stays inside the backend. Only network DTOs are serialized for
clients; images and pose arrays must never be included in notifications.
Detector protocols belong in backend/ai/interface.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from numpy.typing import NDArray


SCHEMA_VERSION = 1
ScoreKind = Literal["rule_score", "uncalibrated_model_score"]


@dataclass(frozen=True)
class FramePacket:
    """One received frame, with identity scoped to a stream session.

    captured_mono is the backend's monotonic receive time in seconds, not
    the camera's exposure time. captured_at_utc is an ISO-8601 UTC string.
    frame_id increases within a session; reconnects must change session ID.
    image_bgr is uint8 H×W×3. Frozen fields do not freeze the NumPy buffer:
    producers and consumers must treat the shared image as read-only.
    """

    camera_id: str
    stream_session_id: str
    frame_id: int
    captured_mono: float
    captured_at_utc: str
    image_bgr: NDArray[np.uint8] = field(repr=False, compare=False)


@dataclass(frozen=True)
class FallCandidate:
    """Per-track evidence, before temporal confirmation.

    Only an assigned track ID may produce a candidate. Missing joints can
    produce valid_pose=False; this is distinct from no detections at all.
    score is a rule/model score, not a calibrated probability of a fall.
    """

    track_id: int
    score: float
    score_kind: ScoreKind
    valid_pose: bool
    onset_observed: bool
    low_posture: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class DetectionUpdate:
    """Evidence for one processed frame; candidates=() means no candidates.

    Identity fields are copied from FramePacket. inference_ms measures this
    processing call; model_id identifies the actual model/rules in use.
    This update alone does not authorize a confirmed fall notification.
    """

    camera_id: str
    stream_session_id: str
    frame_id: int
    candidates: tuple[FallCandidate, ...]
    inference_ms: float
    model_id: str


@dataclass(frozen=True)
class FallEventDTO:
    """Confirmed-event network payload shared by REST and WebSocket.

    occurred_at is the observed onset time; confirmed_at is the time enough
    evidence was accumulated, both ISO-8601 UTC strings. The event service
    assigns and persists event_id once per episode and reuses it on retries.
    A push adapter must encode this DTO as required by its transport.
    """

    event_id: str
    episode_id: str
    installation_id: str
    camera_id: str
    stream_session_id: str
    track_id: int
    occurred_at: str
    confirmed_at: str
    score: float
    score_kind: ScoreKind
    model_id: str
    message: str
    reasons: tuple[str, ...]
    is_test: bool = False
    schema_version: Literal[1] = field(default=SCHEMA_VERSION, init=False)
    type: Literal["fall.confirmed"] = field(default="fall.confirmed", init=False)

    def to_dict(self) -> dict[str, object]:
        """Return the version-1 JSON payload without internal image/pose data."""
        return {
            "schema_version": self.schema_version,
            "type": self.type,
            "event_id": self.event_id,
            "episode_id": self.episode_id,
            "installation_id": self.installation_id,
            "camera_id": self.camera_id,
            "stream_session_id": self.stream_session_id,
            "track_id": self.track_id,
            "occurred_at": self.occurred_at,
            "confirmed_at": self.confirmed_at,
            "score": self.score,
            "score_kind": self.score_kind,
            "model_id": self.model_id,
            "message": self.message,
            "reasons": list(self.reasons),
            "is_test": self.is_test,
        }
