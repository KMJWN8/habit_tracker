from enum import Enum

import uuid
import datetime

from sqlalchemy import Enum as SQLEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Habit(Base):

    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    title: Mapped[str] = mapped_column(String(100))

    description: Mapped[str | None]

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )

    is_active: Mapped[bool] = mapped_column(default=True)

    color: Mapped[str] = mapped_column(String(7), default="#3B82F6")

    goal_streak: Mapped[int] = mapped_column(default=21)

    reminder_time: Mapped[datetime.time | None]

    user: Mapped["User"] = relationship("User", back_populates="habits")

    trackings: Mapped[list["HabitTracking"]] = relationship(
        "HabitTracking", back_populates="habit", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Habit(id={self.id}, title={self.title})"
    

class HabitStatus(str, Enum):
    COMPLETED = "+"
    FAILED = "-"
    SKIPPED = "skip"


class HabitTracking(Base):

    __tablename__ = "habit_tracking"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    habit_id: Mapped[int] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"),
        index=True
    )

    date: Mapped[datetime.date] = mapped_column(index=True)

    status: Mapped[HabitStatus] = mapped_column(
        SQLEnum(HabitStatus, native_enum=False),
        default=HabitStatus.COMPLETED
    )

    notes: Mapped[str | None] = mapped_column(String(500))

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )

    habit: Mapped[Habit] = relationship("Habit", back_populates="trackings")

    def __repr__(self) -> str:
        return f"HabitTracking(habit_id={self.habit_id}, date={self.date}, status={self.status})"
