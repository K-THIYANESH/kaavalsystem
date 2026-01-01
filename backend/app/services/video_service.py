"""Service orchestrating video uploads and processing."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile

from ..core.config import settings
from ..core.database import SessionLocal
from ..pipelines.video_pipeline import VideoPipeline
from ..repositories.video_analysis_repository import VideoAnalysisRepository
from ..schemas.video import VideoJobResponse, VideoProgressResponse, VideoResultsResponse
from ..tasks.state import JobRegistry


class VideoService:
    """Manage lifecycle of video analysis jobs."""

    def __init__(
        self,
        pipeline: VideoPipeline | None = None,
        registry: JobRegistry | None = None,
        repository: VideoAnalysisRepository | None = None,
    ) -> None:
        self.pipeline = pipeline or VideoPipeline()
        self.registry = registry or JobRegistry()
        self.repository = repository or VideoAnalysisRepository()

    async def enqueue_video(self, video_file: UploadFile, reference_image: UploadFile | None = None) -> VideoJobResponse:
        job_id = str(uuid.uuid4())
        destination = settings.uploads_dir / video_file.filename
        with destination.open("wb") as buffer:
            content = await video_file.read()
            buffer.write(content)

        # Save reference image if provided
        reference_path = None
        if reference_image and reference_image.filename:
            reference_destination = settings.uploads_dir / f"{job_id}_reference_{reference_image.filename}"
            with reference_destination.open("wb") as buffer:
                content = await reference_image.read()
                buffer.write(content)
            reference_path = reference_destination

        # Store reference image path in job metadata
        self.registry.add_job(
            job_id, 
            total_frames=0, 
            filename=video_file.filename, 
            metadata={"reference_image_path": str(reference_path) if reference_path else None}
        )
        return VideoJobResponse(
            job_id=job_id,
            filename=video_file.filename,
            status="queued",
            submitted_at=datetime.utcnow(),
        )

    async def process_video_job(self, job_id: str) -> None:
        job = self.registry.get(job_id)
        if not job:
            return
        self.registry.update(job_id, status="processing")

        # Simulated pipeline run
        await self.pipeline.run(job_id, self.registry)

        self.registry.update(job_id, status="completed")

        # Persist summary stats
        from ..core.database import db_session
        with db_session() as session:
            summary = self.pipeline.last_summary
            if summary:
                self.repository.add(session, summary)

    async def get_progress(self, job_id: str) -> VideoProgressResponse:
        job = self.registry.get(job_id)
        if not job:
            raise KeyError(f"Job {job_id} not found")
        return VideoProgressResponse(**job.progress_payload())

    async def get_results(self, job_id: str) -> VideoResultsResponse:
        job = self.registry.get(job_id)
        if not job or not job.results:
            raise KeyError(f"Job {job_id} has no results yet")
        return job.results


def get_video_service() -> VideoService:
    return VideoService()

