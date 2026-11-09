from typing import Protocol
from backend.contracts import DetectionUpdate, FallCandidate, FramePacket


class SequenceScorer(Protocol):
    def score_track(self, track_id: int, window_features: object) -> FallCandidate: ...


__all__ = ["DetectionUpdate", "FallCandidate", "FramePacket", "SequenceScorer"]