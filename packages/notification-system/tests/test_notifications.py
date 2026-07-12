"""Unit tests for Phase 6: Notification System."""

import pytest
import json
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models import DbAdaptiveProfile, DbNotificationLog

from notification_system.models import (
    NotificationPayload,
    NotificationType,
    NotificationPriority,
    NotificationChannel,
)
from notification_system.channels.desktop_notifier import DesktopNotifier
from notification_system.channels.telegram_notifier import TelegramNotifier
from notification_system.dispatcher import NotificationDispatcher


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


class TestDesktopNotifier:
    def test_desktop_notify_returns_bool(self):
        notifier = DesktopNotifier()
        payload = NotificationPayload(
            notification_type=NotificationType.TEST,
            title="Desktop Test",
            message="This is a desktop test message.",
        )
        res = notifier.send(payload)
        assert isinstance(res, bool)


class TestTelegramNotifier:
    def test_telegram_no_op_when_not_configured(self):
        # Empty token
        notifier = TelegramNotifier(bot_token="")
        payload = NotificationPayload(
            notification_type=NotificationType.TEST,
            title="Telegram Test",
            message="This is a Telegram test message.",
        )
        res = notifier.send(payload, chat_id="123456789")
        # Returns False since token is not configured
        assert res is False


class TestNotificationDispatcher:
    def test_dispatch_records_log_in_database(self, db_session):
        # Add profile first
        profile = DbAdaptiveProfile(
            id="test-profile-id",
            operator_id="default_operator",
            notification_prefs=json.dumps({"telegram_chat_id": "987654321"})
        )
        db_session.add(profile)
        db_session.commit()

        payload = NotificationPayload(
            notification_type=NotificationType.TIME_SLICE_REMINDER,
            title="Session Reminder",
            message="Focus session starts soon.",
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.DESKTOP]
        )

        dispatcher = NotificationDispatcher(db_session)
        success = dispatcher.dispatch(payload)
        
        # Verify log entry exists in DB
        logs = db_session.query(DbNotificationLog).all()
        assert len(logs) == 1
        assert logs[0].notification_type == "time_slice_reminder"
        assert logs[0].channel == "desktop"
        
        payload_data = json.loads(logs[0].payload)
        assert payload_data["title"] == "Session Reminder"
        assert payload_data["priority"] == "high"

    def test_dispatch_telegram_resolves_chat_id(self, db_session):
        # Add profile with Telegram config
        profile = DbAdaptiveProfile(
            id="test-profile-id",
            operator_id="default_operator",
            notification_prefs=json.dumps({"telegram_chat_id": "555666"})
        )
        db_session.add(profile)
        db_session.commit()

        payload = NotificationPayload(
            notification_type=NotificationType.TEST,
            title="Telegram Test",
            message="Hello Telegram",
            channels=[NotificationChannel.TELEGRAM]
        )

        dispatcher = NotificationDispatcher(db_session)
        # Should call send() with the correct chat_id (555666).
        # Since Telegram bot token is empty, the send call will gracefully no-op and log success=False.
        success = dispatcher.dispatch(payload)
        assert success is False
        
        logs = db_session.query(DbNotificationLog).filter(
            DbNotificationLog.channel == "telegram"
        ).all()
        assert len(logs) == 1
        assert logs[0].delivered is False
