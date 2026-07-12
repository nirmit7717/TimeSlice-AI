import pytest
import time
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.dependencies import get_db
from database.connection import Base
from database.models import DbProcess

TEST_DB_URL = "sqlite:///w:/Projects Antigravity/TimeSlice AI/test_perf.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    import os
    try:
        os.remove("w:/Projects Antigravity/TimeSlice AI/test_perf.db")
    except OSError:
        pass


def test_schedule_generation_performance():
    """
    Validate that schedule generation takes <= 1 second for 100 active processes.
    """
    db = TestingSessionLocal()
    deadline = datetime.now(timezone.utc) + timedelta(days=5)
    
    # 1. Bulk insert 100 active processes
    processes = []
    for i in range(100):
        processes.append(DbProcess(
            id=f"perf-proc-{i}",
            name=f"Performance Test Process {i}",
            description="Stress test process",
            goal="Ensure performance limits",
            priority=(i % 5) + 1,
            deadline=deadline,
            estimated_effort_hours=4.0,
            remaining_effort_hours=4.0,
            status="Active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ))
    db.bulk_save_objects(processes)
    db.commit()
    db.close()

    # 2. Trigger recomputation (which runs the scheduling algorithm)
    start_time = time.perf_counter()
    res = client.post("/api/v1/scheduler/recompute?policy_name=Priority&quantum_hours=2.0&available_hours=16.0")
    end_time = time.perf_counter()
    
    elapsed = end_time - start_time
    assert res.status_code == 200
    print(f"\n[Performance Profile] 100 processes reschedule took: {elapsed:.4f} seconds")
    # Assert schedule generation <= 1.0 second
    assert elapsed <= 1.0


def test_ai_response_overhead_performance():
    """
    Validate that AI framework response overhead (excluding LLM network latency) is <= 5 seconds.
    We run with mock LLM path by ensuring ChatOpenAI is mocked or not called.
    """
    payload = {
        "message": "Verify framework overhead",
        "history": []
    }
    
    start_time = time.perf_counter()
    res = client.post("/api/v1/chat", json=payload)
    end_time = time.perf_counter()
    
    elapsed = end_time - start_time
    assert res.status_code == 200
    print(f"\n[Performance Profile] Chat router execution took: {elapsed:.4f} seconds")
    # Assert framework overhead <= 5.0 seconds
    assert elapsed <= 5.0


def test_health_check_performance():
    """
    Validate that health checking / ping queries complete in <= 100ms (0.1s).
    """
    latencies = []
    
    for _ in range(5):
        start_time = time.perf_counter()
        res = client.get("/health")
        end_time = time.perf_counter()
        assert res.status_code == 200
        latencies.append(end_time - start_time)
        
    avg_latency = sum(latencies) / len(latencies)
    print(f"\n[Performance Profile] Average health endpoint latency: {avg_latency * 1000:.2f} ms")
    # Assert average latency <= 100ms (0.1s)
    assert avg_latency <= 0.1
