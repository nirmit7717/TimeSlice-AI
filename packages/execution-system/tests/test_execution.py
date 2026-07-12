import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models import DbProcess, DbTimeSlice, DbChecklist
from execution_system.services.execution_service import ExecutionService
from scheduling_system.models.process import Process, ProcessLifecycle

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

def test_execution_start_and_checklist_generation(db_session):
    service = ExecutionService(db_session)

    # 1. Create a dummy process in DB
    now = datetime.now(timezone.utc)
    db_proc = DbProcess(
        id="p1",
        name="Backend Development",
        deadline=now + timedelta(days=2),
        estimated_effort_hours=10.0,
        remaining_effort_hours=10.0,
        status="Created"
    )
    db_session.add(db_proc)
    db_session.commit()

    # 2. Start a session
    time_slice = service.start_time_slice(process_id="p1", duration_hours=2.0)
    assert time_slice.status == "Active"
    assert time_slice.duration_hours == 2.0

    # 3. Check process updated status
    assert db_proc.status == "Active"

    # 4. Check generated checklists
    checklists = service.get_checklists(time_slice.id)
    assert len(checklists) == 3
    assert checklists[0].title == "Review session goals and prerequisites"
    assert checklists[0].completed is False

def test_execution_completion_progress_propagation(db_session):
    service = ExecutionService(db_session)
    now = datetime.now(timezone.utc)

    db_proc = DbProcess(
        id="p1",
        name="Backend Development",
        deadline=now + timedelta(days=2),
        estimated_effort_hours=10.0,
        remaining_effort_hours=10.0,
        status="Active",
        progress=0.0
    )
    db_session.add(db_proc)
    db_session.commit()

    # Start and complete
    ts = service.start_time_slice(process_id="p1", duration_hours=2.0)
    service.complete_time_slice(slice_id=ts.id, progress_gained=0.20, reflection="Built router endpoints")

    # Verify time slice fields
    assert ts.status == "Completed"
    assert ts.progress_gained == 0.20
    assert ts.reflection == "Built router endpoints"

    # Verify process fields updated
    assert db_proc.progress == 0.20
    # Remaining effort hours decreased by duration (10.0 - 2.0 = 8.0)
    assert db_proc.remaining_effort_hours == 8.0

def test_checklist_toggling(db_session):
    service = ExecutionService(db_session)
    now = datetime.now(timezone.utc)

    db_proc = DbProcess(
        id="p1",
        name="Test Task",
        deadline=now + timedelta(days=2),
        estimated_effort_hours=5.0,
        remaining_effort_hours=5.0
    )
    db_session.add(db_proc)
    db_session.commit()

    ts = service.start_time_slice(process_id="p1", duration_hours=1.0)
    items = service.get_checklists(ts.id)
    first_item = items[0]

    # Toggle complete
    updated_item = service.toggle_checklist_item(first_item.id)
    assert updated_item.completed is True

    # Toggle back to incomplete
    updated_item_2 = service.toggle_checklist_item(first_item.id)
    assert updated_item_2.completed is False
