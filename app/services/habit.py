from app.core.logger import get_logger
from app.core.exceptions import BusinessError
from app.models.habit import Habit
from app.models.user import User
from app.repositories.habit import HabitRepository
from app.schemas.habit import HabitCreate, HabitUpdate

logger = get_logger(__name__)


class HabitService:
    MAX_ACTIVE_HABITS = 10

    def __init__(self, habit_repo: HabitRepository):
        self.habit_repo = habit_repo

    async def create_habit(self, user: User, data: HabitCreate) -> Habit:
        active_habits = await self.habit_repo.get_all(user.id, only_active=True)
        if len(active_habits) >= self.MAX_ACTIVE_HABITS:
            logger.warning("Habit limit reached | user_id=%s | count=%s",
                           user.id, len(active_habits)
            )
            raise BusinessError(f"Maximum {self.MAX_ACTIVE_HABITS} active habits")

        return await self.habit_repo.create(user.id, data.model_dump())

    async def get_user_habits(
        self, user: User, only_active: bool = True
    ) -> list[Habit]:

        habits = await self.habit_repo.get_all(user.id, only_active)

        logger.debug("User habits fetched | user_id=%s | count=%s",
                     user.id, len(habits)
        )
        return habits

    async def get_user_habit(self, user: User, habit_id: int) -> Habit | None:
        return await self.habit_repo.get(user.id, habit_id)

    async def update_habit(
        self, user: User, habit_id: int, data: HabitUpdate
    ) -> Habit:
        update_dict = data.model_dump(exclude_unset=True)

        if not update_dict:
            logger.debug("Empty update skipped | user_id=%s | habit_id=%s",
                         user.id, habit_id
        )
            return await self.get_user_habit(user, habit_id)

        return await self.habit_repo.update(user.id, habit_id, update_dict)

    async def deactivate_habit(self, user: User, habit_id: int) -> bool:
        return await self.habit_repo.delete(user.id, habit_id)
    