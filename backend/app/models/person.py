"""Database model for person records."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from .base import Base


class Person(Base):
    """ORM mapping for the persons table."""

    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, index=True)
    gender = Column(String(32), index=True)
    ethnicity = Column(String(64), index=True)
    hair_color = Column(String(32), index=True)
    skin_tone = Column(String(32), index=True)
    eye_color = Column(String(32), index=True)
    tattoos = Column(Text)
    scars = Column(Text)
    missing_since = Column(String(64))
    description = Column(Text)
    photo_path = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

