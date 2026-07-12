"""Notification subpackage init. Exposes initialization hooks."""

from notification_system.models import NotificationPayload, NotificationType, NotificationPriority, NotificationChannel
from notification_system.dispatcher import NotificationDispatcher
from notification_system.scheduler.reminder_scheduler import initialize_notification_scheduler

__all__ = [
    "NotificationPayload",
    "NotificationType",
    "NotificationPriority",
    "NotificationChannel",
    "NotificationDispatcher",
    "initialize_notification_scheduler"
]
