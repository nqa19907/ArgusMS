from backend.ai.mock import MockDetector
from backend.config import AISettings
from backend.contracts import FallDetector


def create_detector(ai_settings: AISettings) -> FallDetector:
    if ai_settings.mode == "mock":
        return MockDetector(trigger_fall=False)

    if ai_settings.mode == "trained":
        try:
            from backend.ai.trained import TrainedDetector  # Do SV1 bàn giao ở Tuần 2
            return TrainedDetector(ai_settings)
        except Exception:
            pass

    try:
        from backend.ai.pretrained import PretrainedDetector  # Do SV1 bàn giao ở Tuần 2
        return PretrainedDetector(ai_settings)
    except Exception:
        return MockDetector(trigger_fall=False)