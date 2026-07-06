import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from scheduling_system.models.process import Process, ProcessLifecycle
from scheduling_system.models.time_slice import TimeSlice, SliceStatus
from scheduling_system.models.execution_plan import ExecutionPlan, ExecutionWindow

def test_process_validation_success():
    p = Process(
        id="p1",
        name="Test",
        deadline=datetime.now(timezone.utc),
        estimated_effort_hours=5.0,
        remaining_effort_hours=2.0,
        priority=3
    )
    assert p.id == "p1"
    assert p.status == ProcessLifecycle.CREATED
    assert p.priority == 3

def test_process_validation_out_of_bounds_priority():
    with pytest.raises(ValidationError):
        Process(
            id="p1",
            name="Test",
            deadline=datetime.now(timezone.utc),
            estimated_effort_hours=5.0,
            remaining_effort_hours=2.0,
            priority=6  # Invalid: ge=1, le=5
        )

def test_process_validation_negative_effort():
    with pytest.raises(ValidationError):
        Process(
            id="p1",
            name="Test",
            deadline=datetime.now(timezone.utc),
            estimated_effort_hours=-1.0,  # Invalid: gt=0
            remaining_effort_hours=2.0,
            priority=3
        )

def test_time_slice_model():
    t = TimeSlice(
        id="s1",
        process_id="p1",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        duration_hours=2.0,
        status=SliceStatus.SCHEDULED
    )
    assert t.id == "s1"
    assert t.status == SliceStatus.SCHEDULED

def test_execution_plan_model():
    t = TimeSlice(
        id="s1",
        process_id="p1",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        duration_hours=2.0,
        status=SliceStatus.SCHEDULED
    )
    w = ExecutionWindow(id="w1", time_slice=t)
    plan = ExecutionPlan(
        id="plan1",
        policy_name="Round Robin",
        time_quantum_hours=1.5,
        execution_windows=[w]
    )
    assert plan.id == "plan1"
    assert len(plan.execution_windows) == 1
    assert plan.execution_windows[0].time_slice.id == "s1"
