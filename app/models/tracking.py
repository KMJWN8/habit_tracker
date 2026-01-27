from datetime import date as data
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class HabitStatus(str, Enum):
    COMPLETED = "+"
    FAILED = "-"
    SKIPPED = "skip"


class HabitTracking(Base):

    __tablename__ = "habit_tracking"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, index=True
    )

    habit_id: Mapped[int] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True
    )

    date: Mapped[data] = mapped_column(Date, nullable=False, index=True)

    status: Mapped[str] = mapped_column(
        String(10), nullable=False, default=HabitStatus.COMPLETED.value
    )

    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.timezone('UTC', func.now()), nullable=False
    )

    habit: Mapped["Habit"] = relationship("Habit", back_populates="trackings")

    def __repr__(self) -> str:
        return f"HabitTracking(habit_id={self.habit_id}, date={self.date}, status={self.status})"
