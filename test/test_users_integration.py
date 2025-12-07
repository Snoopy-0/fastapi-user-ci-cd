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
    for _ in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except Exception:
            time.sleep(1)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_register_user_success():
    response = client.post(
        "/users/register",
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

    # verify user exists in DB
    db = TestingSessionLocal()
    try:
        user = db.query(models.User).filter_by(email="integration@example.com").first()
        assert user is not None
        assert user.username == "integrationuser"
    finally:
        db.close()

def test_register_user_duplicate_email():
    payload = {
        "username": "user1",
        "email": "dup@example.com",
        "password": "password123",
    }

    client.post("/users/register", json=payload)

    response = client.post("/users/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "User with that username or email already exists"

def test_login_user_success():
    payload = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "password123",
    }
    client.post("/users/register", json=payload)

    response = client.post(
        "/users/login",
        json={
            "identifier": "loginuser",  
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "loginuser"
    assert data["email"] == "login@example.com"

def test_login_user_invalid_credentials():
    response = client.post(
        "/users/login",
        json={
            "identifier": "nonexistentuser",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"
