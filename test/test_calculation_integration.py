import os
import time
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app, get_db
from app import models

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///./test_app.db",
)

connect_args = {}
if TEST_DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(TEST_DATABASE_URL, future=True, connect_args=connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_auth_headers():
    uniq = uuid.uuid4().hex[:8]
    payload = {
        "username": f"testuser_{uniq}",
        "email": f"testuser_{uniq}@example.com",
        "password": "password123",
    }
    resp = client.post("/users/register", json=payload)
    assert resp.status_code in (200, 201)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

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

def test_calculation_bread_flow():
    auth = get_auth_headers()

    create_payload = {"a": 10, "b": 5, "type": "sub"}
    resp = client.post(
        "/calculations",
        json=create_payload,
        headers=auth,
    )
    assert resp.status_code == 201
    created = resp.json()
    calc_id = created["id"]

    assert created["a"] == 10
    assert created["b"] == 5
    assert created["result"] == 5

    resp = client.get(f"/calculations/{calc_id}", headers=auth)
    assert resp.status_code == 200
    read_back = resp.json()
    assert read_back["id"] == calc_id

    # BROWSE
    resp = client.get("/calculations", headers=auth)
    assert resp.status_code == 200
    all_calcs = resp.json()
    assert any(c["id"] == calc_id for c in all_calcs)

    # EDIT
    update_payload = {"a": 20, "b": 5, "type": "divide"}
    resp = client.put(
        f"/calculations/{calc_id}",
        json=update_payload,
        headers=auth,
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["result"] == 4

    # DELETE
    resp = client.delete(f"/calculations/{calc_id}", headers=auth)
    assert resp.status_code == 204

    # Ensure it’s gone
    resp = client.get(f"/calculations/{calc_id}", headers=auth)
    assert resp.status_code == 404

def test_invalid_divide_by_zero():
    payload = {"a": 10, "b": 0, "type": "divide"}
    resp = client.post(
        "/calculations",
        json=payload,
        headers=get_auth_headers(),
    )

    assert resp.status_code == 422

    body = resp.json()
    assert "Division by zero" in body["detail"][0]["msg"]

def test_calculation_stats_flow():
    auth = get_auth_headers()

    initial_resp = client.get("/calculations/stats", headers=auth)
    assert initial_resp.status_code == 200
    assert initial_resp.json()["total"] == 0

    client.post("/calculations", json={"a": 4, "b": 4, "type": "add"}, headers=auth)
    client.post(
        "/calculations",
        json={"a": 10, "b": 3, "type": "sub"},
        headers=auth,
    )

    stats_resp = client.get("/calculations/stats", headers=auth)
    assert stats_resp.status_code == 200
    stats = stats_resp.json()

    assert stats["total"] == 2
    assert stats["average_a"] == pytest.approx(7.0)
    assert stats["average_b"] == pytest.approx(3.5)
    assert stats["average_result"] == pytest.approx(7.5)

def test_calculation_stats_requires_auth():
    resp = client.get("/calculations/stats")
    assert resp.status_code == 401
    assert resp.json()["detail"].lower() == "not authenticated"
