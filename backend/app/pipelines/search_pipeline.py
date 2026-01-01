"""Search pipeline combining hierarchical filtering and FAISS stubs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from ..schemas.database import AttributeFilters, CandidateMatch, DatabaseSearchRequest
from ..core.config import settings
from ..ml import get_registry


@dataclass
class SearchResult:
    candidates: List[CandidateMatch]
    search_latency_ms: float
    truncated: bool


@dataclass
class IndexStats:
    index_size: int
    last_sync: datetime | None
    reduction_percent: float
    average_latency_ms: float


@dataclass
class TimelineSummary:
    segments: List[dict]
    anomalies: List[str]


class SearchPipeline:
    """Placeholder for the innovation layer search logic."""

    def __init__(self) -> None:
        self.registry = get_registry(settings.enable_age_progression)

    async def hierarchical_filter(self, filters: AttributeFilters) -> List[int]:
        # Pretend to reduce search space drastically using filters
        return list(range(1, 50001))

    async def search(self, payload: DatabaseSearchRequest, candidate_ids: List[int]) -> SearchResult:
        embedding = payload.embedding_vector or [0.0] * 512
        coarse_ids = self.registry.matcher.coarse_filter(embedding, candidate_ids)
        matches = self.registry.matcher.fine_match(embedding, coarse_ids)

        candidates: List[CandidateMatch] = []
        for match in matches:
            candidates.append(
                CandidateMatch(
                    person_id=match.person_id,
                    name=f"Candidate #{match.person_id}",
                    confidence=match.score,
                    attribute_score=match.attribute_score,
                    evidence_frames=[f"frame_{match.person_id}.jpg"],
                    timeline_summary="Auto-generated from temporal tracker",
                )
            )
        return SearchResult(candidates=candidates, search_latency_ms=685.0, truncated=False)

    async def index_stats(self) -> IndexStats:
        return IndexStats(
            index_size=500_000,
            last_sync=datetime.utcnow(),
            reduction_percent=88.0,
            average_latency_ms=685.0,
        )

    async def timeline(self, person_id: int) -> TimelineSummary:
        return TimelineSummary(
            segments=[{"start": 750.0, "end": 765.5, "camera_id": "CAM-1", "location": "Gateway"}],
            anomalies=["Gap detected between 13:15 and 14:20"],
        )

    async def sync_embeddings(self) -> List[int]:
        return list(range(10))

