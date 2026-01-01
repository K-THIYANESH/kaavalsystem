"""Collect FastAPI route modules and expose a single router."""

from fastapi import APIRouter

from .v1 import camera, video, image, database, results, analytics, auth, reports, alerts, dashboard


api_router = APIRouter()

api_router.include_router(camera.router, prefix="/camera", tags=["camera"])
api_router.include_router(video.router, prefix="/video", tags=["video"])
api_router.include_router(image.router, prefix="/image", tags=["image"])
api_router.include_router(database.router, prefix="/database", tags=["database"])
api_router.include_router(results.router, prefix="/results", tags=["results"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

