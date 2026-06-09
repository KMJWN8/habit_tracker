from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_auth_service, get_current_active_user
from app.models import User
from app.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register(
    user_data: UserCreate, 
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest, 
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.login(login_data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.refresh_tokens(request.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.logout(request.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user
