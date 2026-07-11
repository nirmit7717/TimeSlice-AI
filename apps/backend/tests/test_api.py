import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.dependencies import get_db, get_vector_store
from database.connection import Base
from database.models import DbProcess, DbTimeSlice, DbTransaction
from database.vector.vector_store import VectorStoreClient

TEST_DB_URL = "sqlite:///w:/Projects Antigravity/TimeSlice AI/test_local.db"

# 1. Setup isolated test database on disk
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Setup isolated in-memory Chroma client for API tests
test_vector_store = VectorStoreClient() # Ephemeral by default
def override_get_vector_store():
    return test_vector_store

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_vector_store] = override_get_vector_store

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    # Re-create tables to clean state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    test_vector_store.clear_all()
    yield
    # Cleanup file database after test run
    Base.metadata.drop_all(bind=engine)
    import os
    try:
        os.remove("w:/Projects Antigravity/TimeSlice AI/test_local.db")
    except OSError:
        pass


def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_process_crud_api():
    # 1. Create process (using camelCase payload)
    deadline = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    payload = {
        "name": "Integration Test API",
        "description": "Ensure API works with frontend",
        "goal": "Verify CRUD endpoints",
        "priority": 5,
        "deadline": deadline,
        "estimatedEffortHours": 8.0,
        "status": "Active",
        "tags": ["test", "fastapi"]
    }
    
    res = client.post("/api/v1/processes", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Integration Test API"
    assert "id" in data
    # Verify camelCase serialization outputs
    assert "estimatedEffortHours" in data
    assert data["estimatedEffortHours"] == 8.0
    assert "remainingEffortHours" in data
    assert data["remainingEffortHours"] == 8.0
    assert "attentionDebt" in data
    
    pid = data["id"]

    # 2. Get process list
    res_list = client.get("/api/v1/processes")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1
    assert res_list.json()[0]["id"] == pid

    # 3. Update process
    update_payload = {
        "remainingEffortHours": 4.0,
        "progress": 0.5
    }
    res_upd = client.put(f"/api/v1/processes/{pid}", json=update_payload)
    assert res_upd.status_code == 200
    assert res_upd.json()["remainingEffortHours"] == 4.0
    assert res_upd.json()["progress"] == 0.5

    # 4. Search process context in vault
    search_payload = {"queryText": "Integration API", "nResults": 1}
    res_search = client.post("/api/v1/vault/search", json=search_payload)
    assert res_search.status_code == 200
    assert len(res_search.json()) == 1
    assert res_search.json()[0]["id"] == pid

    # 5. Delete process
    res_del = client.delete(f"/api/v1/processes/{pid}")
    assert res_del.status_code == 204
    
    # Confirm it is gone
    res_get = client.get(f"/api/v1/processes/{pid}")
    assert res_get.status_code == 404

def test_scheduler_endpoints():
    # Create some mock processes in DB first
    deadline = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    client.post("/api/v1/processes", json={
        "name": "Process Alpha",
        "priority": 4,
        "deadline": deadline,
        "estimatedEffortHours": 4.0
    })
    client.post("/api/v1/processes", json={
        "name": "Process Beta",
        "priority": 2,
        "deadline": deadline,
        "estimatedEffortHours": 6.0
    })

    # Generate plan
    plan_payload = {
        "policyName": "Priority",
        "availableHours": 8.0,
        "quantumHours": 2.0,
        "blockedIntervals": []
    }
    res = client.post("/api/v1/scheduler/plan", json=plan_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["policyName"] == "Priority"
    # Available hours is 8.0, quantum is 2.0. So we should get 4 windows (2.0 hours each)
    assert len(data["executionWindows"]) == 4
    
    # Test metrics recalculation
    res_metrics = client.get("/api/v1/scheduler/metrics")
    assert res_metrics.status_code == 200
    procs = res_metrics.json()
    assert len(procs) == 2
    # Verify health score was updated
    assert "healthScore" in procs[0]
    assert procs[0]["healthScore"] > 0


def test_chat_endpoint():
    payload = {
        "message": "Add a new process project for writing unit tests.",
        "history": []
    }
    res = client.post("/api/v1/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "messages" in data
    assert len(data["messages"]) > 0
    assert data["currentProcess"] is not None
    assert data["currentProcess"]["name"] == "Extracted Process Task"


def test_sync_endpoints():
    # 1. Create a process -> Writes an unsynced sync log atomically
    deadline = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    client.post("/api/v1/processes", json={
        "name": "Sync Process",
        "priority": 3,
        "deadline": deadline,
        "estimatedEffortHours": 5.0
    })

    # 2. Get pending logs
    res_pending = client.get("/api/v1/sync/pending")
    assert res_pending.status_code == 200
    logs = res_pending.json()
    assert len(logs) == 1
    assert logs[0]["action"] == "INSERT"
    assert logs[0]["tableName"] == "processes"

    # 3. Trigger manual sync
    trigger_payload = {"cloudEndpoint": "mock-cloud-endpoint"}
    res_trigger = client.post("/api/v1/sync/trigger", json=trigger_payload)
    assert res_trigger.status_code == 200
    assert res_trigger.json()["syncedCount"] == 1

    # 4. Pending logs should be 0 now
    res_check = client.get("/api/v1/sync/pending")
    assert len(res_check.json()) == 0


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "timestamp" in data


