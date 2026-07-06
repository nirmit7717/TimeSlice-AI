import pytest
from datetime import datetime, timedelta, timezone
from scheduling_system.models.process import Process, ProcessLifecycle
from scheduling_system.analyzer.process_analyzer import ProcessAnalyzer

def test_validate_processes(mock_processes):
    analyzer = ProcessAnalyzer()
    active_procs = analyzer.validate_processes(mock_processes)
    
    # Check that completed processes (p3) are filtered out
    assert len(active_procs) == 2
    assert "p1" in [p.id for p in active_procs]
    assert "p2" in [p.id for p in active_procs]
    assert "p3" not in [p.id for p in active_procs]

def test_validate_processes_invalid_effort(mock_processes):
    analyzer = ProcessAnalyzer()
    
    # Set remaining > estimated
    mock_processes[0].remaining_effort_hours = 12.0
    with pytest.raises(ValueError, match="remaining effort exceeds"):
        analyzer.validate_processes(mock_processes)

def test_estimate_total_workload(mock_processes):
    analyzer = ProcessAnalyzer()
    
    # Available hours = 20.0
    metrics = analyzer.estimate_total_workload(mock_processes, available_hours=20.0)
    
    # Active are p1 (4.0 remaining) and p2 (6.0 remaining) = 10.0 total remaining
    assert metrics["total_remaining_hours"] == 10.0
    assert metrics["total_estimated_hours"] == 16.0  # p1 (10) + p2 (6)
    assert metrics["total_attention_debt"] == 1.5
    assert metrics["average_priority"] == 3.0  # (4 + 2) / 2
    assert metrics["feasibility_ratio"] == 0.5  # 10.0 / 20.0
    assert len(metrics["bottlenecks"]) == 0  # Deadlines are far enough in mock

def test_bottleneck_detection(base_deadline):
    analyzer = ProcessAnalyzer()
    
    # Set remaining effort to exceed available time before deadline
    p = Process(
        id="b1",
        name="Bottleneck Process",
        deadline=datetime.now(timezone.utc) + timedelta(hours=2),
        estimated_effort_hours=10.0,
        remaining_effort_hours=5.0,  # 5 hours needed, but only 2 hours left
        status=ProcessLifecycle.ACTIVE
    )
    
    metrics = analyzer.estimate_total_workload([p], available_hours=10.0)
    assert len(metrics["bottlenecks"]) == 1
    assert metrics["bottlenecks"][0]["process_id"] == "b1"
    assert metrics["bottlenecks"][0]["deficit_hours"] > 0

def test_detect_dependencies_no_cycle(mock_processes):
    analyzer = ProcessAnalyzer()
    
    # Create dependency: p2 depends on p1
    mock_processes[1].dependency_ids = ["p1"]
    
    adj_list = analyzer.detect_dependencies(mock_processes)
    assert adj_list["p2"] == ["p1"]
    assert adj_list["p1"] == []

def test_detect_dependencies_cycle(mock_processes):
    analyzer = ProcessAnalyzer()
    
    # Create circular dependency: p1 -> p2 -> p1
    mock_processes[0].dependency_ids = ["p2"]
    mock_processes[1].dependency_ids = ["p1"]
    
    with pytest.raises(ValueError, match="Circular dependency detected"):
        analyzer.detect_dependencies(mock_processes)

def test_compute_scheduling_metadata(mock_processes):
    analyzer = ProcessAnalyzer()
    
    metadata = analyzer.compute_scheduling_metadata(mock_processes)
    # p3 is completed but included in raw metadata check
    assert len(metadata) == 3
    
    # Sort check: highest urgency score is first
    assert metadata[0]["urgency_score"] >= metadata[1]["urgency_score"]
