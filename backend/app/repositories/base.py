"""Base repository helpers."""

from __future__ import annotations

import logging
from typing import Generic, Iterable, Optional, Type, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class Repository(Generic[ModelType]):
    """Reusable CRUD helpers for SQLAlchemy models."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, model_id: int) -> Optional[ModelType]:
        return db.query(self.model).get(model_id)

    def list(self, db: Session) -> Iterable[ModelType]:
        return db.query(self.model).all()

    def add(self, db: Session, instance: ModelType) -> ModelType:
        try:
            db.add(instance)
            db.commit()
            db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Database error in add operation: {e}")
            raise

    def delete(self, db: Session, instance: ModelType) -> None:
        try:
            db.delete(instance)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Database error in delete operation: {e}")
            raise

