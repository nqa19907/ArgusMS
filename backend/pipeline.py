from collections import deque
import threading
import time
from typing import Callable
import cv2
from backend.ai.factory import create_detector
from backend.ai.state_machine import FallStateMachine
from backend.alerts.events import EventService
from backend.camera.latest import LatestValue
from backend.camera.reader import CameraReader
from backend.config import AISettings, AppSettings


class Pipeline:
    def __init__(
        self,
        app_settings: AppSettings,
        ai_settings: AISettings,
        reader: CameraReader,
        event_service: EventService,
        on_status_broadcast: Callable[[dict], None] | None = None,
    ) -> None:
        self.app_settings = app_settings
        self.ai_settings = ai_settings
        self.reader = reader
        self.event_service = event_service
        self._on_status_broadcast = on_status_broadcast

        self.latest_jpeg = LatestValue[bytes]()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

        self._detector = create_detector(ai_settings)
        self._state_machine = FallStateMachine(
            confirmation_seconds=ai_settings.confirmation_seconds,
            recovery_seconds=ai_settings.recovery_seconds,
            cooldown_seconds=ai_settings.cooldown_seconds,
            max_pose_gap_seconds=ai_settings.max_pose_gap_seconds,
        )
        self.reader._on_session_reset = self.reset_session

        self._ai_state: str = "READY"
        self._model_id: str = getattr(self._detector, "model_id", f"{ai_settings.mode}-v1")
        self._last_inference_ms: float = 0.0
        self._warmup_remaining: int = 0
        self._fps_timestamps: deque[float] = deque(maxlen=30)
        self._last_jpeg_mono: float = 0.0

    def start(self, initial_source: str = "") -> None:
        self._stop_event.clear()
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._infer_loop, name="InferenceThread", daemon=True)
            self._thread.start()
        source = initial_source or self.app_settings.rtsp_url
        if source:
            self.reader.start(source)

    def stop(self) -> None:
        self._stop_event.set()
        self.reader.stop()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=3.0)
        self._thread = None
        self.latest_jpeg.clear()
        self._detector.close()

    def switch_camera(self, new_url: str, camera_label: str = "") -> None:
        self.reset_session()
        self.reader.start(new_url)

    def stop_camera(self) -> None:
        self.reader.stop()
        self.reset_session()
        self.latest_jpeg.clear()

    def reset_session(self, stream_session_id: str = "") -> None:
        with self._lock:
            self._detector.reset(stream_session_id)
            self._state_machine.reset(stream_session_id or None)
            self._fps_timestamps.clear()

    def get_ai_status(self) -> dict:
        with self._lock:
            now = time.monotonic()
            while self._fps_timestamps and (now - self._fps_timestamps[0]) > 5.0:
                self._fps_timestamps.popleft()
            if len(self._fps_timestamps) >= 2:
                span = max(now - self._fps_timestamps[0], 1e-3)
                fps = round(len(self._fps_timestamps) / span, 1)
            else:
                fps = 0.0

            return {
                "state": self._ai_state,
                "mode": self.ai_settings.mode,
                "model_id": self._model_id,
                "processed_fps": fps,
                "last_inference_ms": round(self._last_inference_ms, 1),
                "warmup_remaining_samples": self._warmup_remaining,
            }

    def _infer_loop(self) -> None:
        last_seq = 0
        min_jpeg_interval = 1.0 / max(self.app_settings.preview_fps, 0.5)

        while not self._stop_event.is_set():
            packet, seq = self.reader.latest_frame.wait_newer(last_seq, timeout=0.3)
            if packet is None:
                continue
            last_seq = seq

            now_mono = time.monotonic()
            if (now_mono - self._last_jpeg_mono) >= min_jpeg_interval:
                ok, buf = cv2.imencode(".jpg", packet.image_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                if ok:
                    self.latest_jpeg.replace(buf.tobytes())
                    self._last_jpeg_mono = now_mono

            try:
                update = self._detector.process(packet)
                with self._lock:
                    self._fps_timestamps.append(time.monotonic())
                    self._last_inference_ms = update.inference_ms
                    self._model_id = update.model_id
                    self._warmup_remaining = update.warmup_remaining_samples
                    self._ai_state = update.ai_state

                for cand in update.candidates:
                    transition = self._state_machine.update(
                        camera_id=packet.camera_id,
                        stream_session_id=packet.stream_session_id,
                        candidate=cand,
                        captured_mono=packet.captured_mono,
                        model_id=update.model_id,
                    )
                    if transition.just_confirmed:
                        self.event_service.create_once(transition)
            except Exception:
                with self._lock:
                    self._ai_state = "ERROR"