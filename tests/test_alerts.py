from backend.alerts.events import EventService
from backend.alerts.fcm import FcmSendResult
from backend.alerts.outbox import OutboxWorker
from backend.contracts import StateTransition
from backend.storage import Storage, utc_now_iso


class FakeFcmSender:
    def __init__(self, outcome: str = "accepted") -> None:
        self.outcome = outcome
        self.calls = 0

    def send_fall(self, push_token: str, sound_enabled: bool, event_payload: dict) -> FcmSendResult:
        self.calls += 1
        return FcmSendResult(outcome=self.outcome, provider_message_id="msg-123")  # type: ignore[arg-type]


def test_same_episode_created_once_and_accepted_not_retried(tmp_path):
    storage = Storage(str(tmp_path / "alerts.db"))
    code, _, inst_id = storage.create_pairing_code(120)
    claim = storage.claim_pairing_code(code, inst_id, "Test Phone")
    storage.update_device_push(claim["device_id"], "fcm", "token-xyz-12345", True)

    fake_sender = FakeFcmSender(outcome="accepted")
    worker = OutboxWorker(storage=storage, sender=fake_sender)  # type: ignore[arg-type]
    service = EventService(storage=storage)

    now = utc_now_iso()
    tr = StateTransition(
        state="CONFIRMED",
        just_confirmed=True,
        episode_id="ep-sess1-track1-001",
        camera_id="living_room",
        stream_session_id="sess1",
        track_id=1,
        occurred_at_utc=now,
        confirmed_at_utc=now,
        score=0.91,
        score_kind="rule_score",
        model_id="pose-rules-v1",
        reasons=("rapid_descent", "low_posture_sustained"),
    )

    rec1, created1 = service.create_once(tr)
    rec2, created2 = service.create_once(tr)

    assert created1 is True
    assert created2 is False
    assert rec1.event_id == rec2.event_id

    worker.run_due_once()
    worker.run_due_once()
    assert fake_sender.calls == 1