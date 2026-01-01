"""Generate forensic reports and evidence packs."""

from __future__ import annotations

import uuid
from datetime import datetime

from ..core.config import settings
from ..pipelines.reporting_pipeline import ReportingPipeline
from ..schemas.results import EvidencePackResponse, ReportRequest, ReportResponse


class ResultsService:
    """Coordinate report generation and asset bundling."""

    def __init__(self, pipeline: ReportingPipeline | None = None) -> None:
        self.pipeline = pipeline or ReportingPipeline()

    async def generate_report(self, payload: ReportRequest) -> ReportResponse:
        report_id = str(uuid.uuid4())
        path = await self.pipeline.generate_report(payload, report_id)
        return ReportResponse(
            report_id=report_id,
            job_id=payload.job_id,
            format=payload.format,
            path=str(path),
            generated_at=datetime.utcnow(),
        )

    async def get_evidence_pack(self, job_id: str) -> EvidencePackResponse:
        pack = await self.pipeline.evidence_pack(job_id)
        return EvidencePackResponse(**pack.dict())


def get_results_service() -> ResultsService:
    return ResultsService()

