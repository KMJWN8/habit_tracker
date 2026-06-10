from uuid import UUID

from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError, 
    BusinessError,
    ConflictError,
)
from app.core.logger import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse


logger = get_logger(__name__)


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, user_data: UserCreate) -> TokenResponse:
        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            raise ConflictError("Email already registered")

        existing_username = await self.user_repo.get_by_username(user_data.username)
        if existing_username:
            raise ConflictError("Username already taken")

        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = get_password_hash(user_data.password)

        user = await self.user_repo.create(user_dict)

        logger.info("User registered | user_id=%s", user.id)
        return self._create_token_response(user)

    async def login(self, login_data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(login_data.email)

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")

        if not user.is_active:
            raise AuthenticationError("Account is inactive")

        logger.info("User logged in | user_id=%s", user.id)
        return self._create_token_response(user)
    
    async def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token)
            if not payload:
                return
        except Exception:
            pass
    
    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload:
            raise AuthenticationError("Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid refresh token")
        
        user = await self.user_repo.get(UUID(user_id))

        if not user.is_active:
            raise AuthenticationError("Account is inactive")
        
        logger.info("Tokens refreshed | user_id=%s", user.id)
        return self._create_token_response(user)

    async def validate_token(self, token: str) -> User:
        if not token:
            raise AuthenticationError("Token is required")

        payload = decode_token(token)
        if not payload:
            raise AuthenticationError("Invalid or expired token")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")

        user = await self.user_repo.get(UUID(user_id))

        if not user.is_active:
            raise AuthenticationError("Account is inactive")

        return user

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> None:
        # Проверяем текущий пароль
        if not verify_password(current_password, user.hashed_password):
            raise AuthenticationError("Current password is incorrect")

        # Обновляем пароль
        await self.user_repo.update(
            user.id, {"hashed_password": get_password_hash(new_password)}
        )

        logger.info("Password changed | user_id=%s", user.id)

    async def deactivate_user(self, user_id: UUID) -> None:
        user = await self.user_repo.get(user_id)

        if not user.is_active:
            raise BusinessError("User is already inactive")

        await self.user_repo.update(user_id, {"is_active": False})

        logger.info("User deactivated | user_id=%s", user_id)

    async def activate_user(self, user_id: UUID) -> None:
        user = await self.user_repo.get(user_id)
        if user.is_active:
            raise BusinessError("User is already active")

        await self.user_repo.update(user_id, {"is_active": True})

        logger.info("User activated | user_id=%s", user_id)
    
    def _create_token_response(self, user: User) -> TokenResponse:
        """Создание ответа с токенами."""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
        }

        return TokenResponse(
            access_token=create_access_token(data=token_data),
            refresh_token=create_refresh_token(data=token_data),
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            user=UserResponse.model_validate(user),
        )
