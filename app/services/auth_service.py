from typing import Optional, Tuple

from fastapi import Depends, HTTPException, status

from app.core.logger import get_logger
from app.core.security import (
    create_access_token,
    decode_token,
    oauth2_scheme,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate

logger = get_logger(__name__)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository
        logger.debug("AuthService initialized")

    async def register(self, user_data: UserCreate) -> Tuple[User, str]:
        """
        Регистрация нового пользователя.
        Возвращает (user, token)
        """
        logger.info(f"Registration attempt for: {user_data.email}")

        # Проверяем уникальность email
        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            logger.warning(
                f"Registration failed: email {user_data.email} already exists"
            )
            raise ValueError("Email already registered")

        # Проверяем уникальность username (если нужно)
        if hasattr(user_data, "username"):
            existing_username = await self.user_repo.get_by_username(user_data.username)
            if existing_username:
                logger.warning(
                    f"Registration failed: username {user_data.username} already exists"
                )
                raise ValueError("Username already taken")

        # Создаем пользователя
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = (
            user_data.password
        )  # Пароль будет хеширован в репозитории

        user = await self.user_repo.create(user_dict)

        # Создаем токен
        token = self._create_token(user)

        logger.info(f"User registered successfully: {user.id} ({user.email})")
        return user, token

    # ========== ЛОГИН ==========

    async def login(self, email: str, password: str) -> Tuple[User, str]:
        """
        Аутентификация пользователя.
        Возвращает (user, token) или бросает ValueError
        """
        logger.info(f"Login attempt for: {email}")

        user = await self.user_repo.get_by_email(email)
        if not user:
            logger.warning(f"Login failed: user {email} not found")
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Login failed: invalid password for {email}")
            raise ValueError("Invalid credentials")

        if not user.is_active:
            logger.warning(f"Login failed: user {email} is inactive")
            raise ValueError("Account inactive")

        token = self._create_token(user)

        logger.info(f"User logged in successfully: {user.id} ({email})")
        return user, token

    # ========== ВАЛИДАЦИЯ ТОКЕНА ==========

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
        """Смена пароля пользователя"""
        logger.info(f"Password change attempt for user: {user.id}")

        # Проверяем текущий пароль
        if not verify_password(current_password, user.hashed_password):
            logger.warning(
                f"Password change failed: wrong current password for user {user.id}"
            )
            raise ValueError("Current password is incorrect")

        # Обновляем пароль
        await self.user_repo.update(
            user.id, {"hashed_password": new_password}  # Репозиторий должен хешировать
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

    def _create_token(self, user: User) -> str:
        """Создание JWT токена (внутренний метод)"""
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        logger.debug(f"Token created for user: {user.id}")
        return token


async def get_current_user(
    token: str = Depends(oauth2_scheme), auth_service: "AuthService" = Depends()
) -> User:
    """
    Зависимость: получить текущего пользователя из токена.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    user = await auth_service.validate_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Зависимость: получить текущего активного пользователя.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account is inactive"
        )
    return current_user


async def get_auth_service(user_repo: UserRepository = Depends()) -> AuthService:
    return AuthService(user_repo)
