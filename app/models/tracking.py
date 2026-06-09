import datetime
from enum import Enum

from sqlalchemy import Enum as SQLEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


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

    habit: Mapped["Habit"] = relationship("Habit", back_populates="trackings")

    def __repr__(self) -> str:
        return f"HabitTracking(habit_id={self.habit_id}, date={self.date}, status={self.status})"
