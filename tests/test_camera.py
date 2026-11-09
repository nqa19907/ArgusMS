import time
import numpy as np
from backend.camera.reader import CameraReader


class FakeCapture:
    def __init__(self, fail_after: int = 2) -> None:
        self.count = 0
        self.fail_after = fail_after
        self.opened = True

    def isOpened(self) -> bool:
        return self.opened

    def read(self):
        self.count += 1
        if self.count > self.fail_after:
            return False, None
        frame = np.zeros((120, 160, 3), dtype=np.uint8)
        return True, frame

    def release(self) -> None:
        self.opened = False


def test_read_failure_triggers_new_session():
    sessions: list[str] = []
    reader = CameraReader(
        camera_id="cam_test",
        reconnect_seconds=[0.05, 0.05],
        capture_factory=lambda _url: FakeCapture(fail_after=2),
        on_session_reset=lambda sid: sessions.append(sid),
    )
    reader.start("rtsp://127.0.0.1:8554/fake")
    time.sleep(0.25)
    reader.stop()

    assert len(sessions) >= 2
    assert sessions[0] != sessions[1]
    assert reader.get_status()["state"] == "STOPPED"