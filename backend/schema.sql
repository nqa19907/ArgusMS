CREATE TABLE IF NOT EXISTS installation (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    id TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    schema_version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS pairing_codes (
    code_hash TEXT PRIMARY KEY,
    expires_at TEXT NOT NULL,
    consumed_at TEXT
);

CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    secret_hash TEXT NOT NULL UNIQUE,
    client_label TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    push_kind TEXT,
    push_value TEXT,
    sound_enabled INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS camera_config (
    camera_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    protected_url TEXT NOT NULL,
    label TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    cursor INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    episode_id TEXT NOT NULL UNIQUE,
    payload_json TEXT NOT NULL,
    is_test INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    ack_at TEXT
);

CREATE TABLE IF NOT EXISTS outbox (
    event_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('pending', 'accepted', 'failed', 'expired')),
    attempts INTEGER NOT NULL DEFAULT 0,
    next_attempt_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    last_error TEXT,
    PRIMARY KEY (event_id, device_id)
);