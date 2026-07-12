import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models import DbProcess, DbTimeSlice, DbAnalytics
from analytics_system.services.analytics_service import AnalyticsService
from scheduling_system.models.time_slice import SliceStatus

@pytest.fixture
def db_session():
    # In-memory database for testing
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_focus_streak_calculation(db_session):
    service = AnalyticsService(db_session)
    now = datetime.utcnow()

    # 1. 0 streak
    assert service.get_focus_streak() == 0

    # 2. Add completed sessions for today and yesterday
    slice_today = DbTimeSlice(
        id="s1", process_id="p1", start_time=now, end_time=now + timedelta(hours=2),
        duration_hours=2.0, status="Completed"
    )
    slice_yesterday = DbTimeSlice(
        id="s2", process_id="p1", start_time=now - timedelta(days=1), end_time=now - timedelta(days=1) + timedelta(hours=1),
        duration_hours=1.0, status="Completed"
    )
    db_session.add(slice_today)
    db_session.add(slice_yesterday)
    db_session.commit()

    assert service.get_focus_streak() == 2

def test_weekly_focus_hours_aggregation(db_session):
    service = AnalyticsService(db_session)
    now = datetime.utcnow()

    # Add focus sessions
    s1 = DbTimeSlice(
        id="s1", process_id="p1", start_time=now, end_time=now + timedelta(hours=2),
        duration_hours=2.5, status="Completed"
    )
    s2 = DbTimeSlice(
        id="s2", process_id="p1", start_time=now - timedelta(days=2), end_time=now - timedelta(days=2) + timedelta(hours=1),
        duration_hours=1.5, status="Completed"
    )
    db_session.add(s1)
    db_session.add(s2)
    db_session.commit()

    weekly_hours = service.get_weekly_focus_hours()
    assert len(weekly_hours) == 7
    # Sum of hours should equal 4.0
    total_hours = sum(entry.hours for entry in weekly_hours)
    assert total_hours == 4.0

def test_refresh_analytics_table(db_session):
    service = AnalyticsService(db_session)
    now = datetime.utcnow()

    # Create process
    proc = DbProcess(
        id="p1",
        name="Project A",
        deadline=now + timedelta(days=5),
        estimated_effort_hours=10.0,
        remaining_effort_hours=5.0,
        status="Active",
        health_score=85.0
    )
    db_session.add(proc)
    db_session.commit()

    # Refresh
    metrics = service.refresh_analytics()
    assert len(metrics) == 1
    assert metrics[0].process_id == "p1"
    assert metrics[0].process_health == 85.0
    assert metrics[0].health_status == "Good"

    # Query DbAnalytics from table directly to ensure it was saved
    db_row = db_session.query(DbAnalytics).filter(DbAnalytics.process_id == "p1").first()
    assert db_row is not None
    assert db_row.process_health == 85.0
    assert db_row.health_status == "Good"
