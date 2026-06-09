import uuid
from datetime import datetime, time

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models import HabitTracking


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

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    is_active: Mapped[bool] = mapped_column(default=True)

    color: Mapped[str] = mapped_column(String(7), default="#3B82F6")

    goal_streak: Mapped[int] = mapped_column(default=21)

    reminder_time: Mapped[time | None]

    user: Mapped["User"] = relationship("User", back_populates="habits")

    trackings: Mapped[list["HabitTracking"]] = relationship(
        "HabitTracking", back_populates="habit", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Habit(id={self.id}, title={self.title})"
