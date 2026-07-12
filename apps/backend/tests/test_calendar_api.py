import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.dependencies import get_db
from database.connection import Base
from database.models import DbCalendarEvent, DbTimeSlice, DbProcess

TEST_DB_URL = "sqlite:///w:/Projects Antigravity/TimeSlice AI/test_calendar.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    import os
    try:
        os.remove("w:/Projects Antigravity/TimeSlice AI/test_calendar.db")
    except OSError:
        pass


def test_calendar_crud_and_overlay():
    # 1. Create a local calendar event
    start_time = datetime.now(timezone.utc) + timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)
    
    payload = {
        "title": "Local Calendar Event Test",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "description": "Integration testing calendar",
        "location": "Local Office",
        "color": "secondary",
        "is_rest_period": False
    }
    
    res_create = client.post("/api/v1/calendar/events", json=payload)
    assert res_create.status_code == 201
    event_data = res_create.json()
    assert event_data["title"] == "Local Calendar Event Test"
    assert event_data["source"] == "local"
    event_id = event_data["id"]

    # Create a scheduled execution window to verify overlap overlay
    db = TestingSessionLocal()
    proc = DbProcess(
        id="p-cal-test",
        name="Calendar Test Process",
        deadline=datetime.now(timezone.utc) + timedelta(days=2),
        estimated_effort_hours=4.0,
        remaining_effort_hours=4.0,
        status="Active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(proc)
    db.commit()

    ts = DbTimeSlice(
        id="ts-cal-overlay-1",
        process_id="p-cal-test",
        start_time=start_time,
        end_time=end_time,
        duration_hours=1.0,
        status="Scheduled"
    )
    db.add(ts)
    db.commit()
    db.close()

    # 2. Get list of events (should include both manual event and scheduled focus window)
    res_list = client.get("/api/v1/calendar/events")
    assert res_list.status_code == 200
    events = res_list.json()
    assert len(events) == 2
    assert any(e["source"] == "local" for e in events)
    assert any(e["source"] == "execution_plan" for e in events)

    # 3. Update the local event
    update_payload = {
        "title": "Updated Local Calendar Event Test",
        "color": "accent"
    }
    res_upd = client.put(f"/api/v1/calendar/events/{event_id}", json=update_payload)
    assert res_upd.status_code == 200
    assert res_upd.json()["title"] == "Updated Local Calendar Event Test"
    assert res_upd.json()["color"] == "accent"

    # 4. Delete the local event
    res_del = client.delete(f"/api/v1/calendar/events/{event_id}")
    assert res_del.status_code == 204

    # Confirm deleted
    res_list_after = client.get("/api/v1/calendar/events")
    assert len(res_list_after.json()) == 1  # Only execution plan remains
    assert res_list_after.json()[0]["source"] == "execution_plan"


def test_google_calendar_stubs():
    # Test OAuth URL stub
    res_url = client.get("/api/v1/calendar/google/auth-url")
    assert res_url.status_code == 200
    assert "status" in res_url.json()

    # Test OAuth callback stub
    res_cb = client.post("/api/v1/calendar/google/callback?code=mock_code")
    assert res_cb.status_code == 200
    assert "status" in res_cb.json()

    # Test manual Google Calendar sync trigger stub
    res_sync = client.post("/api/v1/calendar/sync/google")
    assert res_sync.status_code == 200
    assert "synced_count" in res_sync.json() or "syncedCount" in res_sync.json()
