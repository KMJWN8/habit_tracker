from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.dependencies import get_current_active_user, get_habit_service
from app.core.logger import get_logger
from app.models import User
from app.schemas import HabitCreate, HabitResponse, HabitUpdate
from app.services import HabitService

logger = get_logger(__name__)

router = APIRouter(prefix="/habits", tags=["habits"])


@router.post("")
async def create_habit(
    habit_data: HabitCreate,
    current_user: User = Depends(get_current_active_user),
    habit_service: HabitService = Depends(get_habit_service),
):
    try:
        habit = await habit_service.create_habit(current_user, habit_data)

        return await habit_service.to_response(habit)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create habit",
        )


@router.get("")
async def get_habits(
    only_active: bool = Query(True, description="Only active habits"),
    current_user: User = Depends(get_current_active_user),
    habit_service: HabitService = Depends(get_habit_service),
) -> list[HabitResponse]:
    try:
        habits = await habit_service.get_user_habits(current_user, only_active)

        return await habit_service.to_response(habits)

    except Exception as e:
        logger.error(f"Error getting habits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed go get habits",
        )


@router.get("/{habit_id}")
async def get_habit(
    current_user: User = Depends(get_current_active_user),
    habit_id: int = Path(..., ge=1),
    habit_service: HabitService = Depends(get_habit_service),
) -> HabitResponse:
    try:
        habit = await habit_service.get_user_habit(current_user, habit_id)

        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
            )

        return await habit_service.to_response(habit)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting habit {habit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get habit",
        )


@router.patch("/{habit_id}")
async def update_habit(
    current_user: User = Depends(get_current_active_user),
    habit_id: int = Path(..., ge=1),
    habit_data: HabitUpdate = None,
    habit_service: HabitService = Depends(get_habit_service),
) -> HabitResponse:
    try:
        if habit_data is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided for update",
            )

        updated_habit = await habit_service.update_habit(
            current_user, habit_id, habit_data
        )

        if not update_habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
            )

        return await habit_service.to_response(update_habit)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating habit {habit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update habit",
        )


@router.delete("/{habit_id}")
async def delete_habit(
    current_user: User = Depends(get_current_active_user),
    habit_id: int = Path(..., ge=1),
    habit_service: HabitService = Depends(get_habit_service),
):
    try:
        success = await habit_service.delete_habit(current_user, habit_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting habit {habit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete habit",
        )
