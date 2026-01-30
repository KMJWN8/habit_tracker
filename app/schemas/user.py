import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8, max_length=100)
    is_active: bool | None = None


class UserResponse(UserBase):
    id: uuid.UUID
    streak_days: int = Field(0, ge=0)
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
