from dataclasses import dataclass
from datetime import timedelta
import os
from typing import Literal
import firebase_admin
from firebase_admin import credentials, messaging


@dataclass(frozen=True)
class FcmSendResult:
    outcome: Literal["accepted", "unregistered", "transient_error", "unavailable"]
    provider_message_id: str | None = None
    error_message: str | None = None


class FcmSender:
    def __init__(self, credential_path: str = "") -> None:
        self.credential_path = credential_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        self._configured = False
        self._last_send_state: str = "idle"
        self._init_sdk()

    def _init_sdk(self) -> None:
        if firebase_admin._apps:
            self._configured = True
            return
        if not self.credential_path or not os.path.exists(self.credential_path):
            self._configured = False
            self._last_send_state = "unavailable"
            return
        try:
            cred = credentials.Certificate(self.credential_path)
            firebase_admin.initialize_app(cred)
            self._configured = True
        except Exception:
            self._configured = False
            self._last_send_state = "unavailable"

    @property
    def is_configured(self) -> bool:
        return self._configured

    @property
    def last_send_state(self) -> str:
        return self._last_send_state

    def send_fall(self, push_token: str, sound_enabled: bool, event_payload: dict) -> FcmSendResult:
        if not self._configured:
            self._last_send_state = "unavailable"
            return FcmSendResult(outcome="unavailable", error_message="Firebase credentials not configured")

        is_test = bool(event_payload.get("is_test", False))
        title = "Thông báo thử FallGuard" if is_test else "Cảnh báo giám sát"
        body = (
            "Đây là thông báo thử kết nối từ hệ thống."
            if is_test
            else "Có sự kiện nghi ngã cần kiểm tra. Mở ứng dụng để xem."
        )
        channel_id = "fall_alerts_v1" if sound_enabled else "fall_silent_v1"

        msg = messaging.Message(
            token=push_token,
            notification=messaging.Notification(title=title, body=body),
            data={
                "event_id": str(event_payload["event_id"]),
                "installation_id": str(event_payload["installation_id"]),
                "camera_id": str(event_payload["camera_id"]),
                "schema_version": str(event_payload.get("schema_version", 1)),
                "type": str(event_payload.get("type", "fall.confirmed")),
                "confirmed_at": str(event_payload["confirmed_at"]),
                "is_test": str(is_test).lower(),
            },
            android=messaging.AndroidConfig(
                priority="high",
                ttl=timedelta(seconds=60),
                notification=messaging.AndroidNotification(
                    channel_id=channel_id,
                    tag=str(event_payload["event_id"]),
                ),
            ),
        )

        try:
            msg_id = messaging.send(msg)
            self._last_send_state = "accepted"
            return FcmSendResult(outcome="accepted", provider_message_id=msg_id)
        except Exception as exc:
            err_text = str(exc)
            if "UNREGISTERED" in err_text.upper() or "NOT_FOUND" in err_text.upper():
                self._last_send_state = "unregistered"
                return FcmSendResult(outcome="unregistered", error_message=err_text)
            self._last_send_state = "transient_error"
            return FcmSendResult(outcome="transient_error", error_message=err_text)

    def send_test(self, push_token: str, sound_enabled: bool, installation_id: str, camera_id: str, event_id: str, confirmed_at: str) -> FcmSendResult:
        payload = {
            "schema_version": 1,
            "type": "fall.confirmed",
            "event_id": event_id,
            "installation_id": installation_id,
            "camera_id": camera_id,
            "confirmed_at": confirmed_at,
            "is_test": True,
        }
        return self.send_fall(push_token, sound_enabled, payload)