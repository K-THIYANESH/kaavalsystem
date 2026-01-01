"""Provide analytics data for dashboards."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from ..schemas.analytics import DashboardMetrics, LatencyBreakdown, PerformanceSnapshot


class AnalyticsService:
    """Return synthetic analytics until real telemetry wiring is complete."""

    async def get_dashboard_metrics(self) -> DashboardMetrics:
        return DashboardMetrics(
            active_jobs=3,
            average_match_latency_ms=685.0,
            search_space_reduction_percent=88.5,
            reconstructed_faces_today=12,
            alerts_generated_today=4,
        )

    async def get_latency_breakdown(self) -> LatencyBreakdown:
        components = {
            "frame_acquisition": 35.0,
            "quality_filter": 58.0,
            "detection": 210.0,
            "recognition": 320.0,
            "faiss_search": 48.0,
            "specialist_models": 72.0,
        }
        return LatencyBreakdown(
            components=components,
            total_latency_ms=sum(components.values()),
            last_updated=datetime.utcnow(),
        )

    async def get_performance_snapshot(self) -> PerformanceSnapshot:
        base = datetime.utcnow()
        timestamps: List[datetime] = [base - timedelta(minutes=i * 5) for i in range(12)][::-1]
        return PerformanceSnapshot(
            metric_series={
                "match_latency_ms": [750 - i * 8 for i in range(12)],
                "search_reduction_percent": [85 + (i % 3) for i in range(12)],
                "gpu_utilization_percent": [40 + (i % 4) * 5 for i in range(12)],
            },
            timestamps=timestamps,
            notes=["Batch optimization applied", "Index sync", "Specialist model update"],
        )


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()

