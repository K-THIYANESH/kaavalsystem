"""Repository for embedding records."""

from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

from ..models.embedding import Embedding
from .base import Repository


class EmbeddingRepository(Repository[Embedding]):
    """Extra methods for embedding persistence."""

    def __init__(self) -> None:
        super().__init__(Embedding)

    def list_for_person(self, db: Session, person_id: int) -> Iterable[Embedding]:
        return db.query(Embedding).filter(Embedding.person_id == person_id).all()

