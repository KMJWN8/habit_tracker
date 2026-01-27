from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models.habit import Habit
from app.repositories.base import BaseRepository
from app.schemas.habit import HabitCreate, HabitUpdate


logger = get_logger(__name__)


class HabitRepository(BaseRepository[Habit, HabitCreate, HabitUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Habit, session)

    async def get_all(
        self, 
        user_id: UUID,
        only_active: bool = True
    ) -> list[Habit]:
        try:
            query = select(self.model).where(self.model.user_id == user_id)

            if only_active:
                query = query.where(self.model.is_active == True)

            query = query.order_by(self.model.created_at.desc())

            result = await self.session.execute(query)
            return list(result.scalars.all())

        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка получения списка привычек пользователя {user_id}: {e}"
            )
            raise

    async def get(
        self, 
        user_id: UUID, 
        habit_id: int
    ) -> Habit:
        try:
            query = select(self.model).where(
                and_(
                    self.model.user_id == user_id, 
                    self.model.id == habit_id
                )
            )

            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения привычки пользователя {user_id}: {e}")
            raise
    

    async def create_with_user(
        self,
        user_id: UUID,
        habit_data: dict
    ) -> Habit:
        try:
            habit_data["user_id"] = user_id
            return await self.create(habit_data)

        except SQLAlchemyError as e:
            logger.error(f"Ошибка создания привычки для пользователя {user_id}: {e}")
            raise

    
    async def update_user_habit(
        self,
        user_id: UUID,
        habit_id: int,
        update_data: dict
    ) -> Optional[Habit]:
        try:
            habit = await self.get(user_id, habit_id)
            if not habit:
                return None

            return await self.update(habit_id, update_data)

        except SQLAlchemyError as e:
            logger.error(f"Error updating habit {habit_id} for user {user_id}: {e}")
            raise


    async def delete_user_habit(
        self,
        user_id: UUID,
        habit_id: int
    ) -> bool:
        try:
            #Обновляем is_active на False вместо физического удаления
            updated = await self.update_user_habit(user_id, habit_id, {"is_active": False})

            return updated is not None
        
        except SQLAlchemyError as e:
            logger.error(f"Error deleting habit {habit_id} for user {user_id}: {e}")
            raise

    