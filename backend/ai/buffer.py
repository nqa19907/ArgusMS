"""Bounded, timestamp-sampled COCO17 history for one stream session."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
import math

import numpy as np

from backend.ai.pose import TrackedPose
from backend.contracts import FramePacket


TORSO_JOINTS = [5, 6, 11, 12]


@dataclass(frozen=True)
class PoseSample:
    frame_id: int
    timestamp: float
    image_height: int
    pose: TrackedPose | None

    @property
    def valid(self) -> bool:
        if self.pose is None:
            return False
        points = self.pose.keypoints[TORSO_JOINTS]
        return bool(self.pose.valid_keypoints[TORSO_JOINTS].all()
                    and np.isfinite(points).all()
                    and (points[:, 2] > 0).all())


@dataclass(frozen=True)
class PoseWindow:
    camera_id: str
    stream_session_id: str
    track_id: int
    segment_id: int
    samples: tuple[PoseSample, ...]
    expected_samples: int
    min_valid_fraction: float

    @property
    def valid_fraction(self) -> float:
        return sum(sample.valid for sample in self.samples) / self.expected_samples

    @property
    def ready(self) -> bool:
        return len(self.samples) == self.expected_samples and self.valid_fraction >= self.min_valid_fraction


class PoseBuffer:
    """Sample new packets at most sample_hz; never repeat/interpolate frames.

    Missing tracks get explicit invalid samples for short gaps. Long gaps in
    valid torso observations start a new segment. Unassigned IDs are ignored.
    Arrays are copied so callers cannot mutate accumulated history.
    """

    def __init__(self, *, sample_hz: float = 10, window_samples: int = 30,
                 max_pose_gap_seconds: float = 0.3, min_valid_window_fraction: float = 0.8):
        if not math.isfinite(sample_hz) or sample_hz <= 0:
            raise ValueError("sample_hz must be positive and finite")
        if isinstance(window_samples, bool) or not isinstance(window_samples, int) or window_samples < 1:
            raise ValueError("window_samples must be a positive integer")
        if not math.isfinite(max_pose_gap_seconds) or max_pose_gap_seconds <= 0:
            raise ValueError("max_pose_gap_seconds must be positive and finite")
        if not 0 < min_valid_window_fraction <= 1:
            raise ValueError("min_valid_window_fraction must be in (0, 1]")
        self.sample_hz = sample_hz
        self.window_samples = window_samples
        self.max_pose_gap_seconds = max_pose_gap_seconds
        self.min_valid_window_fraction = min_valid_window_fraction
        self.reset()

    def reset(self) -> None:
        self._session: tuple[str, str] | None = None
        self._last_frame = -1
        self._last_time: float | None = None
        self._next_tick: float | None = None
        self._tracks: dict[int, deque[PoseSample]] = {}
        self._last_valid: dict[int, float] = {}
        self._segments: dict[int, int] = {}
        self._serial = 0

    def add(self, packet: FramePacket, poses: Iterable[TrackedPose]) -> bool:
        """Return True when this packet was sampled, including empty frames."""
        now = packet.captured_mono
        if not math.isfinite(now):
            raise ValueError("captured_mono must be finite")
        session = (packet.camera_id, packet.stream_session_id)
        if self._session != session:
            self.reset()
            self._session = session
        if packet.frame_id <= self._last_frame:
            return False
        if self._last_time is not None and now <= self._last_time:
            raise ValueError("timestamps must increase within a session")
        self._last_frame, self._last_time = packet.frame_id, now
        if self._next_tick is not None and now + 1e-9 < self._next_tick:
            return False
        if self._next_tick is None:
            self._next_tick = now
        steps = max(1, math.floor((now - self._next_tick + 1e-9) * self.sample_hz) + 1)
        self._next_tick += steps / self.sample_hz

        current = {pose.track_id: pose for pose in poses if pose.track_id is not None}
        for track in set(self._tracks) | set(current):
            previous_valid = self._last_valid.get(track)
            if previous_valid is not None and now - previous_valid > self.max_pose_gap_seconds + 1e-9:
                self._tracks.pop(track, None)
                self._last_valid.pop(track, None)
                self._segments.pop(track, None)
            pose = current.get(track)
            if track not in self._tracks:
                if pose is None:
                    continue
                self._serial += 1
                self._segments[track] = self._serial
                self._tracks[track] = deque(maxlen=self.window_samples)
                self._last_valid[track] = now
            if pose is not None:
                pose = TrackedPose(pose.track_id, pose.bbox_xyxy.copy(), pose.confidence,
                                   pose.keypoints.copy(), pose.valid_keypoints.copy())
            sample = PoseSample(packet.frame_id, now, packet.image_bgr.shape[0], pose)
            history = self._tracks[track]
            # A slow source must not turn 30 sparse observations into a 3 s
            # window. Keep real timestamps, without padding missing ticks.
            horizon = self.window_samples / self.sample_hz
            while history and history[0].timestamp < now - horizon - 1e-9:
                history.popleft()
            history.append(sample)
            if sample.valid:
                self._last_valid[track] = now
        return True

    def window(self, track_id: int) -> PoseWindow | None:
        if track_id not in self._tracks or self._session is None:
            return None
        return PoseWindow(*self._session, track_id, self._segments[track_id],
                          tuple(self._tracks[track_id]), self.window_samples,
                          self.min_valid_window_fraction)

    @property
    def track_ids(self) -> tuple[int, ...]:
        return tuple(sorted(self._tracks))
