from typing import Any, Optional

from app.core.config import settings
from app.core.logger import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models import User
from app.repositories import UserRepository
from app.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterResponse,
    UserCreate,
    UserResponse,
)

logger = get_logger(__name__)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    async def register(self, user_data: UserCreate) -> RegisterResponse:
        logger.info(f"Registration attempt for: {user_data.email}")

        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            logger.warning(
                f"Registration failed: email {user_data.email} already exists"
            )
            raise ValueError("Email already registered")

        existing_username = await self.user_repo.get_by_username(user_data.username)
        if existing_username:
            logger.warning(
                f"Registration failed: username {user_data.username} already exists"
            )
            raise ValueError("Username already taken")

        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = get_password_hash(user_data.password)

        user = await self.user_repo.create(user_dict)

        tokens = self._create_tokens(user)

        logger.info(f"User registered successfully: {user.id} ({user.email})")

        return RegisterResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # в секундах
            refresh_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            user=UserResponse.model_validate(user),
        )

    async def login(self, login_data: LoginRequest) -> LoginResponse:
        logger.info(f"Login attempt for: {login_data.email}")

        user = await self.user_repo.get_by_email(login_data.email)
        if not user:
            logger.warning(f"Login failed: user {login_data.email} not found")
            raise ValueError("Invalid credentials")

        if not verify_password(login_data.password, user.hashed_password):
            logger.warning(f"Login failed: invalid password for {login_data.email}")
            raise ValueError("Invalid credentials")

        if not user.is_active:
            logger.warning(f"Login failed: user {login_data.email} is inactive")
            raise ValueError("Account inactive")

        tokens = self._create_tokens(user)

        logger.info(f"User logged in successfully: {user.id} ({login_data.email})")

        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            user=UserResponse.model_validate(user),
        )

    async def validate_token(self, token: str) -> Optional[User]:
        """Валидация токена и получение пользователя"""
        if not token:
            return None

        payload = decode_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user = await self.user_repo.get(user_id)
        if not user:
            return None

        if not user.is_active:
            return None

        return user

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> bool:

        logger.info(f"Password change attempt for user: {user.id}")

        # Проверяем текущий пароль
        if not verify_password(current_password, user.hashed_password):
            logger.warning(
                f"Password change failed: wrong current password for user {user.id}"
            )
            raise ValueError("Current password is incorrect")

        # Обновляем пароль
        await self.user_repo.update(
            user.id, {"hashed_password": get_password_hash(new_password)}
        )

        logger.info(f"Password changed successfully for user: {user.id}")
        return True

    async def deactivate_user(self, user_id: str) -> bool:
        """Деактивация пользователя"""
        logger.warning(f"Deactivating user: {user_id}")

        user = await self.user_repo.get(user_id)
        if not user:
            return False

        await self.user_repo.update(user_id, {"is_active": False})

        logger.info(f"User deactivated: {user_id}")
        return True

    async def activate_user(self, user_id: str) -> bool:
        """Активация пользователя"""
        logger.info(f"Activating user: {user_id}")

        user = await self.user_repo.get(user_id)
        if not user:
            return False

        await self.user_repo.update(user_id, {"is_active": True})

        logger.info(f"User activated: {user_id}")
        return True

    async def logout(self):
        pass

    def _create_tokens(self, user: User) -> dict[str, Any]:
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
        }

        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        logger.debug(f"Tokens created for user: {user.id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
