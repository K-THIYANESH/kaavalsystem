"""Real-time alert system for strong matches."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import json
import asyncio
from datetime import datetime

from ...schemas.alerts import AlertResponse, AlertRequest
from ...models.match import Match
from ...core.database import db_session


router = APIRouter()

# In-memory alert queue (in production, use Redis or similar)
alert_queue: List[dict] = []


@router.post("/create", response_model=AlertResponse)
async def create_alert(payload: AlertRequest) -> AlertResponse:
    """Create an alert for a strong match (>85% confidence)."""
    if payload.confidence < 0.85:
        raise HTTPException(status_code=400, detail="Alert requires confidence >= 0.85")
    
    alert = {
        "id": len(alert_queue) + 1,
        "person_id": payload.person_id,
        "person_name": payload.person_name,
        "confidence": payload.confidence,
        "match_type": payload.match_type,
        "location": payload.location,
        "timestamp": datetime.utcnow().isoformat(),
        "acknowledged": False,
    }
    alert_queue.append(alert)
    
    return AlertResponse(
        alert_id=alert["id"],
        message="Alert created successfully",
        alert=alert,
    )


@router.get("/stream")
async def stream_alerts():
    """Server-Sent Events stream for real-time alerts."""
    async def event_generator():
        last_id = 0
        while True:
            # Check for new alerts
            new_alerts = [a for a in alert_queue if a["id"] > last_id]
            for alert in new_alerts:
                last_id = alert["id"]
                yield f"data: {json.dumps(alert)}\n\n"
            
            await asyncio.sleep(1)  # Poll every second
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/list", response_model=List[AlertResponse])
async def list_alerts(acknowledged: bool | None = None) -> List[AlertResponse]:
    """List all alerts, optionally filtered by acknowledged status."""
    alerts = alert_queue
    if acknowledged is not None:
        alerts = [a for a in alerts if a["acknowledged"] == acknowledged]
    
    return [
        AlertResponse(alert_id=a["id"], message="", alert=a)
        for a in alerts
    ]


@router.post("/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: int) -> dict:
    """Mark an alert as acknowledged."""
    for alert in alert_queue:
        if alert["id"] == alert_id:
            alert["acknowledged"] = True
            return {"message": "Alert acknowledged", "alert_id": alert_id}
    
    raise HTTPException(status_code=404, detail="Alert not found")

