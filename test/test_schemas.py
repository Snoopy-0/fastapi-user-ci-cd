import pytest
from pydantic import ValidationError
from app.schemas import CalculationCreate, UserCreate

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

def test_calculation_create_valid_add():
    calc = CalculationCreate(a=2, b=3, type="Add")
    assert calc.type.value == "add"

def test_calculation_create_invalid_type():
    with pytest.raises(ValidationError):
        CalculationCreate(a=2, b=3, type="modulo")

def test_calculation_create_divide_by_zero():
    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=0, type="divide")
