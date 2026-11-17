from pathlib import Path
from backend.ai.mock import MockDetector
from backend.config import AISettings
from backend.contracts import DetectionUpdate, FallDetector, FramePacket


class ErrorDetector:
    """Detector an toàn khi thiếu weights hoặc lỗi nạp pretrained model lúc startup."""
    def __init__(self, reason: str) -> None:
        self.model_id = "error-unavailable"
        self.reason = reason

    def process(self, packet: FramePacket) -> DetectionUpdate:
        return DetectionUpdate(
            camera_id=packet.camera_id,
            stream_session_id=packet.stream_session_id,
            frame_id=packet.frame_id,
            candidates=(),
            inference_ms=0.0,
            model_id=self.model_id,
            warmup_remaining_samples=0,
            ai_state="ERROR",
        )

    def reset(self, stream_session_id: str) -> None:
        pass

    def close(self) -> None:
        pass


def create_detector(ai_settings: AISettings) -> FallDetector:
    if ai_settings.mode == "mock":
        return MockDetector(trigger_fall=False)

    weights_path = Path(ai_settings.pose_weights)
    if not weights_path.exists():
        return ErrorDetector(reason=f"Missing pose weights at {weights_path}")

    try:
        from backend.ai.pretrained import PretrainedDetector
        return PretrainedDetector(ai_settings)
    except Exception as exc:
        return ErrorDetector(reason=f"Failed to load PretrainedDetector: {exc}")