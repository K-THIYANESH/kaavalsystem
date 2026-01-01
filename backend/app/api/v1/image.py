"""Image restoration and age progression endpoints."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, HTTPException

from ...schemas.image import (
    AgeProgressionRequest,
    AgeProgressionResponse,
    ImageRestoreResponse,
)
from ...services.image_service import ImageService, get_image_service


router = APIRouter()


@router.post("/restore", response_model=ImageRestoreResponse)
async def restore_image(
    image_file: UploadFile = File(...),
    service: ImageService = Depends(get_image_service),
) -> ImageRestoreResponse:
    """Restore a damaged facial image using the reconstruction pipeline."""
    
    # Validate image file
    if not image_file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")
    
    # Check file extension
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    file_ext = "." + image_file.filename.split(".")[-1].lower() if "." in image_file.filename else ""
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        return await service.restore_face(image_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore image: {str(e)}")


@router.post("/age_progression", response_model=AgeProgressionResponse)
async def age_progression(
    payload: AgeProgressionRequest,
    background_tasks: BackgroundTasks,
    service: ImageService = Depends(get_image_service),
) -> AgeProgressionResponse:
    """Optionally generate age progression variants for a reconstructed face."""

    job = await service.enqueue_age_progression(payload)
    if payload.auto_process:
        background_tasks.add_task(service.process_age_progression, job.job_id)
    return job

