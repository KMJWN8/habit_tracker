from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from enum import Enum

from app.models.tracking import HabitStatus


class HabitTrackingSchema(BaseModel):
    id: int | None = None
    habit_id: int = Field(..., gt=0)
    date: date
    status: HabitStatus = HabitStatus.COMPLETED
    notes: str | None = Field(None, max_length=500)
    created_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)
        