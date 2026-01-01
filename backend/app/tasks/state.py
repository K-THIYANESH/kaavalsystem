"""In-memory job registry for orchestration stubs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..schemas.video import MatchSummary, TimelineEvent, VideoResultsResponse


@dataclass
class JobState:
    """Track progress of long-running jobs."""

    job_id: str
    filename: str = ""  # Added filename
    status: str = "queued"
    total_frames: int = 0
    processed_frames: int = 0
    selected_frames: int = 0
    eta_seconds: float | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    results: Any | None = None

    def progress_payload(self) -> Dict[str, Any]:
        percent = 0.0
        if self.total_frames:
            percent = min(100.0, (self.processed_frames / max(1, self.total_frames)) * 100)
        return {
            "job_id": self.job_id,
            "filename": self.filename,
            "status": self.status,
            "processed_frames": self.processed_frames,
            "total_frames": self.total_frames,
            "selected_frames": self.selected_frames,
            "percent_complete": percent,
            "eta_seconds": self.eta_seconds,
        }


class JobRegistry:
    """Minimal in-memory job store (swap with Redis later)."""

    def __init__(self) -> None:
        self._jobs: Dict[str, JobState] = {}

    def add_job(self, job_id: str, total_frames: int, filename: str = "", results: Any | None = None, metadata: Dict[str, Any] | None = None) -> JobState:
        state = JobState(job_id=job_id, filename=filename, total_frames=total_frames, results=results, metadata=metadata or {})
        self._jobs[job_id] = state
        return state

    def update(self, job_id: str, **kwargs: Any) -> None:
        job = self._jobs.setdefault(job_id, JobState(job_id=job_id))
        for key, value in kwargs.items():
            setattr(job, key, value)

    def complete(self, job_id: str, results: Any) -> None:
        job = self._jobs.setdefault(job_id, JobState(job_id=job_id))
        job.status = "completed"
        job.results = results
        job.processed_frames = job.total_frames
        job.eta_seconds = 0.0

    def get(self, job_id: str) -> JobState | None:
        return self._jobs.get(job_id)

