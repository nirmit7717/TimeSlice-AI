import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models import DbTransaction
from database.sync.sync_manager import SyncManager
from platform_services.auth.cognito import CognitoAuth
from platform_services.calendars.google_cal import GoogleCalendarSync
from platform_services.notifications.telegram import TelegramNotificationService
from platform_services.background.bg_sync import BackgroundSyncService

def test_cognito_auth_mock():
    auth = CognitoAuth(user_pool_id="us-east-1_xxxx", client_id="yyyy", region="us-east-1")
    claims = auth.verify_token("mock-user-token-abc")
    assert claims["username"] == "mockuser"
    assert claims["email"] == "mock@timeslice.ai"

def test_google_calendar_mock_translation():
    sync = GoogleCalendarSync()
    now = datetime.now(timezone.utc)
    
    # Fetch mock events
    events = sync.fetch_events(access_token="mock-token", start_time=now, end_time=now)
    assert len(events) == 2
    assert events[0]["summary"] == "Team Sync Meeting"
    
    # Translate to local blocked intervals
    intervals = sync.to_blocked_intervals(events)
    assert len(intervals) == 2
    # Verify they are datetime objects
    assert isinstance(intervals[0][0], datetime)
    assert isinstance(intervals[0][1], datetime)

def test_telegram_notifications_mock():
    notifier = TelegramNotificationService(bot_token="mock-token")
    success = notifier.send_message(chat_id="12345", message="<b>Test Alert</b>")
    assert success is True

def test_background_sync_service():
    async def run_async_test():
        # 1. Setup in-memory DB
        engine = create_engine("sqlite:///:memory:")
        TestingSession = sessionmaker(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        db = TestingSession()
        
        # 2. Add an unsynced transaction log
        sync_manager = SyncManager(db)
        sync_manager.db.add(DbTransaction(
            id="tx-mock-1",
            table_name="processes",
            record_id="p-1",
            action="INSERT",
            payload="{}"
        ))
        sync_manager.db.commit()
        
        # Verify it is pending
        pending = sync_manager.get_pending_transactions()
        assert len(pending) == 1
        db.close()
        
        # 3. Trigger worker sync
        worker = BackgroundSyncService(interval_seconds=0.1)
        
        # Start and run loop briefly, then stop
        worker.start(TestingSession, cloud_endpoint="mock-cloud-endpoint")
        await asyncio.sleep(0.5) # Wait for worker loop
        worker.stop()
        
        # 4. Check if transaction log was updated to synced
        db_check = TestingSession()
        sync_mgr_check = SyncManager(db_check)
        pending_check = sync_mgr_check.get_pending_transactions()
        assert len(pending_check) == 0  # Successfully synced!
        db_check.close()

    asyncio.run(run_async_test())
