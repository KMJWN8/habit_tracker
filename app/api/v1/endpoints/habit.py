from fastapi import APIRouter, Depends, Path, Query, status

from app.api.dependencies import get_current_active_user, get_habit_service
from app.core.logger import get_logger
from app.models import User
from app.schemas import HabitCreate, HabitResponse, HabitUpdate
from app.services import HabitService

logger = get_logger(__name__)

router = APIRouter(prefix="/habits", tags=["habits"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=HabitResponse)
async def create_habit(
    habit_data: HabitCreate,
    current_user: User = Depends(get_current_active_user),
    habit_service: HabitService = Depends(get_habit_service),
):
    return await habit_service.create_habit(current_user, habit_data)


@router.get("", response_model=list[HabitResponse])
async def get_habits(
    only_active: bool = Query(True, description="Only active habits"),
    current_user: User = Depends(get_current_active_user),
    habit_service: HabitService = Depends(get_habit_service),
):
    return await habit_service.get_user_habits(current_user, only_active)


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    current_user: User = Depends(get_current_active_user),
    habit_id: int = Path(..., ge=1),
    habit_service: HabitService = Depends(get_habit_service),
):
    return await habit_service.get_user_habit(current_user, habit_id)


@router.patch("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_data: HabitUpdate,
    current_user: User = Depends(get_current_active_user),
    habit_id: int = Path(..., ge=1),
    habit_service: HabitService = Depends(get_habit_service),
):
    return await habit_service.update_habit(current_user, habit_id, habit_data)


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    current_user: User = Depends(get_current_active_user),
    habit_id: int = Path(..., ge=1),
    habit_service: HabitService = Depends(get_habit_service),
):
    await habit_service.deactivate_habit(current_user, habit_id)