import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.dependencies import get_db
from database.connection import Base
from database.models import DbNotificationLog

TEST_DB_URL = "sqlite:///w:/Projects Antigravity/TimeSlice AI/test_notifications.db"
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
        os.remove("w:/Projects Antigravity/TimeSlice AI/test_notifications.db")
    except OSError:
        pass


def test_notification_endpoints():
    # 1. Trigger a test notification (using normal priority, desktop channel)
    payload = {
        "title": "Test Title",
        "message": "Integration test body description",
        "priority": "normal",
        "channels": ["desktop"]
    }
    
    # We expect this call to return 200 since notification dispatcher works offline-first
    # Even if plyer fails, dispatcher logs it or returns success/fail status
    res = client.post("/api/v1/notifications/test", json=payload)
    assert res.status_code == 200
    assert "status" in res.json()
    assert "delivered" in res.json()

    # 2. Get history log (limit to 10)
    res_log = client.get("/api/v1/notifications/log?limit=10")
    assert res_log.status_code == 200
    logs = res_log.json()
    assert isinstance(logs, list)
    if len(logs) > 0:
        assert logs[0]["title"] == "Test Title"
        assert logs[0]["message"] == "Integration test body description"
