from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr, constr, Field, model_validator, field_validator
from .calculations import CalculationType

usernameStr = Annotated[str, Field(min_length=3, max_length=50)]
passwordStr = Annotated[str, Field(min_length=6)]

class UserBase(BaseModel):
    username: usernameStr
    email: EmailStr

class UserCreate(UserBase):
    password: passwordStr

class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CalculationBase(BaseModel):
    a: float
    b: float
    type: CalculationType

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value):
        if isinstance(value, CalculationType):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            for calc_type in CalculationType:
                if normalized in {calc_type.value, calc_type.name.lower()}:
                    return calc_type
        raise ValueError("Invalid calculation type. Use add, sub, multiply, or divide.")

    @model_validator(mode="after")
    def validate_division(self):
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Divisor cannot be zero.")
        return self

class CalculationCreate(CalculationBase):
    pass

class CalculationRead(CalculationBase):
    id: int
    result: float
    created_at: datetime

    class Config:
        orm_mode = True
