from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_async_session
from app.repositories.user import UserRepository
from app.repositories.habit import HabitRepository
from app.services.auth_service import AuthService
from app.services.habit_service import HabitService
from app.core.security import oauth2_scheme
from app.models.user import User


async def get_user_repository(
    db: AsyncSession = Depends(get_db_async_session)
) -> UserRepository:
    return UserRepository(db)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(user_repo)

async def get_habit_repository(
    db: AsyncSession = Depends(get_db_async_session)
) -> HabitRepository:
    return HabitRepository(db)

async def get_habit_service(
    habit_repo: HabitRepository = Depends(get_habit_repository)
) -> HabitService:
    return HabitService(habit_repo)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user = await auth_service.validate_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive"
        )
    return current_user