from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habit import Habit
from app.repositories.base import BaseRepository
from app.schemas.habit import HabitCreate, HabitUpdate


class HabitRepository(BaseRepository[Habit, HabitCreate, HabitUpdate]):
    def __init__(self, session: AsyncSession):
        self.session = session
