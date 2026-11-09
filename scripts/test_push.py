import argparse
import uuid
from backend.alerts.fcm import FcmSender
from backend.config import load_settings
from backend.storage import Storage, utc_now_iso


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test gửi thông báo FCM tới thiết bị đã ghép")
    parser.add_argument("--device-id", required=True, help="Mã device_id trong SQLite")
    args = parser.parse_args()

    app_settings, _ = load_settings()
    storage = Storage(app_settings.sqlite_path)
    sender = FcmSender(app_settings.google_application_credentials)

    with storage._connect() as conn:
        row = conn.execute(
            "SELECT device_id, push_value, sound_enabled, active FROM devices WHERE device_id = ?",
            (args.device_id,),
        ).fetchone()

    if row is None or not bool(row["active"]) or not row["push_value"]:
        raise SystemExit(f"Thiết bị {args.device_id} không tồn tại, đã bị thu hồi hoặc chưa đăng ký FCM token.")

    res = sender.send_test(
        push_token=str(row["push_value"]),
        sound_enabled=bool(row["sound_enabled"]),
        installation_id=storage.get_installation_id(),
        camera_id=app_settings.camera_id,
        event_id=f"evt-smoke-{uuid.uuid4().hex[:8]}",
        confirmed_at=utc_now_iso(),
    )
    print(f"Outcome: {res.outcome} | Message ID: {res.provider_message_id} | Error: {res.error_message}")


if __name__ == "__main__":
    main()