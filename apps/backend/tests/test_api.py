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

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_vector_store] = override_get_vector_store
    # Re-create tables to clean state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    test_vector_store.clear_all()
    yield
    app.dependency_overrides.clear()
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
    assert len(logs) >= 1
    assert any(l["action"] == "INSERT" and l["tableName"] == "processes" for l in logs)

    # 3. Trigger manual sync
    trigger_payload = {"cloudEndpoint": "mock-cloud-endpoint"}
    res_trigger = client.post("/api/v1/sync/trigger", json=trigger_payload)
    assert res_trigger.status_code == 200
    assert res_trigger.json()["syncedCount"] == len(logs)

    # 4. Pending logs should be 0 now
    res_check = client.get("/api/v1/sync/pending")
    assert len(res_check.json()) == 0

    # 5. Create a new process and modify it locally to set up a conflict on pull
    res_proc = client.post("/api/v1/processes", json={
        "name": "Sync Conflict Proc",
        "priority": 3,
        "deadline": deadline,
        "estimatedEffortHours": 2.0
    })
    pid = res_proc.json()["id"]

    # Modify locally
    client.put(f"/api/v1/processes/{pid}", json={"name": "Locally Modified Name"})

    # Pull conflicting cloud records
    cloud_records_payload = {
        "cloudRecords": [
            {
                "tableName": "processes",
                "recordId": pid,
                "updatedAt": datetime.now(timezone.utc).isoformat(),
                "payload": {
                    "name": "Cloud Winning Name",
                    "description": "Cloud desc",
                    "status": "Active",
                    "progress": 0.0
                }
            }
        ]
    }
    res_pull = client.post("/api/v1/sync/pull", json=cloud_records_payload)
    assert res_pull.status_code == 200
    conflicts = res_pull.json()
    assert len(conflicts) == 1
    assert conflicts[0]["recordId"] == pid
    assert conflicts[0]["localValue"] == "Locally Modified Name"
    assert conflicts[0]["cloudValue"] == "Cloud Winning Name"

    # 6. Verify status shows conflicts
    res_status = client.get("/api/v1/sync/status")
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert status_data["conflictCount"] == 1
    assert status_data["pendingCount"] > 0

    # Verify conflicts endpoint lists them
    res_conflicts = client.get("/api/v1/sync/conflicts")
    assert len(res_conflicts.json()) == 1

    # 7. Resolve conflict using cloud resolution
    resolve_payload = {
        "resolution": "cloud",
        "cloudPayload": cloud_records_payload["cloudRecords"][0]["payload"]
    }
    res_resolve = client.post(f"/api/v1/sync/conflicts/processes:{pid}/resolve", json=resolve_payload)
    assert res_resolve.status_code == 200
    assert res_resolve.json()["status"] == "success"

    # Confirm resolved
    res_status_after = client.get("/api/v1/sync/status")
    assert res_status_after.json()["conflictCount"] == 0
    
    # Confirm local record name is updated
    res_get_proc = client.get(f"/api/v1/processes/{pid}")
    assert res_get_proc.json()["name"] == "Cloud Winning Name"



def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "timestamp" in data


def test_analytics_endpoints():
    # 1. Create a process to analyze
    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    res_proc = client.post("/api/v1/processes", json={
        "name": "Analytics Test Proc",
        "priority": 3,
        "deadline": deadline,
        "estimatedEffortHours": 4.0
    })
    assert res_proc.status_code == 201
    pid = res_proc.json()["id"]

    # 2. Get metrics (refreshes statistics)
    res = client.get("/api/v1/analytics/metrics")
    assert res.status_code == 200
    metrics = res.json()
    assert len(metrics) > 0
    assert any(m["processId"] == pid for m in metrics)

    # 3. Get individual health
    res_health = client.get(f"/api/v1/analytics/health/{pid}")
    assert res_health.status_code == 200
    assert res_health.json()["processId"] == pid

    # 4. Get focus streak
    res_streak = client.get("/api/v1/analytics/focus-streak")
    assert res_streak.status_code == 200
    assert "streakDays" in res_streak.json()

    # 5. Get time allocation
    res_alloc = client.get("/api/v1/analytics/time-allocation")
    assert res_alloc.status_code == 200
    assert isinstance(res_alloc.json(), list)

    # 6. Get weekly summary
    res_summary = client.get("/api/v1/analytics/weekly-summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert "streakDays" in summary
    assert "weeklyHours" not in summary  # It should be weeklyFocusHours
    assert "weeklyFocusHours" in summary


def test_slices_lifecycle_api():
    # 1. Create process
    deadline = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    res_proc = client.post("/api/v1/processes", json={
        "name": "Slices Lifecycle Proc",
        "priority": 4,
        "deadline": deadline,
        "estimatedEffortHours": 10.0
    })
    pid = res_proc.json()["id"]

    # 2. Start a time slice session
    res_start = client.post("/api/v1/slices/start", json={
        "processId": pid,
        "durationHours": 1.5
    })
    assert res_start.status_code == 201
    slice_data = res_start.json()
    assert slice_data["status"] == "Active"
    assert slice_data["processId"] == pid
    sid = slice_data["id"]

    # 3. Get checklists for active slice
    res_check = client.get(f"/api/v1/slices/{sid}/checklists")
    assert res_check.status_code == 200
    checklists = res_check.json()
    assert len(checklists) > 0
    item_id = checklists[0]["id"]

    # 4. Toggle checklist item
    res_toggle = client.patch(f"/api/v1/slices/checklists/{item_id}")
    assert res_toggle.status_code == 200
    assert res_toggle.json()["completed"] is True

    # 5. Complete slice session
    res_comp = client.post(f"/api/v1/slices/{sid}/complete", json={
        "progressGained": 0.15,
        "reflection": "Completed all subtasks on time!"
    })
    assert res_comp.status_code == 200
    assert res_comp.json()["status"] == "Completed"
    assert res_comp.json()["reflection"] == "Completed all subtasks on time!"

    # 6. Verify process progress increased
    res_proc_check = client.get(f"/api/v1/processes/{pid}")
    assert res_proc_check.json()["progress"] == 0.15

    # 7. Start another session to abandon
    res_start_2 = client.post("/api/v1/slices/start", json={
        "processId": pid,
        "durationHours": 1.0
    })
    sid2 = res_start_2.json()["id"]

    # 8. Abandon slice
    res_abandon = client.post(f"/api/v1/slices/{sid2}/abandon", json={
        "reflection": "Felt tired and distracted"
    })
    assert res_abandon.status_code == 200
    assert res_abandon.json()["status"] == "Abandoned"
    assert res_abandon.json()["reflection"] == "Felt tired and distracted"



