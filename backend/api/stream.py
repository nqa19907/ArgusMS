import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from backend.auth import DeviceContext, require_device

stream_router = APIRouter()


async def mjpeg_generator(request: Request):
    pipeline = request.app.state.pipeline
    last_seq = 0
    while not await request.is_disconnected():
        jpeg_bytes, seq = pipeline.latest_jpeg.get()
        if jpeg_bytes is not None and seq != last_seq:
            last_seq = seq
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpeg_bytes + b"\r\n"
            )
        await asyncio.sleep(0.15)


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
    cam_status = pipeline.reader.get_status()
    jpeg_bytes, _ = pipeline.latest_jpeg.get()
    if jpeg_bytes is None or cam_status["state"] not in ("CONNECTED", "RECONNECTING"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chưa có khung hình mới từ camera",
        )
    return Response(content=jpeg_bytes, media_type="image/jpeg")