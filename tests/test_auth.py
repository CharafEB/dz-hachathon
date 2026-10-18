"""
tests/test_auth.py — Unit tests for JWT authentication endpoints.
Tests: /auth/register, /auth/login, /auth/me
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from database import Base, get_db
from api import app
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    if previous_override is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = previous_override


# ── Register ──────────────────────────────────────────────────────────────────

def test_register_admin():
    resp = client.post("/auth/register", json={
        "email": "admin@univ.edu",
        "password": "adminpass123",
        "role": "admin"
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["email"] == "admin@univ.edu"
    assert body["data"]["role"] == "admin"
    assert body["data"]["is_active"] is True
    # Password must NOT be returned
    assert "password" not in body["data"]
    assert "hashed_password" not in body["data"]
    pytest.admin_id = body["data"]["id"]

def test_register_teacher():
    resp = client.post("/auth/register", json={
        "email": "teacher@univ.edu",
        "password": "teacherpass123",
        "role": "teacher"
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["role"] == "teacher"
    pytest.teacher_id = resp.json()["data"]["id"]

def test_register_default_role_is_teacher():
    resp = client.post("/auth/register", json={
        "email": "default@univ.edu",
        "password": "pass123"
        # no role field → should default to teacher
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["role"] == "teacher"

def test_register_duplicate_email():
    resp = client.post("/auth/register", json={
        "email": "admin@univ.edu",
        "password": "anypass",
        "role": "admin"
    })
    assert resp.status_code == 400
    assert resp.json()["success"] is False

def test_register_invalid_role():
    resp = client.post("/auth/register", json={
        "email": "bad@univ.edu",
        "password": "pass",
        "role": "superuser"  # invalid
    })
    assert resp.status_code == 400
    assert resp.json()["success"] is False


# ── Login ─────────────────────────────────────────────────────────────────────

def test_login_admin_success():
    resp = client.post("/auth/login", json={
        "email": "admin@univ.edu",
        "password": "adminpass123"
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "token" in body
    assert body["token"] != ""
    assert body["data"]["role"] == "admin"
    pytest.admin_token = body["token"]

def test_login_teacher_success():
    resp = client.post("/auth/login", json={
        "email": "teacher@univ.edu",
        "password": "teacherpass123"
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "token" in body
    pytest.teacher_token = body["token"]

def test_login_wrong_password():
    resp = client.post("/auth/login", json={
        "email": "admin@univ.edu",
        "password": "wrongpassword"
    })
    assert resp.status_code == 401
    assert resp.json()["success"] is False

def test_login_unknown_email():
    resp = client.post("/auth/login", json={
        "email": "nobody@univ.edu",
        "password": "anypass"
    })
    assert resp.status_code == 401
    assert resp.json()["success"] is False


# ── /auth/me ──────────────────────────────────────────────────────────────────

def test_me_with_valid_admin_token():
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {pytest.admin_token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["email"] == "admin@univ.edu"
    assert body["data"]["role"] == "admin"

def test_me_with_valid_teacher_token():
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {pytest.teacher_token}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["role"] == "teacher"

def test_me_without_token():
    resp = client.get("/auth/me")
    assert resp.status_code == 401

def test_me_with_invalid_token():
    resp = client.get("/auth/me", headers={"Authorization": "Bearer totally.invalid.token"})
    assert resp.status_code == 401
