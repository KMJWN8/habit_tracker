from typing import List, Union
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

    async def get_all(self, user_id: Union[str, UUID]) -> List[Habit]:
        try:
            user_id = UUID(user_id) if isinstance(user_id, str) else user_id

            query = select(self.model).where(self.model.user_id == user_id)
            result = await self.session.execute(query)

            return list(result.scalars.all())

        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка получения списка привычек пользователя с id: {str(user_id)} {str(e)}"
            )

    async def get(self, user_id: Union[str, UUID], habit_id: int) -> Habit:
        try:
            user_id = UUID(user_id) if isinstance(user_id, str) else user_id

            query = select(self.model).where(
                and_(
                    self.model.user_id == id, 
                    self.model.id == habit_id
                )
            )

            result = await self.session.execute(query)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения привычки пользователя с id: {str(user_id)} {str(e)}")
        return result.scalar_one_or_none()
    
