"""Schemas for image restoration and age progression flows."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RestorationAttributes(BaseModel):
    """Metadata extracted during restoration."""

    damage_type: str
    damage_extent: float
    age: Optional[int]
    gender: Optional[str]
    ethnicity: Optional[str]
    skin_tone: Optional[str]
    hair_color: Optional[str]
    eye_color: Optional[str]
    tattoo_markers: List[str] = Field(default_factory=list)


class ImageRestoreResponse(BaseModel):
    """Payload returned after running restoration models."""

    job_id: str
    status: str
    restored_image_path: str
    enhancement_report_path: str
    attributes: RestorationAttributes
    processed_at: datetime


class AgeProgressionRequest(BaseModel):
    """Request body for generating age progression images."""

    job_id: str = Field(..., description="Restoration job id to use as source")
    target_ages: List[int] = Field(default_factory=lambda: [5, 10, 15, 20])
    auto_process: bool = Field(False, description="Automatically start processing in background")


class AgeVariant(BaseModel):
    """Representation of a single age variant image."""

    age_offset: int
    image_path: str
    confidence: float


class AgeProgressionResponse(BaseModel):
    """Response for age progression queueing or completion."""

    job_id: str
    status: str
    variants: List[AgeVariant] = Field(default_factory=list)

