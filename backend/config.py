import os
from pathlib import Path
from typing import Literal
import yaml
from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    camera_id: str = "living_room"
    camera_source: Literal["rtsp", "video", "webcam"] = "rtsp"
    rtsp_url: str = ""
    rtsp_transport: Literal["tcp", "udp"] = "tcp"
    open_timeout_ms: int = Field(default=5000, ge=500, le=30000)
    read_timeout_ms: int = Field(default=3000, ge=500, le=30000)
    reconnect_seconds: list[float] = Field(default_factory=lambda: [1.0, 2.0, 4.0, 8.0, 15.0])
    stale_frame_seconds: float = Field(default=3.0, gt=0.5)
    capture_queue_size: int = Field(default=1, ge=1, le=2)
    preview_fps: float = Field(default=3.0, ge=0.5, le=15.0)
    sqlite_path: str = "runtime/fallguard.db"
    app_env: Literal["development", "production", "test"] = "development"
    google_application_credentials: str = ""


class AISettings(BaseModel):
    mode: Literal["mock", "pretrained", "trained"] = "mock"
    pose_weights: str = "models/yolo11n-pose.pt"
    trained_weights: str = "models/fall_tcn.pt"
    image_size: int = 480
    sample_hz: int = 10
    window_samples: int = 30
    max_pose_gap_seconds: float = 0.3
    min_valid_window_fraction: float = 0.8
    confirmation_seconds: float = 2.0
    recovery_seconds: float = 3.0
    cooldown_seconds: float = 60.0


def load_settings(
    app_yaml_path: str | None = None,
    ai_yaml_path: str | None = None,
) -> tuple[AppSettings, AISettings]:
    app_path = Path(app_yaml_path or os.getenv("APP_CONFIG_PATH", "configs/app.yaml"))
    ai_path = Path(ai_yaml_path or os.getenv("AI_CONFIG_PATH", "configs/ai.yaml"))

    app_data = yaml.safe_load(app_path.read_text(encoding="utf-8")) if app_path.exists() else {}
    ai_data = yaml.safe_load(ai_path.read_text(encoding="utf-8")) if ai_path.exists() else {}

    if os.getenv("APP_ENV"):
        app_data["app_env"] = os.getenv("APP_ENV")
    app_data["google_application_credentials"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

    return AppSettings(**(app_data or {})), AISettings(**(ai_data or {}))