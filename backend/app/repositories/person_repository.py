"""Repository interface for person records."""

from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

from ..models.person import Person
from .base import Repository


class PersonRepository(Repository[Person]):
    """Extended operations for persons."""

    def __init__(self) -> None:
        super().__init__(Person)

    def filter_by_attributes(
        self,
        db: Session,
        age_range: tuple[int, int] | None = None,
        gender: str | None = None,
        ethnicity: str | None = None,
    ) -> Iterable[Person]:
        query = db.query(Person)
        if age_range:
            query = query.filter(Person.age.between(*age_range))
        if gender:
            query = query.filter(Person.gender == gender)
        if ethnicity:
            query = query.filter(Person.ethnicity == ethnicity)
        return query.all()

