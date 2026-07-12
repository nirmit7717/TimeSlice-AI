import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.dependencies import get_db
from database.connection import Base

TEST_DB_URL = "sqlite:///w:/Projects Antigravity/TimeSlice AI/test_adaptive.db"
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
        os.remove("w:/Projects Antigravity/TimeSlice AI/test_adaptive.db")
    except OSError:
        pass


def test_adaptive_intelligence_endpoints():
    # 1. Get initial adaptive profile
    res_prof = client.get("/api/v1/adaptive/profile")
    assert res_prof.status_code == 200
    prof = res_prof.json()
    assert "preferred_policy" in prof
    assert "preferred_quantum_hours" in prof

    # 2. Put profile overrides
    override_payload = {
        "preferred_policy": "priority",
        "preferred_quantum_hours": 3.0,
        "working_hours_start": 8,
        "working_hours_end": 18,
        "max_daily_hours": 7.5,
        "telegram_chat_id": "999888",
        "telegram_connected": True,
        "local_notifications": True
    }
    res_override = client.put("/api/v1/adaptive/profile", json=override_payload)
    assert res_override.status_code == 200
    updated_prof = res_override.json()
    assert updated_prof["preferred_policy"] == "priority"
    assert updated_prof["preferred_quantum_hours"] == 3.0
    assert updated_prof["working_hours_start"] == 8
    assert updated_prof["working_hours_end"] == 18
    assert updated_prof["max_daily_hours"] == 7.5
    assert updated_prof["telegram_chat_id"] == "999888"
    assert updated_prof["telegram_connected"] is True
    assert updated_prof["local_notifications"] is True

    # 3. Get operator behavioral model stats
    res_model = client.get("/api/v1/adaptive/operator-model")
    assert res_model.status_code == 200
    om = res_model.json()
    assert "focus_duration_avg" in om
    assert "switch_tolerance" in om
    assert "consistency_score" in om

    # 4. Get contextual bandit policy/quantum recommendation
    res_rec = client.get("/api/v1/adaptive/recommendation")
    assert res_rec.status_code == 200
    rec = res_rec.json()
    assert "recommended_policy" in rec
    assert "recommended_quantum_hours" in rec
    assert "confidence" in rec
    assert "reason" in rec
