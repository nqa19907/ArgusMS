from fastapi.testclient import TestClient
from backend.config import AISettings, AppSettings
from backend.main import create_app


def _make_test_client(tmp_path):
    app_cfg = AppSettings(sqlite_path=str(tmp_path / "test.db"), rtsp_url="")
    ai_cfg = AISettings(mode="mock")
    app = create_app(app_settings=app_cfg, ai_settings=ai_cfg)
    return TestClient(app), app


def test_claim_once_and_reject_reuse(tmp_path):
    client, app = _make_test_client(tmp_path)
    code, _, inst_id = app.state.storage.create_pairing_code(ttl_seconds=120)

    r1 = client.post(
        "/api/v1/pairing/claim",
        json={"pairing_code": code, "expected_installation_id": inst_id, "client_label": "Phone 1"},
    )
    assert r1.status_code == 201
    secret = r1.json()["device_secret"]

    r2 = client.post(
        "/api/v1/pairing/claim",
        json={"pairing_code": code, "expected_installation_id": inst_id, "client_label": "Phone 2"},
    )
    assert r2.status_code == 409

    status_ok = client.get("/api/v1/status", headers={"Authorization": f"Bearer {secret}"})
    assert status_ok.status_code == 200


def test_expired_and_revoked_device(tmp_path):
    client, app = _make_test_client(tmp_path)
    expired_code, _, inst_id = app.state.storage.create_pairing_code(ttl_seconds=-5)

    r_exp = client.post(
        "/api/v1/pairing/claim",
        json={"pairing_code": expired_code, "expected_installation_id": inst_id},
    )
    assert r_exp.status_code == 410

    valid_code, _, _ = app.state.storage.create_pairing_code(ttl_seconds=120)
    claim = client.post(
        "/api/v1/pairing/claim",
        json={"pairing_code": valid_code, "expected_installation_id": inst_id},
    ).json()

    app.state.storage.revoke_device(claim["device_id"])
    r_revoked = client.get("/api/v1/status", headers={"Authorization": f"Bearer {claim['device_secret']}"})
    assert r_revoked.status_code == 401