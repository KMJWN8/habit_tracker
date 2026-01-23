from pydantic import BaseModel, ConfigDict, Field, validator
from typing import Optional
import uuid
from datetime import datetime, time


class HabitBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: str = Field(default="#3B82F6", pattern="^#[0-9A-Fa-f]{6}$")
    goal_streak: int = Field(default=21, ge=1, le=365)
    reminder_time: Optional[time] = None


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    goal_streak: Optional[int] = Field(None, ge=1, le=365)
    reminder_time: Optional[time] = None
    is_active: Optional[bool] = None

    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            return f"#{v}"
        return v


class HabitResponse(HabitBase):
    id: int
    user_id: uuid.UUID
    is_active: bool = True
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)