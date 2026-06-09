import uuid
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True
    )

    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    hashed_password: Mapped[str] = mapped_column(String(255))

    streak_days: Mapped[int] = mapped_column(default=0)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    habits: Mapped[list["Habit"]] = relationship(
        "Habit", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username})"
