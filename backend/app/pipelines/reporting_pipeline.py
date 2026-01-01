"""Generate reports and evidence packs."""

from __future__ import annotations

import json
from pathlib import Path

from ..core.config import settings
from ..schemas.results import EvidencePackResponse, ReportRequest


class ReportingPipeline:
    """Placeholder pipeline to stitch reports and assets."""

    async def generate_report(self, payload: ReportRequest, report_id: str) -> Path:
        output = settings.reports_dir / f"{report_id}.{payload.format}"
        if payload.format == "json":
            output.write_text(json.dumps({"job_id": payload.job_id, "format": payload.format}), encoding="utf-8")
        else:
            output.write_bytes(b"fake-report-content")
        return output

    async def evidence_pack(self, job_id: str) -> EvidencePackResponse:
        reconstructed = [str(settings.reports_dir / f"{job_id}_restored.png")]
        age_variants = [str(settings.reports_dir / f"{job_id}_age_{age}.png") for age in (5, 10, 15, 20)]
        timeline = [str(settings.reports_dir / f"{job_id}_timeline.mp4")]
        bundle = str(settings.reports_dir / f"{job_id}_evidence.zip")
        return EvidencePackResponse(
            job_id=job_id,
            reconstructed_faces=reconstructed,
            age_progression_variants=age_variants,
            timeline_media=timeline,
            compressed_bundle=bundle,
        )

