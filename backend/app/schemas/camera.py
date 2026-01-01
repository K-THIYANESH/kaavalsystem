"""Schemas for camera-based operations."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CameraStartRequest(BaseModel):
    """Parameters accepted when starting a live camera stream."""

    device_id: int = Field(0, description="OpenCV device index")
    frame_skip: int = Field(3, ge=0, le=15, description="Number of frames to skip by default")
    adaptive: bool = Field(True, description="Enable adaptive frame skipping to hit target FPS")
    resolution: tuple[int, int] | None = Field(
        default=None, description="Optional desired resolution (width, height)"
    )


class CameraStatusResponse(BaseModel):
    """Report camera health and stream metadata."""

    status: str
    message: str
    fps: Optional[float] = Field(None, description="Measured frames per second")
    frame_skip: Optional[int] = Field(None, description="Current frame skip interval")
    gpu_utilization: Optional[float] = Field(None, description="Percent GPU utilization")
    active_matches: Optional[int] = Field(None, description="Number of matches awaiting review")

