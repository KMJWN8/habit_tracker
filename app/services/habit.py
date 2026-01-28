from typing import Any, Optional

from app.core.config import settings
from app.core.logger import get_logger
from app.models.habit import Habit
from app.models.user import User
from app.repositories.habit import HabitRepository
from app.schemas.habit import HabitCreate, HabitResponse, HabitUpdate


logger = get_logger(__name__)


class HabitService:
    def __init__(self, habit_repository: HabitRepository):
        self.habit_repository = habit_repository

        async def create_habit(
            self, 
            user: User, 
            habit_data: HabitCreate
        ) -> Habit:

            habit_dict = habit_data.model_dump()

            habit = await self.habit_repository.create_with_user(user.id, habit_dict)

            logger.info(f"Habit created: {habit.id} for user: {user.id}")
            return habit

        async def get_user_habits(
            self,
            user: User,
            only_active: bool = True
        ) -> list[Habit]:

            habits = await self.habit_repository.get_all(user.id, only_active)

            logger.debug(f"Found {len(habits)} habits for user: {user.id}")
            return habits

        async def get_user_habit(
            self,
            user: User,
            habit_id: int
        ) -> Optional[Habit]:

            habit = await self.habit_repository.get(user.id, habit_id)

            if habit:
                logger.debug(f"Habit {habit_id} found for user: {user.id}")
            else:
                logger.warning(f"Habit {habit_id} not found for user: {user.id}")

            return habit

        async def update_habit(
            self,
            user: User,
            habit_id: int,
            habit_data: HabitUpdate
        ) -> Optional[Habit]:

            update_dict = habit_data.model_dump(exclude_unset=True)

            if not update_dict:
                logger.warning(f"No data to update for habit {habit_id}")
                return await self.get_user_habit(user, habit_id)

            updated_habit = await self.habit_repository.update_user_habit(
                user.id, habit_id, update_dict
            )

            if updated_habit:
                logger.info(f"Habit {habit_id} updated succesfully for user: {user.id}")
            else:
                logger.warning(f"Habit {habit_id} not found for update for user: {user.id}")

            return updated_habit

        async def delete_habit(
            self,
            user: User,
            habit_id: int
        ) -> bool:
            success = await self.habit_repository.delete_user_habit(user.id, habit_id)

            if success:
                logger.info(f"Habit {habit_id} deleted (deactivated) for user: {user.id}")
            else:
                logger.warning(f"Habit {habit_id} not found for deletion for user: {user.id}")

            return success


        async def to_response(self, habit: Habit) -> HabitResponse:
            return HabitResponse.model_validate(habit)

        async def to_response_list(self, habits: list[Habit]) -> list[HabitResponse]:
            return [HabitResponse.model_validate(habit) for habit in habits]

