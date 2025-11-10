from datetime import datetime
from pydantic import BaseModel, EmailStr, constr

class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: constr(min_length=6)

class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
