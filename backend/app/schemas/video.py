"""Schemas for video upload and processing."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class VideoJobResponse(BaseModel):
    """Return payload when a video job is accepted."""

    job_id: str
    filename: str
    status: str = Field("queued")
    submitted_at: datetime


class VideoProgressResponse(BaseModel):
    """Describe progress of a video processing job."""

    job_id: str
    status: str
    processed_frames: int
    total_frames: int
    selected_frames: int
    percent_complete: float
    eta_seconds: Optional[float]


class TimelineEvent(BaseModel):
    """Single event in a temporal timeline."""

    timestamp: float
    label: str
    confidence: float
    frame_index: Optional[int] = None


class MatchSummary(BaseModel):
    """Aggregate summary data for a match occurring within the video."""

    person_id: int
    person_name: Optional[str]
    confidence: float
    start_time: float
    end_time: float
    frame_numbers: List[int]
    latitude: Optional[float] = None  # For Google Maps
    longitude: Optional[float] = None  # For Google Maps
    location_name: Optional[str] = None  # Human-readable location


class VideoResultsResponse(BaseModel):
    """Return match results for a completed video job."""

    job_id: str
    status: str
    processing_time_seconds: float
    matches_found: int
    timeline: List[TimelineEvent]
    matches: List[MatchSummary]

