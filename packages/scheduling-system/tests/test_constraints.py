import pytest
from datetime import datetime, timedelta, timezone
from scheduling_system.models.process import Process, ProcessLifecycle
from scheduling_system.models.time_slice import TimeSlice
from scheduling_system.models.execution_plan import ExecutionPlan, ExecutionWindow
from scheduling_system.constraints.constraint_engine import (
    CalendarBlockageConstraint,
    ProcessDependencyConstraint,
    MaxDailyHoursConstraint,
    ConstraintEngine
)

def test_calendar_blockage_constraint():
    constraint = CalendarBlockageConstraint()
    now = datetime.now(timezone.utc)
    
    # 1. Non-overlapping slice
    ts1 = TimeSlice(
        id="s1", process_id="p1",
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
        duration_hours=2.0
    )
    # Blocked event is from now to now+30m
    context = {"blocked_intervals": [(now, now + timedelta(minutes=30))]}
    assert constraint.validate_slice(ts1, context) is True

    # 2. Overlapping slice
    ts2 = TimeSlice(
        id="s2", process_id="p1",
        start_time=now + timedelta(minutes=15),
        end_time=now + timedelta(hours=2),
        duration_hours=1.75
    )
    assert constraint.validate_slice(ts2, context) is False

def test_process_dependency_constraint():
    constraint = ProcessDependencyConstraint()
    
    procs = [
        Process(id="dep-1", name="Dependency", deadline=datetime.now(timezone.utc), estimated_effort_hours=2, remaining_effort_hours=2.0, status=ProcessLifecycle.ACTIVE),
        Process(id="target-1", name="Target", deadline=datetime.now(timezone.utc), estimated_effort_hours=2, remaining_effort_hours=2.0, dependency_ids=["dep-1"])
    ]
    context = {"processes": procs}
    
    ts = TimeSlice(id="s1", process_id="target-1", start_time=datetime.now(timezone.utc), end_time=datetime.now(timezone.utc), duration_hours=2.0)
    
    # Target-1 depends on dep-1 which has remaining effort (incomplete) -> invalid!
    assert constraint.validate_slice(ts, context) is False

    # Mark dependency as completed (0 remaining effort)
    procs[0].remaining_effort_hours = 0.0
    procs[0].status = ProcessLifecycle.COMPLETED
    assert constraint.validate_slice(ts, context) is True

def test_max_daily_hours_constraint():
    constraint = MaxDailyHoursConstraint()
    now = datetime.now(timezone.utc)
    
    ts1 = TimeSlice(id="s1", process_id="p1", start_time=now, end_time=now + timedelta(hours=5), duration_hours=5.0)
    ts2 = TimeSlice(id="s2", process_id="p2", start_time=now + timedelta(hours=5), end_time=now + timedelta(hours=9), duration_hours=4.0)
    
    w1 = ExecutionWindow(id="w1", time_slice=ts1)
    w2 = ExecutionWindow(id="w2", time_slice=ts2)
    plan = ExecutionPlan(id="plan1", policy_name="Priority", time_quantum_hours=2.0, execution_windows=[w1, w2])
    
    # Sum is 9.0 hours on the same day. Max daily limit is 8.0 -> invalid!
    context = {"max_daily_hours": 8.0}
    assert constraint.validate_plan(plan, context) is False
    
    # Increase capacity limit to 10.0 -> valid
    context = {"max_daily_hours": 10.0}
    assert constraint.validate_plan(plan, context) is True

def test_constraint_engine(mock_processes):
    engine = ConstraintEngine()
    now = datetime.now(timezone.utc)
    
    ts = TimeSlice(
        id="s1", process_id="p1",
        start_time=now + timedelta(minutes=15),
        end_time=now + timedelta(hours=2),
        duration_hours=1.75
    )
    
    # Set calendar blockage that overlaps
    context = {
        "processes": mock_processes,
        "blocked_intervals": [(now, now + timedelta(hours=1))],
        "max_daily_hours": 8.0
    }
    
    violations = engine.validate_slice(ts, context)
    assert "Calendar Blockage" in violations
