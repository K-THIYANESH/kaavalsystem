"""Video upload and batch analysis endpoints."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from fastapi import HTTPException, status

from ...schemas.video import (
    VideoJobResponse,
    VideoProgressResponse,
    VideoResultsResponse,
)
from ...services.video_service import VideoService, get_video_service


router = APIRouter()


@router.post("/upload", response_model=VideoJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_video(
    video_file: UploadFile = File(...),
    reference_image: UploadFile | None = File(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: VideoService = Depends(get_video_service),
) -> VideoJobResponse:
    """Accept a video file and optional reference image, then search for the person in video."""
    
    # Validate video file
    if not video_file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")
    
    # Check file extension
    allowed_video_extensions = {".mp4", ".mkv", ".mov", ".avi", ".webm"}
    video_ext = "." + video_file.filename.split(".")[-1].lower() if "." in video_file.filename else ""
    if video_ext not in allowed_video_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported video format. Allowed: {', '.join(allowed_video_extensions)}"
        )
    
    # Validate reference image if provided
    if reference_image and reference_image.filename:
        allowed_image_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        image_ext = "." + reference_image.filename.split(".")[-1].lower() if "." in reference_image.filename else ""
        if image_ext not in allowed_image_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format. Allowed: {', '.join(allowed_image_extensions)}"
            )

    try:
        job = await service.enqueue_video(video_file, reference_image)
        if background_tasks:
            background_tasks.add_task(service.process_video_job, job.job_id)
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process video upload: {str(e)}")


@router.get("/progress/{job_id}", response_model=VideoProgressResponse)
async def video_progress(
    job_id: str,
    service: VideoService = Depends(get_video_service),
) -> VideoProgressResponse:
    """Return the current progress of a video analysis job."""
    try:
        return await service.get_progress(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")


@router.get("/results/{job_id}", response_model=VideoResultsResponse)
async def video_results(
    job_id: str,
    service: VideoService = Depends(get_video_service),
) -> VideoResultsResponse:
    """Return the match results for a completed job."""
    try:
        return await service.get_results(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found or has no results yet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")


@router.get("/frames/{job_id}")
async def get_frame_extraction(
    job_id: str,
    service: VideoService = Depends(get_video_service),
) -> dict:
    """Get frame extraction table with timestamps for a video job."""
    results = await service.get_results(job_id)
    frames = []
    if results.timeline_events:
        for event in results.timeline_events:
            frames.append({
                "frame_number": event.get("frame_index", 0),
                "timestamp": event.get("timestamp", 0.0),
                "time_formatted": f"{int(event.get('timestamp', 0) // 60)}:{int(event.get('timestamp', 0) % 60):02d}",
                "confidence": event.get("confidence", 0.0),
                "person_id": event.get("person_id"),
                "person_name": event.get("person_name", "Unknown"),
                "location": event.get("location", "N/A"),
            })
    return {"job_id": job_id, "frames": frames, "total_frames": len(frames)}

