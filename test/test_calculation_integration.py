import os
import time

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

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # ensure DB is ready (handles Postgres startup lag in CI)
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
    create_payload = {"a": 10, "b": 5, "type": "sub"}
    resp = client.post("/calculations", json=create_payload)
    assert resp.status_code == 201
    created = resp.json()
    calc_id = created["id"]

    assert created["a"] == 10
    assert created["b"] == 5
    assert created["result"] == 5

    resp = client.get(f"/calculations/{calc_id}")
    assert resp.status_code == 200
    read_calc = resp.json()
    assert read_calc["id"] == calc_id
    assert read_calc["result"] == 5

    resp = client.get("/calculations")
    assert resp.status_code == 200
    all_calcs = resp.json()
    assert any(c["id"] == calc_id for c in all_calcs)

    update_payload = {"a": 20, "b": 5, "type": "divide"}
    resp = client.put(f"/calculations/{calc_id}", json=update_payload)
    assert resp.status_code == 200
    updated = resp.json()

    assert updated["result"] == 4

    resp = client.delete(f"/calculations/{calc_id}")
    assert resp.status_code == 204

    resp = client.get(f"/calculations/{calc_id}")
    assert resp.status_code == 404

def test_invalid_divide_by_zero():
    payload = {"a": 10, "b": 0, "type": "divide"}
    resp = client.post("/calculations", json=payload)

    assert resp.status_code == 422

    body = resp.json()
    assert "Division by zero" in body["detail"][0]["msg"]
