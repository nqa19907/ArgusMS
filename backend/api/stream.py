import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from backend.auth import DeviceContext, require_device

stream_router = APIRouter()


def _is_stream_fresh(pipeline) -> bool:
    cam_status = pipeline.reader.get_status()
    age_ms = cam_status.get("last_frame_age_ms")
    max_age_ms = int(pipeline.app_settings.stale_frame_seconds * 1000)
    return (
        cam_status["state"] == "CONNECTED"
        and age_ms is not None
        and age_ms <= max_age_ms
    )


async def mjpeg_generator(request: Request):
    pipeline = request.app.state.pipeline
    last_seq = 0
    interval = 1.0 / max(pipeline.app_settings.preview_fps, 1.0)
    while not await request.is_disconnected():
        if _is_stream_fresh(pipeline):
            jpeg_bytes, seq = pipeline.latest_jpeg.get()
            if jpeg_bytes is not None and seq != last_seq:
                last_seq = seq
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + jpeg_bytes + b"\r\n"
                )
        await asyncio.sleep(interval)


@stream_router.get("/api/v1/stream.mjpeg")
async def stream_mjpeg(
    request: Request,
    _device: DeviceContext = Depends(require_device),
) -> StreamingResponse:
    return StreamingResponse(
        mjpeg_generator(request),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@stream_router.get("/api/v1/preview.jpg")
async def get_preview(
    request: Request,
    _device: DeviceContext = Depends(require_device),
) -> Response:
    pipeline = request.app.state.pipeline
    jpeg_bytes, _ = pipeline.latest_jpeg.get()
    if jpeg_bytes is None or not _is_stream_fresh(pipeline):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Khung hình chưa sẵn sàng hoặc đã quá hạn (stale frame)",
        )
    return Response(content=jpeg_bytes, media_type="image/jpeg")