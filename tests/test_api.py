from fastapi.testclient import TestClient
from backend.config import AISettings, AppSettings
from backend.main import create_app


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