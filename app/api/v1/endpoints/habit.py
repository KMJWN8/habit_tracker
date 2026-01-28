from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from app.schemas.habit import (
    HabitCreate,
    HabitUpdate,
    HabitResponse
)
from app.services.habit import HabitService
from app.models.user import User
from app.api.dependencies import get_current_active_user, get_habit_service


router = APIRouter(prefix="/habits", tags=["habits"])


@router.post("")
async def create_habit(
    habit_data: HabitCreate,
    current_user: User = Depends(get_current_active_user),
    habit_service: HabitService = Depends(get_habit_service)
):
    try:
        habit = await habit_service.create_habit(current_user, habit_data)

        return await habit_service.to_response(habit)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create habit"
        )

