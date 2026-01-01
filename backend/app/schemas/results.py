"""Schemas for forensic report exports."""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """Request to generate a mission report."""

    job_id: str
    include_video_summary: bool = True
    include_image_assets: bool = True
    include_age_progression: bool = False
    format: str = Field("pdf", pattern="^(pdf|json|html)$")


class ReportResponse(BaseModel):
    """Meta information for a generated report."""

    report_id: str
    job_id: str
    format: str
    path: str
    generated_at: datetime


class EvidencePackResponse(BaseModel):
    """Paths for downloadable evidence assets."""

    job_id: str
    reconstructed_faces: List[str]
    age_progression_variants: List[str]
    timeline_media: List[str]
    compressed_bundle: str

