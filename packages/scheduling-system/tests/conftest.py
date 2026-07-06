import pytest
from datetime import datetime, timedelta, timezone
from scheduling_system.models.process import Process, ProcessLifecycle

@pytest.fixture
def base_deadline():
    return datetime.now(timezone.utc) + timedelta(days=5)

@pytest.fixture
def mock_processes(base_deadline):
    return [
        Process(
            id="p1",
            name="Write Code",
            description="Write scheduler logic",
            goal="Complete Sprint 1",
            priority=4,
            deadline=base_deadline,
            estimated_effort_hours=10.0,
            remaining_effort_hours=4.0,
            status=ProcessLifecycle.ACTIVE,
            tags=["dev", "scheduler"],
            attention_debt=1.5
        ),
        Process(
            id="p2",
            name="Design Database",
            description="Sketch SQLite models",
            goal="Complete Phase 2",
            priority=2,
            deadline=base_deadline + timedelta(days=2),
            estimated_effort_hours=6.0,
            remaining_effort_hours=6.0,
            status=ProcessLifecycle.CREATED,
            tags=["design", "db"],
            attention_debt=0.0
        ),
        Process(
            id="p3",
            name="Deploy Server",
            description="Configure Docker",
            goal="Go Live",
            priority=5,
            deadline=base_deadline + timedelta(days=1),
            estimated_effort_hours=4.0,
            remaining_effort_hours=0.0,
            status=ProcessLifecycle.COMPLETED,
            tags=["devops", "cloud"]
        )
    ]
