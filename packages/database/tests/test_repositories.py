import pytest
from datetime import datetime, timedelta, timezone
from database.repositories.process_repo import ProcessRepository
from database.repositories.slice_repo import TimeSliceRepository
from scheduling_system.models.time_slice import TimeSlice, SliceStatus

def test_process_repository_crud(db_session, sample_process_domain):
    repo = ProcessRepository(db_session)
    
    # 1. Create Process
    created = repo.create(sample_process_domain)
    assert created.id == "test-p1"
    assert created.name == "Build SQLite Persistence"
    assert created.tags == ["database", "backend"]
    
    # 2. Get Process
    fetched = repo.get("test-p1")
    assert fetched is not None
    assert fetched.id == "test-p1"
    assert fetched.priority == 4
    
    # 3. Update Process
    fetched.remaining_effort_hours = 4.0
    fetched.progress = 0.5
    fetched.tags.append("sqlite")
    updated = repo.update(fetched)
    assert updated.remaining_effort_hours == 4.0
    assert updated.progress == 0.5
    assert "sqlite" in updated.tags
    
    # 4. List Processes
    all_procs = repo.list()
    assert len(all_procs) == 1
    assert all_procs[0].id == "test-p1"
    
    # 5. Delete Process
    deleted = repo.delete("test-p1")
    assert deleted is True
    
    # Verify it is gone
    assert repo.get("test-p1") is None

def test_timeslice_repository_crud(db_session, sample_process_domain):
    process_repo = ProcessRepository(db_session)
    slice_repo = TimeSliceRepository(db_session)
    
    # Create parent process
    process_repo.create(sample_process_domain)
    
    # 1. Create TimeSlice
    now = datetime.now(timezone.utc)
    ts = TimeSlice(
        id="slice-1",
        process_id="test-p1",
        start_time=now,
        end_time=now + timedelta(hours=2),
        duration_hours=2.0,
        status=SliceStatus.SCHEDULED,
        progress_gained=0.25
    )
    created_ts = slice_repo.create(ts)
    assert created_ts.id == "slice-1"
    assert created_ts.process_id == "test-p1"
    assert created_ts.duration_hours == 2.0
    
    # 2. Get TimeSlice
    fetched_ts = slice_repo.get("slice-1")
    assert fetched_ts is not None
    assert fetched_ts.id == "slice-1"
    
    # 3. List slices by process
    slices_for_p = slice_repo.list_by_process("test-p1")
    assert len(slices_for_p) == 1
    assert slices_for_p[0].id == "slice-1"
    
    # 4. Update TimeSlice status
    fetched_ts.status = SliceStatus.COMPLETED
    fetched_ts.reflection = "Worked well"
    updated_ts = slice_repo.update(fetched_ts)
    assert updated_ts.status == SliceStatus.COMPLETED
    assert updated_ts.reflection == "Worked well"

def test_cascade_delete_time_slice(db_session, sample_process_domain):
    process_repo = ProcessRepository(db_session)
    slice_repo = TimeSliceRepository(db_session)
    
    # Create parent process and time slice
    process_repo.create(sample_process_domain)
    now = datetime.now(timezone.utc)
    ts = TimeSlice(
        id="slice-cascade",
        process_id="test-p1",
        start_time=now,
        end_time=now + timedelta(hours=1),
        duration_hours=1.0,
        status=SliceStatus.SCHEDULED
    )
    slice_repo.create(ts)
    
    # Ensure slice is created
    assert slice_repo.get("slice-cascade") is not None
    
    # Delete parent process
    process_repo.delete("test-p1")
    
    # Verify that the associated time slice is cascade deleted
    assert slice_repo.get("slice-cascade") is None
