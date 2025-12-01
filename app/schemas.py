from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
)

# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    identifier: str = Field(..., description="Username or email")
    password: str = Field(..., min_length=6)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Calculation schemas
class CalculationType(str, Enum):
    add = "add"
    sub = "sub"
    multiply = "multiply"
    divide = "divide"

class CalculationBase(BaseModel):
    a: float
    b: float
    type: CalculationType

    model_config = ConfigDict(from_attributes=True)

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v):
        if isinstance(v, CalculationType):
            return v

        if not isinstance(v, str):
            raise ValueError("type must be a string or CalculationType")

        key = v.strip().lower()
        mapping = {
            "add": CalculationType.add,
            "plus": CalculationType.add,
            "sum": CalculationType.add,
            "sub": CalculationType.sub,
            "subtract": CalculationType.sub,
            "minus": CalculationType.sub,
            "mul": CalculationType.multiply,
            "multiply": CalculationType.multiply,
            "times": CalculationType.multiply,
            "div": CalculationType.divide,
            "divide": CalculationType.divide,
        }
        if key in mapping:
            return mapping[key]

        raise ValueError("type must be one of: add, sub, multiply, divide")

class CalculationRead(CalculationBase):
    id: int
    result: float

    model_config = ConfigDict(from_attributes=True)

class CalculationCreate(CalculationBase):

    @model_validator(mode="after")
    def check_division_by_zero(self):
        if self.type == CalculationType.divide and self.b == 0:
            raise ValueError("Division by zero is not allowed")
        return self