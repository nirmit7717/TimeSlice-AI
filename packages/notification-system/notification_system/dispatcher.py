"""Notification Dispatcher.

Orchestrates routing notifications to the designated channels (Desktop, Telegram, etc.)
and logs the outcomes to the database for history and audit tracking.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import List, Optional

from notification_system.models import NotificationPayload, NotificationChannel
from notification_system.channels.desktop_notifier import DesktopNotifier
from notification_system.channels.telegram_notifier import TelegramNotifier

logger = logging.getLogger("timeslice.notifications.dispatcher")


class NotificationDispatcher:
    """Dispatches notifications to various channels and tracks delivery logs."""

    def __init__(self, db_session=None):
        self.db = db_session
        self.desktop_notifier = DesktopNotifier()
        self.telegram_notifier = TelegramNotifier()

    def dispatch(self, payload: NotificationPayload) -> bool:
        """
        Dispatches a notification to all configured channels.
        Logs the result to the console, and to the DB if db_session is provided.
        """
        success = True
        errors = []
        channels_attempted = []

        # Get operator's Telegram Chat ID from profile if Telegram channel is requested
        telegram_chat_id = None
        if NotificationChannel.TELEGRAM in payload.channels:
            telegram_chat_id = self._get_telegram_chat_id(payload.operator_id)

        for channel in payload.channels:
            channels_attempted.append(channel.value)
            delivered = False

            if channel == NotificationChannel.DESKTOP:
                delivered = self.desktop_notifier.send(payload)
                if not delivered:
                    errors.append("Desktop delivery failed")
                    success = False

            elif channel == NotificationChannel.TELEGRAM:
                if telegram_chat_id:
                    delivered = self.telegram_notifier.send(payload, telegram_chat_id)
                    if not delivered:
                        errors.append("Telegram delivery failed")
                        success = False
                else:
                    errors.append("Telegram chat ID not configured")
                    logger.warning(
                        "[Dispatcher] Skipped Telegram delivery for %s: Chat ID not set.",
                        payload.operator_id
                    )
                    success = False

        # Log notification in the database if DB session is available
        if self.db:
            try:
                from database.models import DbNotificationLog
                for chan in payload.channels:
                    log_entry = DbNotificationLog(
                        id=str(uuid.uuid4()),
                        operator_id=payload.operator_id,
                        notification_type=payload.notification_type.value,
                        channel=chan.value,
                        payload=json.dumps({
                            "title": payload.title,
                            "message": payload.message,
                            "priority": payload.priority.value,
                            "process_id": payload.process_id,
                            "slice_id": payload.slice_id,
                            "errors": errors if not success else []
                        }),
                        sent_at=datetime.utcnow(),
                        delivered=success
                    )
                    self.db.add(log_entry)
                self.db.commit()
            except Exception as e:
                logger.error("[Dispatcher] Failed to write DbNotificationLog entry: %s", e)

        return success

    def _get_telegram_chat_id(self, operator_id: str) -> Optional[str]:
        """Resolves the Telegram Chat ID from the operator's adaptive profile."""
        if not self.db:
            return None
        try:
            from database.models import DbAdaptiveProfile
            profile = self.db.query(DbAdaptiveProfile).filter(
                DbAdaptiveProfile.operator_id == operator_id
            ).first()
            if profile and profile.notification_prefs:
                prefs = json.loads(profile.notification_prefs)
                return prefs.get("telegram_chat_id")
        except Exception as e:
            logger.error("[Dispatcher] Error resolving telegram chat ID: %s", e)
        return None
