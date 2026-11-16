"""Contracts used by the pipeline without importing a model implementation."""

from __future__ import annotations

from typing import Protocol, TYPE_CHECKING, runtime_checkable

from backend.contracts import DetectionUpdate, FallCandidate, FramePacket

if TYPE_CHECKING:
    from backend.ai.buffer import PoseWindow


@runtime_checkable
class FallDetector(Protocol):
    """One sequential inference worker owns one detector instance.

    reset() is required on reconnect/switch. Errors propagate to the pipeline;
    an empty candidates tuple means no evidence, rather than an inference error.
    """

    def process(self, packet: FramePacket) -> DetectionUpdate: ...
    def reset(self) -> None: ...
    def close(self) -> None: ...


class SequenceScorer(Protocol):
    """Week-2 scorers consume timestamped history, never confirm events."""

    def score(self, window: PoseWindow) -> FallCandidate | None: ...
    def reset(self) -> None: ...
    def close(self) -> None: ...
