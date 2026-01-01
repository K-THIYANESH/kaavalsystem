"""Reporting endpoints for user and admin reports."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ...auth.security import decode_access_token, get_current_user
from ...core.database import get_db
from ...models.user import MissingPersonReport, FoundPersonReport
from ...schemas.auth import FoundPersonReportRequest, MissingPersonReportRequest, ReportResponse
from sqlalchemy.orm import Session

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("/missing/recent", response_model=List[dict])
async def get_recent_missing(
    limit: int = 10,
    db: Session = Depends(get_db),
) -> List[dict]:
    """Get recently reported missing persons for dashboard."""
    reports = (
        db.query(MissingPersonReport)
        .order_by(MissingPersonReport.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "person_name": r.person_name,
            "age": r.person_age,
            "gender": r.person_gender,
            "last_seen": r.last_seen_location,
            "last_seen_location": r.last_seen_location,
            "photo_path": r.photo_path,
            "description": getattr(r, "description", None),
            "reported_at": r.created_at.isoformat() if r.created_at else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]


@router.get("/found/recent", response_model=List[dict])
async def get_recent_found(
    limit: int = 10,
    db: Session = Depends(get_db),
) -> List[dict]:
    """Get recently reported found persons for dashboard."""
    reports = (
        db.query(FoundPersonReport)
        .order_by(FoundPersonReport.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "person_name": "Found Person",
            "found_location": r.found_location,
            "found_date": r.found_date.isoformat() if r.found_date else None,
            "person_description": r.person_description,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "reported_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]

