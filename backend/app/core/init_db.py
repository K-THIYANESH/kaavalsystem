"""Utilities to initialize the database schema."""

from __future__ import annotations

from .database import engine
from ..models.base import Base
from ..models import (
    Person,
    Embedding,
    Match,
    VideoAnalysis,
    User,
    Admin,
    MissingPersonReport,
    FoundPersonReport,
)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()

