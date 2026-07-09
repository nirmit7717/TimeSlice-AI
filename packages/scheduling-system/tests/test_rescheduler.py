import pytest
from datetime import datetime, timedelta, timezone
from scheduling_system.models.time_slice import TimeSlice
from scheduling_system.models.execution_plan import ExecutionPlan, ExecutionWindow
from scheduling_system.rescheduler.dynamic_rescheduler import DynamicRescheduler
from scheduling_system.rescheduler.impact_analyzer import ImpactAnalyzer

def test_impact_analyzer():
    analyzer = ImpactAnalyzer()
    now = datetime.now(timezone.utc)
    
    # Original Plan
    ts1 = TimeSlice(id="s1", process_id="p1", start_time=now, end_time=now + timedelta(hours=2), duration_hours=2.0)
    ts2 = TimeSlice(id="s2", process_id="p2", start_time=now + timedelta(hours=2), end_time=now + timedelta(hours=4), duration_hours=2.0)
    w1 = ExecutionWindow(id="w1", time_slice=ts1)
    w2 = ExecutionWindow(id="w2", time_slice=ts2)
    plan1 = ExecutionPlan(id="plan1", policy_name="Priority", time_quantum_hours=2.0, execution_windows=[w1, w2])
    
    # Updated Plan: Shift ts2 by 1 hour
    ts2_shifted = TimeSlice(id="s2", process_id="p2", start_time=now + timedelta(hours=3), end_time=now + timedelta(hours=5), duration_hours=2.0)
    w1_upd = ExecutionWindow(id="w1", time_slice=ts1)
    w2_upd = ExecutionWindow(id="w2", time_slice=ts2_shifted)
    plan2 = ExecutionPlan(id="plan2", policy_name="Priority", time_quantum_hours=2.0, execution_windows=[w1_upd, w2_upd])
    
    impact = analyzer.analyze_impact(plan1, plan2)
    assert impact["shifted_windows_count"] == 1
    assert impact["total_delay_hours"] == 1.0
    assert impact["max_individual_delay_hours"] == 1.0
    assert impact["context_switches_diff"] == 0

def test_dynamic_rescheduler():
    rescheduler = DynamicRescheduler()
    now = datetime.now(timezone.utc)
    
    # Schedule: s1 (10 AM to 12 PM), s2 (12 PM to 2 PM)
    s1_start = now.replace(hour=10, minute=0, second=0, microsecond=0)
    ts1 = TimeSlice(id="s1", process_id="p1", start_time=s1_start, end_time=s1_start + timedelta(hours=2), duration_hours=2.0)
    ts2 = TimeSlice(id="s2", process_id="p2", start_time=s1_start + timedelta(hours=2), end_time=s1_start + timedelta(hours=4), duration_hours=2.0)
    
    w1 = ExecutionWindow(id="w1", time_slice=ts1)
    w2 = ExecutionWindow(id="w2", time_slice=ts2)
    plan = ExecutionPlan(id="plan1", policy_name="Priority", time_quantum_hours=2.0, execution_windows=[w1, w2])
    
    # Event: Interruption from 11 AM to 12 PM (overlaps with s1)
    event = {
        "event_type": "Calendar Interrupt",
        "start_time": s1_start + timedelta(hours=1),
        "end_time": s1_start + timedelta(hours=2)
    }
    
    context = {"blocked_intervals": []}
    
    new_plan = rescheduler.reschedule(plan, event, context)
    new_windows = new_plan.execution_windows
    
    assert len(new_windows) == 2
    # s1 (starts at 10 AM, overlaps with 11 AM, so it gets shifted to end of block = 12 PM!)
    # And then s2 gets pushed to 2 PM to avoid overlapping with shifted s1!
    assert new_windows[0].time_slice.id == "s1"
    assert new_windows[0].time_slice.start_time == s1_start + timedelta(hours=2) # Pushed past event end
    
    assert new_windows[1].time_slice.id == "s2"
    assert new_windows[1].time_slice.start_time == s1_start + timedelta(hours=4) # Cascade pushed
