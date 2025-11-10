import pytest
from pydantic import ValidationError
from app.schemas import UserCreate

def test_user_create_valid():
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="123456",
    )
    assert user.username == "testuser"

def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="not-an-email",
            password="123456",
        )

def test_user_create_password_too_short():
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="123",
        )
