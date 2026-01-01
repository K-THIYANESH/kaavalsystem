"""Attribute-based narrowing for face recognition."""

from __future__ import annotations

from typing import Dict, List, Optional, Any

from sqlalchemy import or_

from ...core.database import db_session
from ...models.person import Person


class AttributeFilter:
    """Filters person candidates based on attribute criteria."""

    def filter_candidates(
        self,
        attributes: Dict[str, Any],
        tolerance: str = "strict"
    ) -> List[int]:
        """
        Return a list of person IDs that match the given attributes.
        
        Args:
            attributes: Dictionary of attribute keys and values (e.g., {"gender": "Male", "age": 30}).
            tolerance: 'strict' (all must match) or 'loose' (some can mismatch).
        
        Returns:
            List of Person IDs.
        """
        if not attributes:
            return []

        with db_session() as session:
            query = session.query(Person.id)

            # Gender (usually strict)
            if "gender" in attributes and attributes["gender"]:
                query = query.filter(Person.gender == attributes["gender"])

            # Ethnicity (usually strict)
            if "ethnicity" in attributes and attributes["ethnicity"]:
                query = query.filter(Person.ethnicity == attributes["ethnicity"])

            # Age (range based)
            if "age" in attributes and attributes["age"]:
                age = int(attributes["age"])
                # +/- 5 years tolerance
                query = query.filter(Person.age.between(age - 5, age + 5))

            # Hair Color
            if "hair_color" in attributes and attributes["hair_color"]:
                if tolerance == "strict":
                    query = query.filter(Person.hair_color == attributes["hair_color"])
                else:
                    # Allow unknown or match
                    query = query.filter(or_(Person.hair_color == attributes["hair_color"], Person.hair_color == None))

            # Execute
            results = query.all()
            return [r[0] for r in results]
