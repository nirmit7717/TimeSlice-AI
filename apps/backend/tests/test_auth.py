"""Unit & integration tests for local JWT authentication."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
import database.models
from apps.backend.main import app
from app.dependencies import get_db
from app.auth import hash_password, verify_password, decode_token


@pytest.fixture
def db_session():
    import os
    import uuid
    db_id = str(uuid.uuid4())
    test_db = f"w:/Projects Antigravity/TimeSlice AI/test_timeslice_{db_id}.db"
            
    engine = create_engine(f"sqlite:///{test_db}", connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except Exception:
                pass


@pytest.fixture
def client(db_session):
    # Override get_db dependency
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestPasswordHashing:
    def test_hashing_creates_different_salts(self):
        h1 = hash_password("mypassword")
        h2 = hash_password("mypassword")
        assert h1 != h2
        assert verify_password("mypassword", h1)
        assert verify_password("mypassword", h2)

    def test_invalid_password_fails(self):
        h = hash_password("mypassword")
        assert not verify_password("wrongpassword", h)


class TestAuthEndpoints:
    def test_register_creates_user_and_returns_jwt(self, client):
        res = client.post(
            "/api/v1/auth/register",
            json={"email": "dev@timeslice.ai", "password": "securepwd123", "name": "Lead Developer"}
        )
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert data["user_email"] == "dev@timeslice.ai"
        assert data["user_name"] == "Lead Developer"

        # Verify token content
        payload = decode_token(data["access_token"])
        assert payload["sub"] == "dev@timeslice.ai"
        assert payload["name"] == "Lead Developer"

    def test_register_duplicate_email_fails(self, client):
        client.post(
            "/api/v1/auth/register",
            json={"email": "dev@timeslice.ai", "password": "securepwd123", "name": "Lead Developer"}
        )
        res = client.post(
            "/api/v1/auth/register",
            json={"email": "dev@timeslice.ai", "password": "anotherpassword", "name": "Someone Else"}
        )
        assert res.status_code == 409
        assert "already exists" in res.json()["detail"]

    def test_login_success(self, client):
        # Register first
        client.post(
            "/api/v1/auth/register",
            json={"email": "dev@timeslice.ai", "password": "securepwd123", "name": "Lead Developer"}
        )
        
        # Login using OAuth2 form fields
        res = client.post(
            "/api/v1/auth/login",
            data={"username": "dev@timeslice.ai", "password": "securepwd123"}
        )
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user_email"] == "dev@timeslice.ai"

    def test_login_invalid_credentials_fails(self, client):
        client.post(
            "/api/v1/auth/register",
            json={"email": "dev@timeslice.ai", "password": "securepwd123", "name": "Lead Developer"}
        )
        res = client.post(
            "/api/v1/auth/login",
            data={"username": "dev@timeslice.ai", "password": "wrongpassword"}
        )
        assert res.status_code == 401

    def test_get_me_endpoint(self, client):
        # Register
        reg_res = client.post(
            "/api/v1/auth/register",
            json={"email": "dev@timeslice.ai", "password": "securepwd123", "name": "Lead Developer"}
        )
        token = reg_res.json()["access_token"]

        # Call /me with authorization header
        res = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == "dev@timeslice.ai"
        assert data["name"] == "Lead Developer"
