from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.core.exceptions import NotFoundError, DatabaseError
from app.models import Habit

logger = get_logger(__name__)


class HabitRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Habit

    async def get_all(self, user_id: UUID, only_active: bool = True) -> list[Habit]:
        try:
            query = select(self.model).where(self.model.user_id == user_id)

            if only_active:
                query = query.where(self.model.is_active.is_(True))

            query = query.order_by(self.model.created_at.desc())

            result = await self.session.execute(query)
            return list(result.scalars().all())

        except SQLAlchemyError as e:
            logger.error(
                "Failed to fetch habits | user_id=%s | only_active=%s | error=%s",
                user_id, only_active, e
            )
            # Оборачиваем в доменную ошибку
            raise DatabaseError("Failed to fetch habits") from e

    async def get(self, user_id: UUID, habit_id: int) -> Habit:
        try:
            query = select(self.model).where(
                and_(self.model.user_id == user_id, self.model.id == habit_id)
            )

            result = await self.session.execute(query)
            habit = result.scalar_one_or_none()
        
            if not habit:
                raise NotFoundError("Habit")
            return habit
        
        except SQLAlchemyError as e:
            logger.error(
                "Failed to fetch habit | user_id=%s | habit_id=%s | error=%s",
                user_id, habit_id, e
            )
            raise DatabaseError("Failed to fetch habit") from e

    async def create(self, user_id: UUID, data: dict) -> Habit:
        try:
            data["user_id"] = user_id
            habit = self.model(**data)
            self.session.add(habit)
            await self.session.commit()
            await self.session.refresh(habit)
            
            logger.info("Habit created | user_id=%s | habit_id=%s",
                        user_id, habit.id
            )
            return habit

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error("Failed to create habit | user_id=%s | error=%s",
                         user_id, e
            )
            raise DatabaseError("Failed to create habit") from e

    async def update(
        self, user_id: UUID, habit_id: int, data: dict
    ) -> Habit:
        habit = await self.get(user_id, habit_id)

        try:
            for key, value in data.items():
                setattr(habit, key, value)

            await self.session.commit()
            await self.session.refresh(habit)

            logger.info("Habit updated | user_id=%s | habit_id=%s",
                        user_id, habit_id
            )
            return habit

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error("Failed to update habit | user_id=%s | habit_id=%s | error=%s",
                         user_id, habit_id, e
            )
            raise DatabaseError("Failed to update habit") from e

    async def delete(self, user_id: UUID, habit_id: int) -> bool:
        habit = await self.get(user_id, habit_id)

        try:
            habit.is_active = False
            await self.session.commit()

            logger.info("Habit deleted (soft) | user_id=%s | habit_id=%s",
                        user_id, habit_id
            )
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error("Failed to delete habit | user_id=%s | habit_id=%s | error=%s",
                         user_id, habit_id, e
            )
            raise DatabaseError("Failed to delete habit") from e
