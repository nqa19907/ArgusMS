from typing import Callable
import uuid
from backend.contracts import FallEventRecord, StateTransition
from backend.storage import Storage, utc_now_iso


class EventService:
    def __init__(
        self,
        storage: Storage,
        on_event_created: Callable[[dict], None] | None = None,
        on_outbox_wake: Callable[[], None] | None = None,
    ) -> None:
        self.storage = storage
        self._on_event_created = on_event_created
        self._on_outbox_wake = on_outbox_wake

    def create_once(self, transition: StateTransition) -> tuple[FallEventRecord, bool]:
        event_id = f"evt-{uuid.uuid4()}"
        installation_id = self.storage.get_installation_id()
        payload = {
            "schema_version": 1,
            "type": "fall.confirmed",
            "event_id": event_id,
            "episode_id": transition.episode_id,
            "installation_id": installation_id,
            "camera_id": transition.camera_id,
            "stream_session_id": transition.stream_session_id,
            "track_id": transition.track_id,
            "occurred_at": transition.occurred_at_utc,
            "confirmed_at": transition.confirmed_at_utc,
            "score": round(transition.score, 4),
            "score_kind": transition.score_kind,
            "model_id": transition.model_id,
            "message": "Phát hiện diễn biến nghi ngã. Vui lòng kiểm tra người được theo dõi.",
            "reasons": list(transition.reasons),
            "is_test": False,
        }
        record, created = self.storage.save_event_and_enqueue_outbox(
            event_id=event_id,
            episode_id=transition.episode_id,
            payload=payload,
            is_test=False,
        )
        if created:
            if self._on_event_created is not None:
                self._on_event_created(record.to_dict())
            if self._on_outbox_wake is not None:
                self._on_outbox_wake()
        return record, created

    def create_test_event(self, camera_id: str, target_device_id: str) -> FallEventRecord:
        now_iso = utc_now_iso()
        event_id = f"evt-test-{uuid.uuid4()}"
        episode_id = f"ep-test-{uuid.uuid4().hex[:10]}"
        installation_id = self.storage.get_installation_id()
        payload = {
            "schema_version": 1,
            "type": "fall.confirmed",
            "event_id": event_id,
            "episode_id": episode_id,
            "installation_id": installation_id,
            "camera_id": camera_id,
            "stream_session_id": "test-session",
            "track_id": 0,
            "occurred_at": now_iso,
            "confirmed_at": now_iso,
            "score": 1.0,
            "score_kind": "rule_score",
            "model_id": "test-notification",
            "message": "Thông báo thử kết nối cảnh báo.",
            "reasons": ["manual_test"],
            "is_test": True,
        }
        record, _ = self.storage.save_event_and_enqueue_outbox(
            event_id=event_id,
            episode_id=episode_id,
            payload=payload,
            is_test=True,
            target_device_id=target_device_id,
        )
        if self._on_event_created is not None:
            self._on_event_created(record.to_dict())
        if self._on_outbox_wake is not None:
            self._on_outbox_wake()
        return record

    def acknowledge(self, event_id: str) -> bool:
        return self.storage.acknowledge_event(event_id)