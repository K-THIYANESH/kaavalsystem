"""Database + vector search orchestration."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

import numpy as np
from sqlalchemy.orm import Session
from ..core.database import db_session
from ..pipelines.search_pipeline import SearchPipeline
from ..repositories.embedding_repository import EmbeddingRepository
from ..repositories.match_repository import MatchRepository
from ..repositories.person_repository import PersonRepository
from ..schemas.database import (
    AttributeFilters,
    CandidateMatch,
    DatabaseSearchRequest,
    DatabaseSearchResponse,
    DatabaseStatsResponse,
    TimelineResponse,
)


class DatabaseService:
    """Coordinate hierarchical filtering with FAISS search."""

    def __init__(
        self,
        pipeline: SearchPipeline | None = None,
        person_repo: PersonRepository | None = None,
        embedding_repo: EmbeddingRepository | None = None,
        match_repo: MatchRepository | None = None,
    ) -> None:
        self.pipeline = pipeline or SearchPipeline()
        self.person_repo = person_repo or PersonRepository()
        self.embedding_repo = embedding_repo or EmbeddingRepository()
        self.match_repo = match_repo or MatchRepository()

    async def search(self, payload: DatabaseSearchRequest) -> DatabaseSearchResponse:
        filters = payload.filters
        filtered_ids = await self.pipeline.hierarchical_filter(filters)
        embedding_vector = payload.embedding_vector
        if not embedding_vector and payload.embedding_path:
            vector_path = Path(payload.embedding_path)
            if vector_path.exists():
                embedding_vector = np.load(vector_path).tolist()
        if not embedding_vector:
            raise ValueError("Embedding vector or path is required for search")

        enriched_payload = DatabaseSearchRequest(
            embedding_vector=embedding_vector,
            filters=filters,
            return_top_k=payload.return_top_k,
            include_attribute_scores=payload.include_attribute_scores,
            include_temporal_summary=payload.include_temporal_summary,
        )
        results = await self.pipeline.search(enriched_payload, candidate_ids=filtered_ids)
        candidates = [CandidateMatch(**candidate.dict()) for candidate in results.candidates]
        return DatabaseSearchResponse(
            candidates=candidates,
            truncated=results.truncated,
            search_latency_ms=results.search_latency_ms,
            filters_applied=filters,
        )

    async def get_stats(self) -> DatabaseStatsResponse:
        with db_session() as db:
            persons_count = db.query(self.person_repo.model).count()
            embeddings_count = db.query(self.embedding_repo.model).count()
            matches_count = db.query(self.match_repo.model).count()
        faiss_stats = await self.pipeline.index_stats()
        return DatabaseStatsResponse(
            persons_count=persons_count,
            embeddings_count=embeddings_count,
            matches_count=matches_count,
            faiss_index_size=faiss_stats.index_size,
            last_sync=faiss_stats.last_sync,
            reduction_percent=faiss_stats.reduction_percent,
            average_latency_ms=faiss_stats.average_latency_ms,
        )

    async def get_timeline(self, person_id: int) -> TimelineResponse:
        matches = await self.pipeline.timeline(person_id)
        return TimelineResponse(person_id=person_id, segments=matches.segments, anomalies_detected=matches.anomalies)

    async def sync_embeddings(self) -> List[int]:
        return await self.pipeline.sync_embeddings()


def get_database_service() -> DatabaseService:
    return DatabaseService()

