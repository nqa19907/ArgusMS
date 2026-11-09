import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.alerts.events import EventService
from backend.alerts.fcm import FcmSender
from backend.alerts.outbox import OutboxWorker
from backend.api.routes import api_router
from backend.api.stream import stream_router
from backend.api.ws import ConnectionHub, ws_router
from backend.camera.reader import CameraReader
from backend.config import AISettings, AppSettings, load_settings
from backend.pipeline import Pipeline
from backend.storage import Storage


def create_app(
    app_settings: AppSettings | None = None,
    ai_settings: AISettings | None = None,
    capture_factory=None,
    fcm_sender: FcmSender | None = None,
) -> FastAPI:
    if app_settings is None or ai_settings is None:
        loaded_app, loaded_ai = load_settings()
        app_settings = app_settings or loaded_app
        ai_settings = ai_settings or loaded_ai

    storage = Storage(app_settings.sqlite_path)
    ws_hub = ConnectionHub()
    sender = fcm_sender or FcmSender(app_settings.google_application_credentials)
    outbox_worker = OutboxWorker(storage=storage, sender=sender)

    event_service = EventService(
        storage=storage,
        on_event_created=ws_hub.broadcast_from_thread,
        on_outbox_wake=outbox_worker.wake,
    )

    reader = CameraReader(
        camera_id=app_settings.camera_id,
        open_timeout_ms=app_settings.open_timeout_ms,
        read_timeout_ms=app_settings.read_timeout_ms,
        reconnect_seconds=app_settings.reconnect_seconds,
        stale_frame_seconds=app_settings.stale_frame_seconds,
        rtsp_transport=app_settings.rtsp_transport,
        capture_factory=capture_factory,
    )

    pipeline = Pipeline(
        app_settings=app_settings,
        ai_settings=ai_settings,
        reader=reader,
        event_service=event_service,
        on_status_broadcast=ws_hub.broadcast_from_thread,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        ws_hub.set_event_loop(asyncio.get_running_loop())
        outbox_worker.start()
        pipeline.start()
        yield
        pipeline.stop()
        outbox_worker.stop()

    app = FastAPI(title="FallGuard Backend", version="0.1.0", lifespan=lifespan)
    app.state.app_settings = app_settings
    app.state.ai_settings = ai_settings
    app.state.storage = storage
    app.state.ws_hub = ws_hub
    app.state.fcm_sender = sender
    app.state.outbox_worker = outbox_worker
    app.state.event_service = event_service
    app.state.pipeline = pipeline

    app.include_router(api_router)
    app.include_router(stream_router)
    app.include_router(ws_router)
    return app


app = create_app()