import pytest
from datetime import datetime, timezone
from scheduling_system.models.process import Process, ProcessLifecycle
from scheduling_system.policy.round_robin import RoundRobinPolicy
from scheduling_system.policy.priority import PriorityPolicy
from scheduling_system.policy.policy_manager import PolicyManager

def test_round_robin_policy(mock_processes):
    policy = RoundRobinPolicy()
    assert policy.name == "Round Robin"

    # We have mock_processes: p1 (remaining 4 hrs), p2 (remaining 6 hrs), p3 (completed, remaining 0 hrs)
    # Available capacity: 6.0 hours, Quantum: 2.0 hours
    slices = policy.generate_slices(mock_processes, quantum_hours=2.0, available_hours=6.0)

    # Round Robin should alternate:
    # 1. p1: gets 2.0 hrs (rem: 2.0)
    # 2. p2: gets 2.0 hrs (rem: 4.0)
    # 3. p1: gets 2.0 hrs (rem: 0.0) -> capacity is now 6.0 hrs, should terminate!
    assert len(slices) == 3
    assert slices[0].process_id == "p1"
    assert slices[0].duration_hours == 2.0
    assert slices[1].process_id == "p2"
    assert slices[1].duration_hours == 2.0
    assert slices[2].process_id == "p1"
    assert slices[2].duration_hours == 2.0

def test_round_robin_empty():
    policy = RoundRobinPolicy()
    slices = policy.generate_slices([], quantum_hours=2.0, available_hours=5.0)
    assert len(slices) == 0

def test_priority_policy(mock_processes):
    policy = PriorityPolicy()
    assert policy.name == "Priority"

    # mock_processes: p1 (priority 4, remaining 4 hrs), p2 (priority 2, remaining 6 hrs)
    # Available capacity: 6.0 hours, Quantum: 2.0 hours
    slices = policy.generate_slices(mock_processes, quantum_hours=2.0, available_hours=6.0)

    # Priority should schedule p1 (priority 4) fully first, then p2 (priority 2):
    # 1. p1: gets 2.0 hrs (rem: 2.0)
    # 2. p1: gets 2.0 hrs (rem: 0.0)
    # 3. p2: gets 2.0 hrs (rem: 4.0) -> capacity limit 6.0 reached
    assert len(slices) == 3
    assert slices[0].process_id == "p1"
    assert slices[0].duration_hours == 2.0
    assert slices[1].process_id == "p1"
    assert slices[1].duration_hours == 2.0
    assert slices[2].process_id == "p2"
    assert slices[2].duration_hours == 2.0

def test_priority_tie_breaker(base_deadline):
    policy = PriorityPolicy()
    
    # Create two processes with priority 3, but different attention debts
    procs = [
        Process(
            id="low_debt",
            name="Low Debt",
            deadline=base_deadline,
            estimated_effort_hours=5.0,
            remaining_effort_hours=4.0,
            priority=3,
            attention_debt=1.0,
            status=ProcessLifecycle.ACTIVE
        ),
        Process(
            id="high_debt",
            name="High Debt",
            deadline=base_deadline,
            estimated_effort_hours=5.0,
            remaining_effort_hours=4.0,
            priority=3,
            attention_debt=3.5,  # Higher debt should break the tie!
            status=ProcessLifecycle.ACTIVE
        )
    ]
    
    # Available: 4.0 hrs, Quantum: 2.0 hrs
    slices = policy.generate_slices(procs, quantum_hours=2.0, available_hours=4.0)
    
    # Priority policy sorts by (priority, attention_debt) descending.
    # Therefore, high_debt gets scheduled first.
    assert len(slices) == 2
    assert slices[0].process_id == "high_debt"
    assert slices[1].process_id == "high_debt"

def test_policy_manager():
    manager = PolicyManager()
    
    # Check default registration
    policies = manager.list_policies()
    assert "Round Robin" in policies
    assert "Priority" in policies
    
    rr = manager.get_policy("round robin")
    assert isinstance(rr, RoundRobinPolicy)
    
    pri = manager.get_policy("PRIORITY")
    assert isinstance(pri, PriorityPolicy)
    
    with pytest.raises(ValueError, match="is not registered"):
        manager.get_policy("nonexistent")
