import os
import time
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app, get_db

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_app.db")

connect_args = {}
if TEST_DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(TEST_DATABASE_URL, future=True, connect_args=connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    for _ in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except Exception:
            time.sleep(1)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_register_success():
    unique_suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"e2euser_{unique_suffix}",
        "email": f"e2e_{unique_suffix}@example.com",
        "password": "password123",
    }

    resp = client.post("/users/register", json=payload)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["access_token"]

    auth_headers = {"Authorization": f"Bearer {data['access_token']}"}
    protected_resp = client.get("/calculations", headers=auth_headers)
    assert protected_resp.status_code == 200

def test_register_short_password_shows_error():
    payload = {
        "username": "baduser",
        "email": "badpass@example.com",
        "password": "123",
    }

    resp = client.post("/users/register", json=payload)
    assert resp.status_code == 422
    detail = resp.json()["detail"][0]["msg"].lower()
    assert "at least 6 characters" in detail

def test_login_success():
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"login_{unique_suffix}@example.com"
    username = f"loginuser_{unique_suffix}"
    password = "password123"

    reg_resp = client.post(
        "/users/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg_resp.status_code in (200, 201)

    resp = client.post(
        "/users/login",
        json={"identifier": username, "password": password},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == username
    assert data["access_token"]

def test_login_wrong_password_shows_error():
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"wrongpw_{unique_suffix}@example.com"
    username = f"wrongpwuser_{unique_suffix}"
    password = "password123"

    reg_resp = client.post(
        "/users/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg_resp.status_code in (200, 201)

    resp = client.post(
        "/users/login",
        json={"identifier": username, "password": "wrongpassword"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid credentials"
