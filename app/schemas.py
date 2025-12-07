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

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    access_token: str | None = None

    model_config = ConfigDict(from_attributes=True)

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

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v):
        if isinstance(v, CalculationType):
            return v
        if isinstance(v, str):
            s = v.strip().lower()
            mapping = {
                "add": CalculationType.add,
                "sub": CalculationType.sub,
                "subtract": CalculationType.sub,
                "mul": CalculationType.multiply,
                "multiply": CalculationType.multiply,
                "div": CalculationType.divide,
                "divide": CalculationType.divide,
            }
            if s in mapping:
                return mapping[s]
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

class CalculationUpdate(BaseModel):
    a: float | None = None
    b: float | None = None
    type: CalculationType | None = None

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v):
        if v is None:
            return v
        if isinstance(v, CalculationType):
            return v
        if isinstance(v, str):
            s = v.strip().lower()
            mapping = {
                "add": CalculationType.add,
                "sub": CalculationType.sub,
                "subtract": CalculationType.sub,
                "mul": CalculationType.multiply,
                "multiply": CalculationType.multiply,
                "div": CalculationType.divide,
                "divide": CalculationType.divide,
            }
            if s in mapping:
                return mapping[s]
        raise ValueError("type must be one of: add, sub, multiply, divide")

    @model_validator(mode="after")
    def check_division_by_zero(self):
        if self.type == CalculationType.divide and self.b == 0:
            raise ValueError("Division by zero is not allowed")
        return self

# Auth schemas

class UserLogin(BaseModel):
    identifier: str
    password: str
