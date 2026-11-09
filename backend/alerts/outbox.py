from datetime import datetime, timedelta, timezone
import json
import threading
from backend.alerts.fcm import FcmSender
from backend.storage import Storage, parse_utc

RETRY_DELAYS_SECONDS = (5, 15, 30)


class OutboxWorker:
    def __init__(self, storage: Storage, sender: FcmSender, poll_interval: float = 1.0) -> None:
        self.storage = storage
        self.sender = sender
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._wake_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, name="OutboxWorkerThread", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._wake_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=3.0)
        self._thread = None

    def wake(self) -> None:
        self._wake_event.set()

    def run_due_once(self) -> int:
        jobs = self.storage.fetch_due_outbox_jobs()
        processed = 0
        for job in jobs:
            processed += 1
            event_id = str(job["event_id"])
            device_id = str(job["device_id"])
            attempts = int(job["attempts"]) + 1
            expires_at = parse_utc(str(job["expires_at"]))

            if not bool(job["active"]) or not job["push_value"]:
                self.storage.mark_outbox_result(
                    event_id, device_id, "expired", attempts, error_msg="DEVICE_INACTIVE_OR_NO_TOKEN"
                )
                continue

            payload = json.loads(job["payload_json"])
            res = self.sender.send_fall(
                push_token=str(job["push_value"]),
                sound_enabled=bool(job["sound_enabled"]),
                event_payload=payload,
            )

            if res.outcome == "accepted":
                self.storage.mark_outbox_result(event_id, device_id, "accepted", attempts)
            elif res.outcome == "unregistered":
                self.storage.invalidate_device_push(device_id)
                self.storage.mark_outbox_result(
                    event_id, device_id, "failed", attempts, error_msg="UNREGISTERED_TOKEN"
                )
            elif res.outcome == "unavailable":
                self.storage.mark_outbox_result(
                    event_id, device_id, "failed", attempts, error_msg=res.error_message
                )
            else:
                if attempts >= len(RETRY_DELAYS_SECONDS):
                    self.storage.mark_outbox_result(
                        event_id, device_id, "failed", attempts, error_msg=res.error_message
                    )
                else:
                    delay_s = RETRY_DELAYS_SECONDS[attempts - 1]
                    next_time = datetime.now(timezone.utc) + timedelta(seconds=delay_s)
                    if next_time >= expires_at:
                        self.storage.mark_outbox_result(
                            event_id, device_id, "expired", attempts, error_msg="RETRY_EXCEEDS_TTL"
                        )
                    else:
                        next_iso = next_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                        self.storage.mark_outbox_result(
                            event_id,
                            device_id,
                            "pending",
                            attempts,
                            next_attempt_at=next_iso,
                            error_msg=res.error_message,
                        )
        return processed

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.run_due_once()
            except Exception:
                pass
            self._wake_event.wait(timeout=self.poll_interval)
            self._wake_event.clear()