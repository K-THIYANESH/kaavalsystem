"""Schemas powering analytics dashboards."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    """Headline figures for the dashboard."""

    active_jobs: int
    average_match_latency_ms: float
    search_space_reduction_percent: float
    reconstructed_faces_today: int
    alerts_generated_today: int


class LatencyBreakdown(BaseModel):
    """Latency contribution of each pipeline component."""

    components: Dict[str, float]
    total_latency_ms: float
    last_updated: datetime


class PerformanceSnapshot(BaseModel):
    """Comprehensive stats for analytics reports."""

    metric_series: Dict[str, List[float]]
    timestamps: List[datetime]
    notes: List[str]

