"""
Calculation BREAD flows exercised without starting a real server/browser.
We rely on FastAPI's TestClient because the sandbox blocks opening sockets and Playwright.
"""
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

def _create_user_and_token():
    uniq = uuid.uuid4().hex[:8]
    payload = {
        "username": f"user_{uniq}",
        "email": f"user_{uniq}@example.com",
        "password": "mysecret123",
    }
    resp = client.post("/users/register", json=payload)
    assert resp.status_code in (200, 201)
    return resp.json()["access_token"]

def _auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}

def test_calculation_bread_positive():
    token = _create_user_and_token()
    headers = _auth_headers(token)

    create_resp = client.post(
        "/calculations",
        json={"a": 2, "b": 3, "type": "add"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    calc_id = created["id"]
    assert created["result"] == 5

    update_resp = client.put(
        f"/calculations/{calc_id}",
        json={"a": 2, "b": 4, "type": "multiply"},
        headers=headers,
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["result"] == 8
    assert updated["type"] == "multiply"

    delete_resp = client.delete(f"/calculations/{calc_id}", headers=headers)
    assert delete_resp.status_code == 204

    read_resp = client.get(f"/calculations/{calc_id}", headers=headers)
    assert read_resp.status_code == 404

def test_calculation_negative_divide_by_zero():
    token = _create_user_and_token()
    headers = _auth_headers(token)

    resp = client.post(
        "/calculations",
        json={"a": 10, "b": 0, "type": "divide"},
        headers=headers,
    )
    assert resp.status_code == 422
    msg = resp.json()["detail"][0]["msg"].lower()
    assert "division by zero" in msg

def test_calculation_unauthorized_access():
    resp = client.get("/calculations")
    assert resp.status_code == 401
    assert resp.json()["detail"].lower() == "not authenticated"
