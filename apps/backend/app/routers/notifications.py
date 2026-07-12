"""Notification API endpoints router.

Provides endpoints to trigger test notifications and query dispatch history logs.
"""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_db
from notification_system.models import NotificationType, NotificationPriority, NotificationChannel, NotificationPayload
from notification_system.dispatcher import NotificationDispatcher

router = APIRouter(tags=["notifications"])


# ── Request / Response schemas ─────────────────────────────────────────────────

class TestNotificationRequest(BaseModel):
    title: str = "Test Notification"
    message: str = "This is a verification notification from TimeSlice AI."
    priority: str = "normal"
    channels: List[str] = ["desktop"]


class NotificationLogOut(BaseModel):
    id: str
    type: str
    title: str
    message: str
    channels: List[str]
    delivered: bool
    error: Optional[str] = None
    timestamp: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/log", response_model=List[NotificationLogOut])
def get_notification_log(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Returns the operator's recent notification delivery log history
    saved within the DbNotificationLog table.
    """
    from database.models import DbNotificationLog
    logs = db.query(DbNotificationLog).filter(
        DbNotificationLog.operator_id == "default_operator"
    ).order_by(DbNotificationLog.sent_at.desc()).limit(limit).all()

    result = []
    for l in logs:
        try:
            payload_data = json.loads(l.payload or "{}")
        except Exception:
            payload_data = {}
            
        title = payload_data.get("title", "Notification")
        message = payload_data.get("message", "")
        errors = payload_data.get("errors", [])
        error_str = ", ".join(errors) if errors else None
        
        result.append(NotificationLogOut(
            id=l.id,
            type=l.notification_type,
            title=title,
            message=message,
            channels=[l.channel],
            delivered=l.delivered,
            error=error_str,
            timestamp=l.sent_at.isoformat()
        ))
    return result



@router.post("/test")
def send_test_notification(
    body: TestNotificationRequest,
    db: Session = Depends(get_db),
):
    """
    Manually triggers a test notification to verify channel connectivity (desktop and/or Telegram).
    """
    channels = []
    for c in body.channels:
        try:
            channels.append(NotificationChannel(c.lower()))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid channel option: '{c}'. Must be 'desktop' or 'telegram'."
            )
            
    try:
        priority = NotificationPriority(body.priority.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority level: '{body.priority}'."
        )

    payload = NotificationPayload(
        notification_type=NotificationType.TEST,
        title=body.title,
        message=body.message,
        priority=priority,
        channels=channels,
    )
    
    dispatcher = NotificationDispatcher(db)
    success = dispatcher.dispatch(payload)
    
    return {
        "status": "success" if success else "failed",
        "message": "Test notification dispatched.",
        "delivered": success
    }
