import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, Field
from backend.auth import DeviceContext, require_device
from backend.camera.reader import validate_rtsp_url

api_router = APIRouter()


class ClaimPairingRequest(BaseModel):
    pairing_code: str = Field(..., min_length=10, max_length=256)
    expected_installation_id: str = Field(default="", max_length=128)
    client_label: str = Field(default="Dien thoai nguoi cham soc", max_length=128)


class CameraConfigRequest(BaseModel):
    rtsp_url: str = Field(..., min_length=8, max_length=512)
    label: str = Field(default="Living Room", max_length=128)


class PushUpdateRequest(BaseModel):
    push_kind: str = Field(default="fcm", pattern="^(fcm|fid)$")
    push_value: str = Field(..., min_length=10, max_length=4096)
    sound_enabled: bool = True


@api_router.get("/health")
async def health() -> dict:
    return {"status": "alive", "schema_version": 1}


@api_router.post("/api/v1/pairing/claim", status_code=status.HTTP_201_CREATED)
async def claim_pairing(payload: ClaimPairingRequest, request: Request) -> dict:
    storage = request.app.state.storage
    try:
        return storage.claim_pairing_code(
            raw_code=payload.pairing_code,
            expected_installation_id=payload.expected_installation_id,
            client_label=payload.client_label,
        )
    except ValueError as exc:
        code = str(exc)
        if code == "ALREADY_CONSUMED":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Mã ghép đã được sử dụng")
        if code == "EXPIRED_CODE":
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Mã ghép đã hết hạn")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dữ liệu ghép thiết bị không hợp lệ")


@api_router.get("/api/v1/status")
async def get_status(
    request: Request,
    _device: DeviceContext = Depends(require_device),
) -> dict:
    storage = request.app.state.storage
    pipeline = request.app.state.pipeline
    fcm_sender = request.app.state.fcm_sender

    return {
        "schema_version": 1,
        "installation_id": storage.get_installation_id(),
        "camera": pipeline.reader.get_status(),
        "ai": pipeline.get_ai_status(),
        "notifications": {
            "configured": fcm_sender.is_configured and storage.has_configured_push_device(),
            "last_send_state": fcm_sender.last_send_state,
        },
    }


@api_router.put("/api/v1/camera", status_code=status.HTTP_202_ACCEPTED)
async def set_camera(
    payload: CameraConfigRequest,
    request: Request,
    _device: DeviceContext = Depends(require_device),
) -> dict:
    try:
        validated_url = validate_rtsp_url(payload.rtsp_url)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    storage = request.app.state.storage
    pipeline = request.app.state.pipeline
    storage.save_camera_config(
        camera_id=pipeline.reader.camera_id,
        source="rtsp",
        protected_url=validated_url,
        label=payload.label,
    )
    pipeline.switch_camera(validated_url, payload.label)
    return {
        "schema_version": 1,
        "state": "CONNECTING",
        "request_id": f"req-{uuid.uuid4().hex[:10]}",
    }


@api_router.post("/api/v1/camera/stop", status_code=status.HTTP_202_ACCEPTED)
async def stop_camera(
    request: Request,
    _device: DeviceContext = Depends(require_device),
) -> dict:
    pipeline = request.app.state.pipeline
    pipeline.stop_camera()
    return {"schema_version": 1, "state": "STOPPED"}


@api_router.get("/api/v1/events")
async def list_events(
    request: Request,
    after: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    _device: DeviceContext = Depends(require_device),
) -> dict:
    storage = request.app.state.storage
    items, next_cursor = storage.list_events(after_cursor=after, limit=limit)
    return {
        "schema_version": 1,
        "events": items,
        "next_cursor": next_cursor,
    }


@api_router.post("/api/v1/events/{event_id}/ack")
async def ack_event(
    event_id: str,
    request: Request,
    _device: DeviceContext = Depends(require_device),
) -> dict:
    event_service = request.app.state.event_service
    found = event_service.acknowledge(event_id)
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sự kiện không tồn tại")
    return {"schema_version": 1, "event_id": event_id, "acknowledged": True}


@api_router.put("/api/v1/devices/{device_id}/push")
async def update_device_push(
    device_id: str,
    payload: PushUpdateRequest,
    request: Request,
    device: DeviceContext = Depends(require_device),
) -> dict:
    if device.device_id != device_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không được phép cập nhật thông tin push của thiết bị khác",
        )
    storage = request.app.state.storage
    storage.update_device_push(
        device_id=device_id,
        push_kind=payload.push_kind,
        push_value=payload.push_value,
        sound_enabled=payload.sound_enabled,
    )
    return {"schema_version": 1, "device_id": device_id, "updated": True}


@api_router.delete("/api/v1/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    request: Request,
    device: DeviceContext = Depends(require_device),
) -> Response:
    if device.device_id != device_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không được phép thu hồi thiết bị khác",
        )
    request.app.state.storage.revoke_device(device_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api_router.post("/api/v1/notifications/test", status_code=status.HTTP_202_ACCEPTED)
async def send_test_notification(
    request: Request,
    device: DeviceContext = Depends(require_device),
) -> dict:
    event_service = request.app.state.event_service
    pipeline = request.app.state.pipeline
    record = event_service.create_test_event(
        camera_id=pipeline.reader.camera_id,
        target_device_id=device.device_id,
    )
    return {
        "schema_version": 1,
        "event_id": record.event_id,
        "is_test": True,
    }