import uuid
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HabitBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    color: str = Field(default="#3B82F6", pattern="^#[0-9A-Fa-f]{6}$")
    goal_streak: int = Field(default=21, ge=1, le=365)
    reminder_time: time | None = None


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    color: str | None = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    goal_streak: int | None = Field(None, ge=1, le=365)
    reminder_time: time | None = None
    is_active: bool | None = None

    @field_validator("color", mode="before")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        if isinstance(v, str) and not v.startswith('#'):
            return f"#{v}"
        return v


class HabitResponse(HabitBase):
    id: int
    user_id: uuid.UUID
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
