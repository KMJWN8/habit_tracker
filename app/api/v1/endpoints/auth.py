from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import RegisterResponse, LoginResponse, LoginRequest, LogoutRequest
from app.services.auth import AuthService
from app.core.config import settings
from app.api.dependencies import get_auth_service, get_current_active_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, 
    auth_service: AuthService = Depends(get_auth_service)
) -> RegisterResponse:
    try:
        return await auth_service.register(user_data)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login")
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    try:
        return await auth_service.login(login_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/logout")
async def logout(
    request: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict[str, str]:
    try:
        success = await auth_service.logout(request.refresh_token)
        if success:
            return {"message": "Succesfully logged out"}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Logout failed")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    return UserResponse.model_validate(current_user)

