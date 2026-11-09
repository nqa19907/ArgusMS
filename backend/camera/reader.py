import os
import threading
import time
from typing import Callable, Literal
from urllib.parse import urlparse
import uuid
import cv2
from backend.camera.latest import LatestValue
from backend.contracts import FramePacket
from backend.storage import utc_now_iso

CameraState = Literal["STOPPED", "CONNECTING", "CONNECTED", "RECONNECTING", "ERROR"]


def validate_rtsp_url(url: str) -> str:
    cleaned = url.strip()
    parsed = urlparse(cleaned)
    if parsed.scheme.lower() not in ("rtsp", "rtsps") or not parsed.hostname:
        raise ValueError("URL phải có scheme rtsp:// hoặc rtsps:// và có hostname hợp lệ")
    return cleaned


class CameraReader:
    def __init__(
        self,
        camera_id: str,
        open_timeout_ms: int = 5000,
        read_timeout_ms: int = 3000,
        reconnect_seconds: list[float] | None = None,
        stale_frame_seconds: float = 3.0,
        rtsp_transport: str = "tcp",
        capture_factory: Callable[[str], cv2.VideoCapture] | None = None,
        on_session_reset: Callable[[str], None] | None = None,
    ) -> None:
        self.camera_id = camera_id
        self.open_timeout_ms = open_timeout_ms
        self.read_timeout_ms = read_timeout_ms
        self.reconnect_seconds = reconnect_seconds or [1.0, 2.0, 4.0, 8.0, 15.0]
        self.stale_frame_seconds = stale_frame_seconds
        self.rtsp_transport = rtsp_transport
        self._capture_factory = capture_factory
        self._on_session_reset = on_session_reset

        self.latest_frame = LatestValue[FramePacket]()
        self._lock = threading.Lock()
        self._switch_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

        self._source_url: str = ""
        self._state: CameraState = "STOPPED"
        self._reconnect_attempts: int = 0
        self._last_frame_mono: float | None = None
        self._stream_session_id: str = f"sess-{uuid.uuid4().hex[:8]}"
        self._frame_id: int = 0

    def start(self, source_url: str) -> None:
        with self._switch_lock:
            self.stop()
            self._source_url = source_url.strip()
            if not self._source_url:
                with self._lock:
                    self._state = "STOPPED"
                return
            self._stop_event.clear()
            with self._lock:
                self._state = "CONNECTING"
                self._reconnect_attempts = 0
                self._last_frame_mono = None
            self._thread = threading.Thread(target=self._capture_loop, name="CameraReaderThread", daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=(self.read_timeout_ms / 1000.0) + 2.0)
        self._thread = None
        self.latest_frame.clear()
        with self._lock:
            self._state = "STOPPED"
            self._last_frame_mono = None
            self._reconnect_attempts = 0

    def get_status(self) -> dict:
        with self._lock:
            state = self._state
            last_mono = self._last_frame_mono
            attempts = self._reconnect_attempts

        age_ms: int | None = None
        if last_mono is not None:
            elapsed = time.monotonic() - last_mono
            age_ms = int(elapsed * 1000)
            if state == "CONNECTED" and elapsed > self.stale_frame_seconds:
                state = "RECONNECTING"

        return {
            "id": self.camera_id,
            "state": state,
            "last_frame_age_ms": age_ms,
            "reconnect_attempts": attempts,
        }

    def _open_capture(self, source_url: str) -> cv2.VideoCapture:
        if self._capture_factory is not None:
            return self._capture_factory(source_url)

        if source_url.lower().startswith(("rtsp://", "rtsps://")):
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = f"rtsp_transport;{self.rtsp_transport}"
            params = [
                cv2.CAP_PROP_OPEN_TIMEOUT_MSEC,
                int(self.open_timeout_ms),
                cv2.CAP_PROP_READ_TIMEOUT_MSEC,
                int(self.read_timeout_ms),
                cv2.CAP_PROP_BUFFERSIZE,
                1,
            ]
            return cv2.VideoCapture(source_url, cv2.CAP_FFMPEG, params)

        if source_url.isdigit():
            return cv2.VideoCapture(int(source_url))
        return cv2.VideoCapture(source_url)

    def _new_session(self) -> str:
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        with self._lock:
            self._stream_session_id = session_id
            self._frame_id = 0
        if self._on_session_reset is not None:
            self._on_session_reset(session_id)
        return session_id

    def _capture_loop(self) -> None:
        cap: cv2.VideoCapture | None = None
        session_id = self._new_session()

        while not self._stop_event.is_set():
            if cap is None or not cap.isOpened():
                with self._lock:
                    self._state = "CONNECTING" if self._reconnect_attempts == 0 else "RECONNECTING"
                try:
                    cap = self._open_capture(self._source_url)
                except Exception:
                    cap = None

                if cap is None or not cap.isOpened():
                    if cap is not None:
                        cap.release()
                        cap = None
                    self._wait_backoff()
                    session_id = self._new_session()
                    continue

                with self._lock:
                    self._state = "CONNECTED"
                    self._reconnect_attempts = 0

            ok, frame = cap.read()
            if not ok or frame is None or frame.size == 0:
                cap.release()
                cap = None
                self.latest_frame.clear()
                self._wait_backoff()
                session_id = self._new_session()
                continue

            now_mono = time.monotonic()
            now_utc = utc_now_iso()
            with self._lock:
                self._frame_id += 1
                fid = self._frame_id
                self._last_frame_mono = now_mono
                self._state = "CONNECTED"

            packet = FramePacket(
                camera_id=self.camera_id,
                stream_session_id=session_id,
                frame_id=fid,
                captured_mono=now_mono,
                captured_at_utc=now_utc,
                image_bgr=frame,
            )
            self.latest_frame.replace(packet)

        if cap is not None:
            cap.release()

    def _wait_backoff(self) -> None:
        with self._lock:
            idx = min(self._reconnect_attempts, len(self.reconnect_seconds) - 1)
            delay = self.reconnect_seconds[idx]
            self._reconnect_attempts += 1
            self._state = "RECONNECTING" if self._reconnect_attempts <= len(self.reconnect_seconds) else "ERROR"
        self._stop_event.wait(timeout=delay)