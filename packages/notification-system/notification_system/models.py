"""Pydantic models for the Notification System. PRD §8.8"""

from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class NotificationChannel(str, Enum):
    DESKTOP = "desktop"
    TELEGRAM = "telegram"


class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(str, Enum):
    TIME_SLICE_REMINDER = "time_slice_reminder"    # 5 min before focus session
    REFLECTION_PROMPT = "reflection_prompt"         # After session ends
    DEADLINE_ALERT = "deadline_alert"               # Deadline approaching
    WEEKLY_SUMMARY = "weekly_summary"               # Monday morning summary
    TEST = "test"                                   # Manual test notification


class NotificationPayload(BaseModel):
    """A single notification to be dispatched to one or more channels."""
    notification_type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: List[NotificationChannel] = [NotificationChannel.DESKTOP]
    # Optional context
    process_id: Optional[str] = None
    slice_id: Optional[str] = None
    operator_id: str = "default_operator"
    timestamp: datetime = None

    def __init__(self, **data):
        if data.get("timestamp") is None:
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)


class NotificationLog(BaseModel):
    """Record of a dispatched notification for audit/display."""
    id: str
    notification_type: str
    title: str
    message: str
    channels: List[str]
    delivered: bool
    error: Optional[str] = None
    timestamp: datetime
