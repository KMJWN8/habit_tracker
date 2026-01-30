import uuid
from datetime import datetime, time
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models import HabitTracking


class Habit(Base):

    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, index=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(100), nullable=False)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.timezone("UTC", func.now()),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    color: Mapped[str] = mapped_column(String(7), default="#3B82F6", nullable=False)

    goal_streak: Mapped[int] = mapped_column(Integer, default=21, nullable=False)

    reminder_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="habits")

    trackings: Mapped[list["HabitTracking"]] = relationship(
        "HabitTracking", back_populates="habit", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Habit(id={self.id}, title={self.title})"
