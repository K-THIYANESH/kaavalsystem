"""Database search and statistics endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ...schemas.database import (
    DatabaseSearchRequest,
    DatabaseSearchResponse,
    DatabaseStatsResponse,
    TimelineResponse,
)
from ...services.database_service import DatabaseService, get_database_service


router = APIRouter()


@router.post("/search", response_model=DatabaseSearchResponse)
async def search_database(
    payload: DatabaseSearchRequest,
    service: DatabaseService = Depends(get_database_service),
) -> DatabaseSearchResponse:
    """Execute a hierarchical attribute-aware search across the vector index."""
    try:
        return await service.search(payload)
    except ValueError as exc:
        # Treat as validation error for missing embedding (match tests)
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/stats", response_model=DatabaseStatsResponse)
async def database_stats(service: DatabaseService = Depends(get_database_service)) -> DatabaseStatsResponse:
    """Return aggregate statistics about the database and index performance."""

    return await service.get_stats()


@router.get("/timeline/{person_id}", response_model=TimelineResponse)
async def timeline(
    person_id: int,
    service: DatabaseService = Depends(get_database_service),
) -> TimelineResponse:
    """Retrieve the temporal tracker summary for a matched individual."""

    return await service.get_timeline(person_id)


@router.post("/bulk_sync", response_model=List[int])
async def bulk_sync_embeddings(
    service: DatabaseService = Depends(get_database_service),
) -> List[int]:
    """Synchronize new embeddings into the FAISS index (incremental update)."""

    return await service.sync_embeddings()

