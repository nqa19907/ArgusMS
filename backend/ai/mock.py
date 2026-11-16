"""Deterministic development fixtures. Every update is explicitly is_test."""

from __future__ import annotations

from collections.abc import Sequence

from backend.contracts import DetectionUpdate, FallCandidate, FramePacket


DEFAULT_FIXTURES = (
    (),
    (FallCandidate(1, 0.0, "rule_score", True, False, False, ("mock:upright",)),),
    (FallCandidate(1, 0.0, "rule_score", False, False, False, ("mock:missing_joints",)),),
)


class MockDetector:
    """Advance one fixture per new frame, cycling until reset.

    Reprocessing the latest frame returns exactly the same update. A new camera
    or session starts at fixture zero. No FallEventDTO is generated here.
    """

    def __init__(self, fixtures: Sequence[tuple[FallCandidate, ...]] = DEFAULT_FIXTURES):
        if not fixtures:
            raise ValueError("fixtures must contain at least one frame")
        self._fixtures = tuple(tuple(row) for row in fixtures)
        self._closed = False
        self.reset()

    def process(self, packet: FramePacket) -> DetectionUpdate:
        if self._closed:
            raise RuntimeError("MockDetector is closed")
        session = (packet.camera_id, packet.stream_session_id)
        if session != self._session:
            self.reset()
            self._session = session
        if self._last is not None:
            if packet.frame_id == self._last.frame_id:
                return self._last
            if packet.frame_id < self._last.frame_id:
                raise ValueError("frame_id must increase within a session")
        update = DetectionUpdate(
            packet.camera_id, packet.stream_session_id, packet.frame_id,
            self._fixtures[self._index % len(self._fixtures)], 0.0,
            "mock-week1-v1", is_test=True,
        )
        self._index += 1
        self._last = update
        return update

    def reset(self) -> None:
        self._index = 0
        self._session = None
        self._last: DetectionUpdate | None = None

    def close(self) -> None:
        self.reset()
        self._closed = True
