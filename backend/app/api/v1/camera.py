"""Camera streaming and live detection endpoints."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse

from ...schemas.camera import CameraStartRequest, CameraStatusResponse
from ...services.camera_service import CameraService, get_camera_service


router = APIRouter()


@router.post("/start", response_model=CameraStatusResponse)
async def start_camera(
    payload: CameraStartRequest,
    background_tasks: BackgroundTasks,
    service: CameraService = Depends(get_camera_service),
) -> CameraStatusResponse:
    """Boot the live camera pipeline and begin frame ingestion."""

    background_tasks.add_task(service.start_stream, payload)
    return CameraStatusResponse(status="initializing", message="Camera stream initialization started")


@router.post("/stop", response_model=CameraStatusResponse)
async def stop_camera(service: CameraService = Depends(get_camera_service)) -> CameraStatusResponse:
    """Gracefully close the active camera stream."""

    await service.stop_stream()
    return CameraStatusResponse(status="stopped", message="Camera stream stopped")


@router.get("/video_feed")
async def video_feed(service: CameraService = Depends(get_camera_service)) -> StreamingResponse:
    """Return an MJPEG streaming response for the live preview."""

    generator = service.stream_frames()
    return StreamingResponse(generator, media_type="multipart/x-mixed-replace; boundary=frame")


@router.get("/health", response_model=CameraStatusResponse)
async def camera_health(service: CameraService = Depends(get_camera_service)) -> CameraStatusResponse:
    """Report live camera health and telemetry."""

    status = await service.get_status()
    return CameraStatusResponse(**status)

