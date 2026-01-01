"""Embeddings table model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, LargeBinary
from sqlalchemy.orm import relationship

from .base import Base


class Embedding(Base):
    """Stores face embeddings associated with a person."""

    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, index=True)
    embedding = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    person = relationship("Person", backref="embeddings")

