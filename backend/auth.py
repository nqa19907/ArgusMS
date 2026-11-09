from dataclasses import dataclass
from fastapi import Depends, HTTPException, Request, WebSocket, status


@dataclass(frozen=True)
class DeviceContext:
    device_id: str
    client_label: str
    installation_id: str
    sound_enabled: bool


def _extract_bearer_token(auth_header: str | None) -> str:
    if not auth_header:
        return ""
    parts = auth_header.strip().split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return ""
    return parts[1].strip()


def require_device(request: Request) -> DeviceContext:
    token = _extract_bearer_token(request.headers.get("Authorization"))
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer device_secret")

    storage = request.app.state.storage
    dev = storage.verify_device_secret(token)
    if dev is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or revoked device_secret")

    return DeviceContext(
        device_id=dev["device_id"],
        client_label=dev["client_label"],
        installation_id=storage.get_installation_id(),
        sound_enabled=bool(dev["sound_enabled"]),
    )


def verify_ws_device(websocket: WebSocket) -> DeviceContext | None:
    token = _extract_bearer_token(websocket.headers.get("Authorization"))
    if not token:
        return None
    storage = websocket.app.state.storage
    dev = storage.verify_device_secret(token)
    if dev is None:
        return None
    return DeviceContext(
        device_id=dev["device_id"],
        client_label=dev["client_label"],
        installation_id=storage.get_installation_id(),
        sound_enabled=bool(dev["sound_enabled"]),
    )