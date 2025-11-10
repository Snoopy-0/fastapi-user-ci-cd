import os
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.database import Base

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/test_db",
)

engine = create_engine(TEST_DATABASE_URL, future=True)
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
    # ensure DB is ready (esp. in CI)
    for _ in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except Exception:
            time.sleep(1)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_create_user_success():
    response = client.post(
        "/users/",
        json={
            "username": "integrationuser",
            "email": "integration@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "integrationuser"
    assert data["email"] == "integration@example.com"
    assert "id" in data
    assert "created_at" in data

def test_create_user_duplicate_email():
    payload = {
        "username": "user1",
        "email": "dup@example.com",
        "password": "password123",
    }
    client.post("/users/", json=payload)
    response = client.post("/users/", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
