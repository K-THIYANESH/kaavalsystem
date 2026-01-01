"""Video analysis summary model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from .base import Base


class VideoAnalysis(Base):
    """Stores statistics for processed videos."""

    __tablename__ = "video_analysis"

    id = Column(Integer, primary_key=True, index=True)
    video_path = Column(String(512), nullable=False)
    total_frames = Column(Integer)
    selected_frames = Column(Integer)
    processing_time_seconds = Column(Float)
    matches_found = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

