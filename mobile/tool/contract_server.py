"""Validation harness: real SV2 routes/auth/storage/WS; fake pipeline/sender only.
Not shipped as production backend. Runs on loopback and a temporary SQLite file.
"""

import asyncio
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace

import uvicorn
from fastapi import FastAPI

from backend.alerts.events import EventService
from backend.api.routes import api_router
from backend.api.ws import ConnectionHub, ws_router
from backend.pairing import build_pairing_uri
from backend.storage import Storage

base = Path(__file__).resolve().parents[2]
runtime = tempfile.TemporaryDirectory(prefix="argusms-contract-")
storage = Storage(
    str(Path(runtime.name) / "contract.db"), str(base / "backend/schema.sql")
)
hub = ConnectionHub()
events = EventService(storage, on_event_created=hub.broadcast_from_thread)
reader = SimpleNamespace(
    camera_id="living_room",
    get_status=lambda: {
        "id": "living_room",
        "state": "STOPPED",
        "last_frame_age_ms": None,
        "reconnect_attempts": 0,
    },
)
pipeline = SimpleNamespace(
    reader=reader,
    get_ai_status=lambda: {
        "state": "WARMUP",
        "mode": "mock",
        "model_id": "mock-v1",
        "processed_fps": 0,
        "last_inference_ms": 0,
        "warmup_remaining_samples": 30,
    },
)


@asynccontextmanager
async def lifespan(app):
    hub.set_event_loop(asyncio.get_running_loop())
    yield
    runtime.cleanup()


app = FastAPI(lifespan=lifespan)
app.state.storage = storage
app.state.pipeline = pipeline
app.state.fcm_sender = SimpleNamespace(
    is_configured=False, last_send_state="unavailable"
)
app.state.ws_hub = hub
app.state.event_service = events
app.include_router(api_router)
app.include_router(ws_router)


@app.get("/__test__/pair-link")
def test_pair_link():
    code, _expiry, inst = storage.create_pairing_code()
    return {"link": build_pairing_uri("http://127.0.0.1:18761", code, inst)}


if __name__ == "__main__":
    uvicorn.run(
        app, host="127.0.0.1", port=18761, log_level="warning", access_log=False
    )
