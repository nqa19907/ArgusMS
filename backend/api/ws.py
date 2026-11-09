import asyncio
import threading
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.auth import verify_ws_device

ws_router = APIRouter()


class ConnectionHub:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._clients: set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        with self._lock:
            self._clients.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        with self._lock:
            self._clients.discard(ws)

    async def broadcast(self, message: dict) -> None:
        with self._lock:
            clients = list(self._clients)
        stale: list[WebSocket] = []
        for ws in clients:
            try:
                await ws.send_json(message)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(ws)

    def broadcast_from_thread(self, message: dict) -> None:
        if self._loop is None or self._loop.is_closed():
            return
        asyncio.run_coroutine_threadsafe(self.broadcast(message), self._loop)


@ws_router.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    ctx = verify_ws_device(websocket)
    if ctx is None:
        await websocket.close(code=1008)
        return

    hub: ConnectionHub = websocket.app.state.ws_hub
    await hub.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            if msg.strip().lower() == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        hub.disconnect(websocket)
    except Exception:
        hub.disconnect(websocket)