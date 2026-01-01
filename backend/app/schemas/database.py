"""Schemas for database and vector search operations."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AttributeFilters(BaseModel):
    """Attributes to prioritize when narrowing the search space."""

    age_min: Optional[int]
    age_max: Optional[int]
    gender: Optional[str]
    ethnicity: Optional[str]
    skin_tone: Optional[str]
    hair_color: Optional[str]
    eye_color: Optional[str]
    tattoo_keywords: List[str] = Field(default_factory=list)
    scar_keywords: List[str] = Field(default_factory=list)
    specialist_model_override: Optional[str]


class DatabaseSearchRequest(BaseModel):
    """Request body for attribute-assisted search."""

    embedding_path: Optional[str] = None
    embedding_vector: Optional[List[float]] = None
    filters: AttributeFilters = Field(default_factory=AttributeFilters)
    return_top_k: int = 10
    include_attribute_scores: bool = True
    include_temporal_summary: bool = True


class CandidateMatch(BaseModel):
    """Single candidate returned from the vector search."""

    person_id: int
    name: Optional[str]
    confidence: float
    attribute_score: Optional[float]
    evidence_frames: List[str]
    timeline_summary: Optional[str]


class DatabaseSearchResponse(BaseModel):
    """Response payload for a database search."""

    candidates: List[CandidateMatch]
    truncated: bool
    search_latency_ms: float
    filters_applied: AttributeFilters


class DatabaseStatsResponse(BaseModel):
    """Expose database-wide statistics."""

    persons_count: int
    embeddings_count: int
    matches_count: int
    faiss_index_size: int
    last_sync: Optional[datetime]
    reduction_percent: float
    average_latency_ms: float


class TimelineSegment(BaseModel):
    """Segment representing a continuous presence interval."""

    start: float
    end: float
    camera_id: Optional[str]
    location: Optional[str]


class TimelineResponse(BaseModel):
    """Timeline information for a matched person."""

    person_id: int
    segments: List[TimelineSegment]
    anomalies_detected: List[str]

