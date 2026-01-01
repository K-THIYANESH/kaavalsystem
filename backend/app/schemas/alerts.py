"""Schemas for alert system."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class AlertRequest(BaseModel):
    """Request to create an alert."""
    
    person_id: int
    person_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    match_type: str = Field(..., description="Type: 'live_camera', 'video', 'image'")
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AlertResponse(BaseModel):
    """Alert response."""
    
    alert_id: int
    message: str
    alert: dict

