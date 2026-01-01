"""Application metrics setup."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


def register_metrics(app: FastAPI) -> None:
    """Placeholder for metrics instrumentation.

    Registers a lightweight `/metrics` endpoint for scraping or debugging.
    Keep `/healthz` defined by application entrypoint to avoid duplicate routes.
    """

    @app.get("/metrics", tags=["telemetry"], include_in_schema=False)
    async def metrics() -> dict[str, Any]:
        # Return a simple metrics payload. Replace with Prometheus text format if needed.
        return {
            "uptime_seconds": 0,
            "active_workers": 0,
            "queued_jobs": 0,
        }

