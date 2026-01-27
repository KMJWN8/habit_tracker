from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import RegisterResponse, LoginResponse, LoginRequest
from app.services.auth_service import AuthService
from app.core.config import settings
from app.api.dependencies import get_auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


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
    
