"""Image restoration and age progression service."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import UploadFile

from ..core.config import settings
from ..pipelines.image_pipeline import ImagePipeline
from ..schemas.image import (
    AgeProgressionRequest,
    AgeProgressionResponse,
    ImageRestoreResponse,
)
from ..tasks.state import JobRegistry


class ImageService:
    """Coordinates reconstruction and optional age progression."""

    def __init__(self, pipeline: ImagePipeline | None = None, registry: JobRegistry | None = None) -> None:
        self.pipeline = pipeline or ImagePipeline()
        self.registry = registry or JobRegistry()

    async def restore_face(self, image_file: UploadFile) -> ImageRestoreResponse:
        job_id = str(uuid.uuid4())
        destination = settings.uploads_dir / image_file.filename
        with destination.open("wb") as buffer:
            buffer.write(await image_file.read())

        restoration = await self.pipeline.restore(destination, job_id)
        self.registry.add_job(job_id, total_frames=0, results=restoration)

        return ImageRestoreResponse(
            job_id=job_id,
            status="completed",
            restored_image_path=str(restoration.restored_image_path),
            enhancement_report_path=str(restoration.report_path),
            attributes=restoration.attributes,
            processed_at=datetime.utcnow(),
        )

    async def enqueue_age_progression(self, payload: AgeProgressionRequest) -> AgeProgressionResponse:
        if not settings.enable_age_progression:
            return AgeProgressionResponse(job_id=payload.job_id, status="disabled", variants=[])

        job_id = payload.job_id or str(uuid.uuid4())
        self.registry.update(
            job_id,
            status="queued",
            metadata={"target_ages": payload.target_ages},
        )
        return AgeProgressionResponse(job_id=job_id, status="queued", variants=[])

    async def process_age_progression(self, job_id: str) -> None:
        job = self.registry.get(job_id)
        if not job:
            return
        self.registry.update(job_id, status="processing")
        variants = await self.pipeline.age_progress(job_id, job.metadata.get("target_ages", []))
        response = AgeProgressionResponse(job_id=job_id, status="completed", variants=variants)
        self.registry.complete(job_id, response)


def get_image_service() -> ImageService:
    return ImageService()

