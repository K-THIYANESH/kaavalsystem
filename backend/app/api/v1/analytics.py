"""Analytics and dashboard metric endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ...schemas.analytics import (
    DashboardMetrics,
    LatencyBreakdown,
    PerformanceSnapshot,
)
from ...telemetry.analytics_service import AnalyticsService, get_analytics_service


router = APIRouter()


@router.get("/dashboard", response_model=DashboardMetrics)
async def dashboard_metrics(service: AnalyticsService = Depends(get_analytics_service)) -> DashboardMetrics:
    """Return headline metrics for the landing dashboard."""

    return await service.get_dashboard_metrics()


@router.get("/latency", response_model=LatencyBreakdown)
async def latency_breakdown(service: AnalyticsService = Depends(get_analytics_service)) -> LatencyBreakdown:
    """Expose the latency contributions of each pipeline component."""

    return await service.get_latency_breakdown()


@router.get("/performance", response_model=PerformanceSnapshot)
async def performance_snapshot(service: AnalyticsService = Depends(get_analytics_service)) -> PerformanceSnapshot:
    """Expose extended performance statistics and benchmark comparisons."""

    return await service.get_performance_snapshot()

