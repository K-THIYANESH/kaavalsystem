"""Feature Store for managing ML feature versions and lineage."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON

from .database import Base, db_session


class FeatureSet(Base):
    """SQLAlchemy model for feature sets."""

    __tablename__ = "feature_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    version = Column(String(32), nullable=False)
    description = Column(Text)
    schema = Column(Text)  # JSON string of schema definition
    metadata_json = Column(Text)  # JSON string of arbitrary metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FeatureStore:
    """Manager for feature sets and their metadata."""

    def register_feature_set(
        self,
        name: str,
        version: str,
        schema: Dict[str, Any],
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FeatureSet:
        """Register a new feature set or update existing one."""
        with db_session() as session:
            feature_set = session.query(FeatureSet).filter(FeatureSet.name == name).first()
            
            if feature_set:
                feature_set.version = version
                feature_set.schema = json.dumps(schema)
                feature_set.description = description
                feature_set.metadata_json = json.dumps(metadata or {})
            else:
                feature_set = FeatureSet(
                    name=name,
                    version=version,
                    schema=json.dumps(schema),
                    description=description,
                    metadata_json=json.dumps(metadata or {}),
                )
                session.add(feature_set)
            
            return feature_set

    def get_feature_set(self, name: str) -> Optional[FeatureSet]:
        """Retrieve a feature set by name."""
        with db_session() as session:
            return session.query(FeatureSet).filter(FeatureSet.name == name).first()

    def log_lineage(self, feature_set_name: str, source: str, operation: str) -> None:
        """Log data lineage (placeholder for more complex lineage tracking)."""
        # In a full implementation, this would write to a Lineage table.
        # For now, we update the metadata of the feature set.
        with db_session() as session:
            fs = session.query(FeatureSet).filter(FeatureSet.name == feature_set_name).first()
            if fs:
                meta = json.loads(fs.metadata_json) if fs.metadata_json else {}
                lineage = meta.get("lineage", [])
                lineage.append(
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "source": source,
                        "operation": operation,
                    }
                )
                meta["lineage"] = lineage
                fs.metadata_json = json.dumps(meta)


feature_store = FeatureStore()
