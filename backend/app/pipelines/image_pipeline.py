"""Image restoration and age progression pipeline stubs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from ..core.config import settings
from ..ml import get_registry
from ..schemas.image import AgeVariant, RestorationAttributes


@dataclass
class RestorationResult:
    job_id: str
    restored_image_path: Path
    report_path: Path
    attributes: RestorationAttributes


class ImagePipeline:
    """Run restoration and optional age progression pipelines."""

    def __init__(self) -> None:
        self.registry = get_registry(settings.enable_age_progression)

    async def restore(self, image_path: Path, job_id: str) -> RestorationResult:
        restored_path, attributes = self.registry.restorer.restore(image_path)
        report_path = settings.reports_dir / f"{job_id}_restoration_report.json"
        report_path.write_text("{}", encoding="utf-8")
        return RestorationResult(
            job_id=job_id,
            restored_image_path=restored_path,
            report_path=report_path,
            attributes=attributes,
        )

    async def age_progress(self, job_id: str, age_offsets: List[int]) -> List[AgeVariant]:
        if not settings.enable_age_progression or not self.registry.age_progressor:
            return []
        offsets = age_offsets or [5, 10, 15, 20]
        base_path = settings.reports_dir
        return self.registry.age_progressor.progress(job_id, offsets, base_path)

