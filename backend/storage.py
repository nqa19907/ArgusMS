from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
import threading
import uuid
from backend.contracts import FallEventRecord


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class Storage:
    def __init__(self, db_path: str, schema_path: str = "backend/schema.sql") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_db(schema_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self, schema_path: str) -> None:
        ddl = Path(schema_path).read_text(encoding="utf-8")
        with self._lock, self._connect() as conn:
            conn.executescript(ddl)
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT id FROM installation WHERE singleton_id = 1").fetchone()
            if row is None:
                inst_id = f"inst-{uuid.uuid4().hex[:12]}"
                conn.execute(
                    "INSERT INTO installation (singleton_id, id, created_at, schema_version) VALUES (1, ?, ?, 1)",
                    (inst_id, utc_now_iso()),
                )
            conn.execute("COMMIT")

    def get_installation_id(self) -> str:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT id FROM installation WHERE singleton_id = 1").fetchone()
            return str(row["id"])

    def create_pairing_code(self, ttl_seconds: int = 120) -> tuple[str, str, str]:
        raw_code = secrets.token_urlsafe(32)
        code_hash = sha256_hex(raw_code)
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")
        with self._lock, self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "INSERT INTO pairing_codes (code_hash, expires_at, consumed_at) VALUES (?, ?, NULL)",
                (code_hash, expires_at),
            )
            conn.execute("COMMIT")
        return raw_code, expires_at, self.get_installation_id()

    def claim_pairing_code(self, raw_code: str, expected_installation_id: str, client_label: str) -> dict:
        code_hash = sha256_hex(raw_code)
        now = datetime.now(timezone.utc)
        now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        with self._lock, self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                inst_row = conn.execute("SELECT id FROM installation WHERE singleton_id = 1").fetchone()
                inst_id = str(inst_row["id"])
                if expected_installation_id and expected_installation_id != inst_id:
                    conn.execute("ROLLBACK")
                    raise ValueError("INSTALLATION_MISMATCH")

                row = conn.execute(
                    "SELECT code_hash, expires_at, consumed_at FROM pairing_codes WHERE code_hash = ?",
                    (code_hash,),
                ).fetchone()
                if row is None:
                    conn.execute("ROLLBACK")
                    raise ValueError("INVALID_CODE")
                if row["consumed_at"] is not None:
                    conn.execute("ROLLBACK")
                    raise ValueError("ALREADY_CONSUMED")
                if now > parse_utc(row["expires_at"]):
                    conn.execute("ROLLBACK")
                    raise ValueError("EXPIRED_CODE")

                conn.execute(
                    "UPDATE pairing_codes SET consumed_at = ? WHERE code_hash = ?",
                    (now_iso, code_hash),
                )
                device_id = f"dev-{uuid.uuid4().hex[:12]}"
                device_secret = secrets.token_urlsafe(32)
                secret_hash = sha256_hex(device_secret)

                conn.execute(
                    """
                    INSERT INTO devices (device_id, secret_hash, client_label, active, sound_enabled, updated_at)
                    VALUES (?, ?, ?, 1, 1, ?)
                    """,
                    (device_id, secret_hash, client_label.strip() or "Android Device", now_iso),
                )
                conn.execute("COMMIT")
                return {
                    "schema_version": 1,
                    "device_id": device_id,
                    "device_secret": device_secret,
                    "installation_id": inst_id,
                }
            except Exception:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise

    def verify_device_secret(self, raw_secret: str) -> dict | None:
        secret_hash = sha256_hex(raw_secret)
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT device_id, client_label, active, push_kind, push_value, sound_enabled FROM devices WHERE secret_hash = ?",
                (secret_hash,),
            ).fetchone()
            if row is None or not bool(row["active"]):
                return None
            return dict(row)

    def revoke_device(self, device_id: str) -> bool:
        now_iso = utc_now_iso()
        with self._lock, self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            cur = conn.execute(
                "UPDATE devices SET active = 0, updated_at = ? WHERE device_id = ?",
                (now_iso, device_id),
            )
            conn.execute(
                "UPDATE outbox SET state = 'expired', last_error = 'DEVICE_REVOKED' WHERE device_id = ? AND state = 'pending'",
                (device_id,),
            )
            conn.execute("COMMIT")
            return cur.rowcount > 0

    def update_device_push(
        self, device_id: str, push_kind: str, push_value: str, sound_enabled: bool
    ) -> bool:
        now_iso = utc_now_iso()
        with self._lock, self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            cur = conn.execute(
                """
                UPDATE devices
                SET push_kind = ?, push_value = ?, sound_enabled = ?, updated_at = ?
                WHERE device_id = ? AND active = 1
                """,
                (push_kind, push_value, 1 if sound_enabled else 0, now_iso, device_id),
            )
            conn.execute("COMMIT")
            return cur.rowcount > 0

    def invalidate_device_push(self, device_id: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE devices SET push_value = NULL, updated_at = ? WHERE device_id = ?",
                (utc_now_iso(), device_id),
            )
            conn.execute("COMMIT")

    def has_configured_push_device(self) -> bool:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM devices WHERE active = 1 AND push_value IS NOT NULL AND push_value != '' LIMIT 1"
            ).fetchone()
            return row is not None

    def save_camera_config(self, camera_id: str, source: str, protected_url: str, label: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """
                INSERT INTO camera_config (camera_id, source, protected_url, label, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(camera_id) DO UPDATE SET
                    source = excluded.source,
                    protected_url = excluded.protected_url,
                    label = excluded.label,
                    updated_at = excluded.updated_at
                """,
                (camera_id, source, protected_url, label, utc_now_iso()),
            )
            conn.execute("COMMIT")

    def save_event_and_enqueue_outbox(
        self,
        event_id: str,
        episode_id: str,
        payload: dict,
        is_test: bool = False,
        target_device_id: str | None = None,
        ttl_seconds: int = 60,
    ) -> tuple[FallEventRecord, bool]:
        now = datetime.now(timezone.utc)
        now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        expires_iso = (now + timedelta(seconds=ttl_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")

        with self._lock, self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                existing = conn.execute(
                    "SELECT cursor, event_id, episode_id, payload_json, ack_at FROM events WHERE episode_id = ?",
                    (episode_id,),
                ).fetchone()
                if existing is not None:
                    conn.execute("COMMIT")
                    data = json.loads(existing["payload_json"])
                    return self._row_to_event_record(existing["cursor"], data, existing["ack_at"]), False

                payload_str = json.dumps(payload, ensure_ascii=False)
                cur = conn.execute(
                    """
                    INSERT INTO events (event_id, episode_id, payload_json, is_test, created_at, ack_at)
                    VALUES (?, ?, ?, ?, ?, NULL)
                    """,
                    (event_id, episode_id, payload_str, 1 if is_test else 0, now_iso),
                )
                cursor_id = int(cur.lastrowid)

                if target_device_id:
                    dev_rows = conn.execute(
                        "SELECT device_id FROM devices WHERE device_id = ? AND active = 1 AND push_value IS NOT NULL AND push_value != ''",
                        (target_device_id,),
                    ).fetchall()
                else:
                    dev_rows = conn.execute(
                        "SELECT device_id FROM devices WHERE active = 1 AND push_value IS NOT NULL AND push_value != ''"
                    ).fetchall()

                for dev in dev_rows:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO outbox (event_id, device_id, state, attempts, next_attempt_at, expires_at)
                        VALUES (?, ?, 'pending', 0, ?, ?)
                        """,
                        (event_id, str(dev["device_id"]), now_iso, expires_iso),
                    )

                # Giữ tối đa 100 sự kiện gần nhất theo thiết kế MVP
                conn.execute(
                    """
                    DELETE FROM events WHERE cursor NOT IN (
                        SELECT cursor FROM events ORDER BY cursor DESC LIMIT 100
                    )
                    """
                )
                conn.execute("COMMIT")
                return self._row_to_event_record(cursor_id, payload, None), True
            except Exception:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise

    def list_events(self, after_cursor: int = 0, limit: int = 50) -> tuple[list[dict], int]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT cursor, payload_json, ack_at
                FROM events
                WHERE cursor > ?
                ORDER BY cursor ASC
                LIMIT ?
                """,
                (after_cursor, limit),
            ).fetchall()
            items = []
            next_cursor = after_cursor
            for r in rows:
                next_cursor = int(r["cursor"])
                item = json.loads(r["payload_json"])
                item["cursor"] = next_cursor
                item["ack_at"] = r["ack_at"]
                items.append(item)
            return items, next_cursor

    def acknowledge_event(self, event_id: str) -> bool:
        now_iso = utc_now_iso()
        with self._lock, self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT event_id, ack_at FROM events WHERE event_id = ?", (event_id,)).fetchone()
            if row is None:
                conn.execute("ROLLBACK")
                return False
            if row["ack_at"] is None:
                conn.execute("UPDATE events SET ack_at = ? WHERE event_id = ?", (now_iso, event_id))
            conn.execute("COMMIT")
            return True

    def fetch_due_outbox_jobs(self) -> list[dict]:
        now_iso = utc_now_iso()
        with self._lock, self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE outbox SET state = 'expired', last_error = 'TTL_EXPIRED' WHERE state = 'pending' AND expires_at <= ?",
                (now_iso,),
            )
            rows = conn.execute(
                """
                SELECT o.event_id, o.device_id, o.attempts, o.expires_at,
                       d.active, d.push_kind, d.push_value, d.sound_enabled,
                       e.payload_json
                FROM outbox o
                JOIN devices d ON o.device_id = d.device_id
                JOIN events e ON o.event_id = e.event_id
                WHERE o.state = 'pending' AND o.next_attempt_at <= ? AND o.expires_at > ?
                """,
                (now_iso, now_iso),
            ).fetchall()
            conn.execute("COMMIT")
            return [dict(r) for r in rows]

    def mark_outbox_result(
        self,
        event_id: str,
        device_id: str,
        status: str,
        attempts: int,
        next_attempt_at: str | None = None,
        error_msg: str | None = None,
    ) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """
                UPDATE outbox
                SET state = ?, attempts = ?, next_attempt_at = COALESCE(?, next_attempt_at), last_error = ?
                WHERE event_id = ? AND device_id = ?
                """,
                (status, attempts, next_attempt_at, error_msg, event_id, device_id),
            )
            conn.execute("COMMIT")

    @staticmethod
    def _row_to_event_record(cursor_id: int, data: dict, ack_at: str | None) -> FallEventRecord:
        return FallEventRecord(
            cursor=cursor_id,
            event_id=data["event_id"],
            episode_id=data["episode_id"],
            installation_id=data["installation_id"],
            camera_id=data["camera_id"],
            stream_session_id=data["stream_session_id"],
            track_id=int(data["track_id"]),
            occurred_at=data["occurred_at"],
            confirmed_at=data["confirmed_at"],
            score=float(data["score"]),
            score_kind=data["score_kind"],
            model_id=data["model_id"],
            message=data["message"],
            reasons=list(data.get("reasons", [])),
            is_test=bool(data.get("is_test", False)),
            ack_at=ack_at,
        )