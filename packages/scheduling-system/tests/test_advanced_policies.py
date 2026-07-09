import pytest
from datetime import datetime, timedelta, timezone
from scheduling_system.policy.sjf import ShortestJobFirstPolicy
from scheduling_system.policy.edf import EarliestDeadlineFirstPolicy

def test_sjf_policy(mock_processes):
    policy = ShortestJobFirstPolicy()
    assert policy.name == "Shortest Job First"

    # mock_processes: 
    # p1 (rem: 4 hrs, pri: 4)
    # p2 (rem: 6 hrs, pri: 2)
    # SJF sorts by remaining effort ascending (p1 then p2)
    # Available: 4.0 hrs, Quantum: 2.0 hrs
    slices = policy.generate_slices(mock_processes, quantum_hours=2.0, available_hours=4.0)

    assert len(slices) == 2
    # p1 is shorter (4.0 hrs) and gets scheduled first
    assert slices[0].process_id == "p1"
    assert slices[1].process_id == "p1"

def test_edf_policy(mock_processes, base_deadline):
    policy = EarliestDeadlineFirstPolicy()
    assert policy.name == "Earliest Deadline First"

    # We make p2 have an earlier deadline than p1
    mock_processes[0].deadline = base_deadline + timedelta(days=2) # p1 deadline
    mock_processes[1].deadline = base_deadline + timedelta(days=1) # p2 deadline (earliest)
    
    # EDF sorts by deadline ascending (p2 then p1)
    # Available: 4.0 hrs, Quantum: 2.0 hrs
    slices = policy.generate_slices(mock_processes, quantum_hours=2.0, available_hours=4.0)

    assert len(slices) == 2
    # p2 has the earliest deadline and gets scheduled first
    assert slices[0].process_id == "p2"
    assert slices[1].process_id == "p2"
