"""Repository for match events."""

from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

from ..models.match import Match
from .base import Repository


class MatchRepository(Repository[Match]):
    """Persistence helpers for match events."""

    def __init__(self) -> None:
        super().__init__(Match)

    def list_for_person(self, db: Session, person_id: int) -> Iterable[Match]:
        return db.query(Match).filter(Match.person_id == person_id).order_by(Match.timestamp.asc()).all()

