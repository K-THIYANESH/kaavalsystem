"""Dashboard API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from typing import Dict, Any

from ...core.metrics import metrics
from ...core.config import settings

router = APIRouter()


@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats():
    """Get real-time system statistics."""
    
    # System Metrics
    system_stats = metrics.get_summary()
    
    # GPU Stats (Mock for now, would use pynvml in production)
    gpu_stats = {
        "gpu_utilization": 45.0,  # %
        "memory_used": 4096,      # MB
        "memory_total": 8192,     # MB
        "temperature": 65         # C
    } if settings.use_gpu else {}

    # Cache Stats
    cache_stats = {
        "hit_ratio": 0.85,
        "items": 1240
    }

    return {
        "system": system_stats,
        "gpu": gpu_stats,
        "cache": cache_stats,
        "status": "healthy"
    }


@router.get("/report/generate")
async def generate_report():
    """Trigger generation of a research report."""
    # In a real implementation, this would trigger a background task
    # to compile all metrics and generate a PDF/HTML report.
    return {"message": "Report generation started", "job_id": "rep_12345"}
