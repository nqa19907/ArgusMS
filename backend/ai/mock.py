import time
from backend.contracts import DetectionUpdate, FallCandidate, FramePacket


class MockDetector:
    def __init__(self, trigger_fall: bool = False) -> None:
        self.trigger_fall = trigger_fall
        self.model_id = "mock-detector-v1"

    def process(self, packet: FramePacket) -> DetectionUpdate:
        t0 = time.perf_counter()
        if self.trigger_fall:
            candidate = FallCandidate(
                track_id=1,
                score=0.88,
                score_kind="rule_score",
                valid_pose=True,
                onset_observed=True,
                low_posture=True,
                reasons=("rapid_descent", "low_posture_sustained"),
            )
            candidates = (candidate,)
        else:
            candidates = (
                FallCandidate(
                    track_id=1,
                    score=0.12,
                    score_kind="rule_score",
                    valid_pose=True,
                    onset_observed=False,
                    low_posture=False,
                    reasons=(),
                ),
            )
        dt_ms = (time.perf_counter() - t0) * 1000.0
        return DetectionUpdate(
            camera_id=packet.camera_id,
            stream_session_id=packet.stream_session_id,
            frame_id=packet.frame_id,
            candidates=candidates,
            inference_ms=round(dt_ms, 2),
            model_id=self.model_id,
            warmup_remaining_samples=0,
            ai_state="READY",
        )

    def reset(self, stream_session_id: str) -> None:
        pass

    def close(self) -> None:
        pass