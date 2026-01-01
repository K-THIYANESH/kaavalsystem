"""Match events table."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Match(Base):
    """Records match detections linking persons to media evidence."""

    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), index=True)
    match_score = Column(Float)
    frame_number = Column(Integer)
    video_file = Column(String(512))
    timestamp = Column(Float)
    location = Column(String(255))
    latitude = Column(Float, nullable=True)  # For Google Maps
    longitude = Column(Float, nullable=True)  # For Google Maps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    person = relationship("Person", backref="matches")

