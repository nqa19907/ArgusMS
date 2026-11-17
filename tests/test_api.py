import time
import numpy as np
from fastapi.testclient import TestClient
from backend.config import AISettings, AppSettings
from backend.contracts import FramePacket
from backend.main import create_app

def _pair_device(client: TestClient, app) -> tuple[str, str]:
    code, _, inst_id = app.state.storage.create_pairing_code(120)
    res = client.post(
        "/api/v1/pairing/claim",
        json={"pairing_code": code, "expected_installation_id": inst_id, "client_label": "SV3 Phone"},
    )
    assert res.status_code == 201
    data = res.json()
    return data["device_id"], data["device_secret"]


def test_status_and_protected_preview_flow(tmp_path):
    app_cfg = AppSettings(sqlite_path=str(tmp_path / "api_w2.db"), rtsp_url="")
    ai_cfg = AISettings(mode="mock")
    app = create_app(app_settings=app_cfg, ai_settings=ai_cfg)

    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/api/v1/status").status_code == 401
        assert client.get("/api/v1/preview.jpg").status_code == 401
        assert client.get("/api/v1/stream.mjpeg").status_code == 401

        _, secret = _pair_device(client, app)
        headers = {"Authorization": f"Bearer {secret}"}

        # Khi chưa có frame, preview trả 503
        assert client.get("/api/v1/preview.jpg", headers=headers).status_code == 503

        # Giả lập CameraReader vừa nhận được 1 frame mới
        dummy_img = np.zeros((240, 320, 3), dtype=np.uint8)
        now_mono = time.monotonic()
        with app.state.pipeline.reader._lock:
            app.state.pipeline.reader._state = "CONNECTED"
            app.state.pipeline.reader._last_frame_mono = now_mono

        packet = FramePacket(
            camera_id="living_room",
            stream_session_id="sess-test1",
            frame_id=1,
            captured_mono=now_mono,
            captured_at_utc="2026-11-14T00:00:00Z",
            image_bgr=dummy_img,
        )
        app.state.pipeline.reader.latest_frame.replace(packet)
        time.sleep(0.4)

        preview_res = client.get("/api/v1/preview.jpg", headers=headers)
        assert preview_res.status_code == 200
        assert preview_res.headers["content-type"] == "image/jpeg"

        # Dừng camera -> preview phải lập tức quay về 503 và không lộ URL trong status
        stop_res = client.post("/api/v1/camera/stop", headers=headers)
        assert stop_res.status_code == 202
        assert client.get("/api/v1/preview.jpg", headers=headers).status_code == 503

        status_data = client.get("/api/v1/status", headers=headers).json()
        assert status_data["camera"]["state"] == "STOPPED"
        assert "rtsp://" not in str(status_data)


def test_camera_url_validation_and_ack(tmp_path):
    app_cfg = AppSettings(sqlite_path=str(tmp_path / "api_cam.db"), rtsp_url="")
    ai_cfg = AISettings(mode="mock")
    app = create_app(app_settings=app_cfg, ai_settings=ai_cfg)

    with TestClient(app) as client:
        _, secret = _pair_device(client, app)
        headers = {"Authorization": f"Bearer {secret}"}

        # Chặn scheme http hoặc đường dẫn file cục bộ
        assert client.put("/api/v1/camera", json={"rtsp_url": "http://192.168.1.1/video"}, headers=headers).status_code == 422
        assert client.put("/api/v1/camera", json={"rtsp_url": "file:///C:/video.mp4"}, headers=headers).status_code == 422

        # Tạo thông báo thử và kiểm tra ack lũy đẳng (idempotent)
        r_test = client.post("/api/v1/notifications/test", headers=headers)
        assert r_test.status_code == 202
        evt_id = r_test.json()["event_id"]

        assert client.post(f"/api/v1/events/{evt_id}/ack", headers=headers).status_code == 200
        assert client.post(f"/api/v1/events/{evt_id}/ack", headers=headers).status_code == 200
        assert client.post("/api/v1/events/evt-khong-ton-tai/ack", headers=headers).status_code == 404
        
def test_api_contracts_and_ack(tmp_path):
    app_cfg = AppSettings(sqlite_path=str(tmp_path / "api.db"), rtsp_url="")
    ai_cfg = AISettings(mode="mock")
    app = create_app(app_settings=app_cfg, ai_settings=ai_cfg)
    client = TestClient(app)

    assert client.get("/health").status_code == 200
    assert client.get("/api/v1/preview.jpg").status_code == 401

    code, _, inst_id = app.state.storage.create_pairing_code(120)
    claim = client.post(
        "/api/v1/pairing/claim",
        json={"pairing_code": code, "expected_installation_id": inst_id},
    ).json()
    headers = {"Authorization": f"Bearer {claim['device_secret']}"}

    r_bad_cam = client.put("/api/v1/camera", json={"rtsp_url": "http://invalid-scheme"}, headers=headers)
    assert r_bad_cam.status_code == 422

    r_test_notif = client.post("/api/v1/notifications/test", headers=headers)
    assert r_test_notif.status_code == 202
    evt_id = r_test_notif.json()["event_id"]

    r_ack1 = client.post(f"/api/v1/events/{evt_id}/ack", headers=headers)
    r_ack2 = client.post(f"/api/v1/events/{evt_id}/ack", headers=headers)
    assert r_ack1.status_code == 200
    assert r_ack2.status_code == 200