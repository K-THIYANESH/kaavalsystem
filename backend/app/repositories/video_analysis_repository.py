"""Repository for video analysis summaries."""

from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

from ..models.video_analysis import VideoAnalysis
from .base import Repository


class VideoAnalysisRepository(Repository[VideoAnalysis]):
    """Handle persistence of video analysis metadata."""

    def __init__(self) -> None:
        super().__init__(VideoAnalysis)

    def recent(self, db: Session, limit: int = 10) -> Iterable[VideoAnalysis]:
        return db.query(VideoAnalysis).order_by(VideoAnalysis.created_at.desc()).limit(limit).all()

