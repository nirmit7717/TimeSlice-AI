import pytest
from datetime import datetime, timezone, timedelta
from scheduling_system.services.scheduling_service import SchedulingService
from scheduling_system.models.process import Process, ProcessLifecycle

def test_service_generate_plan(mock_processes):
    service = SchedulingService()
    
    calendar = {"blocked_intervals": []}
    preferences = {
        "max_daily_hours": 8.0,
        "quantum_hours": 2.0,
        "available_hours": 6.0
    }
    
    plan = service.generate_execution_plan(
        processes=mock_processes,
        calendar=calendar,
        preferences=preferences,
        policy_name="Round Robin"
    )
    
    assert plan.policy_name == "Round Robin"
    assert len(plan.execution_windows) == 3

def test_service_simulate_policy(mock_processes):
    service = SchedulingService()
    
    constraints = {
        "blocked_intervals": [],
        "quantum_hours": 2.0,
        "available_hours": 6.0
    }
    
    sim_result = service.simulate_policy(
        policy_name="Priority",
        processes=mock_processes,
        constraints=constraints
    )
    
    assert sim_result["policy_name"] == "Priority"
    assert sim_result["total_slices"] == 3
    assert sim_result["context_switches"] == 1

def test_service_compute_metrics():
    service = SchedulingService()
    now = datetime.now(timezone.utc)
    
    p = Process(
        id="test-p", name="Test", deadline=now + timedelta(days=2),
        estimated_effort_hours=10.0, remaining_effort_hours=4.0, priority=3
    )
    
    # 5 days neglected, 2 consecutive completed slices, 100% checklist rate
    last_slice_dates = {"test-p": now - timedelta(days=5)}
    history_stats = {"test-p": {"consecutive_completed": 2, "checklist_completion_rate": 1.0}}
    
    updated_procs = service.compute_metrics([p], last_slice_dates, history_stats)
    assert len(updated_procs) == 1
    
    updated_p = updated_procs[0]
    # debt: 5 * 1 * 0.4 = 2.0
    # equity: 2 * 3.0 + 1 * 10 = 16.0
    # health: 100 - (2 * 2.5) + (16.0 * 0.20) = 100 - 5.0 + 3.2 = 98.2
    assert updated_p.attention_debt == 2.0
    assert updated_p.attention_equity == 16.0
    assert updated_p.health_score == 98.2
