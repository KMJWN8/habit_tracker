from uuid import UUID
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Базовая схема пользователя с публичными полями."""
    
    username: Annotated[
        str,
        Field(
            ...,
            min_length=3,
            max_length=50,
            pattern=r"^[a-zA-Z0-9_]+$",
            description="Уникальное имя пользователя (только буквы, цифры, подчеркивания)",
            examples=["john_doe", "alice123", "fitness_guru"],
        )
    ]
    
    email: Annotated[
        EmailStr,
        Field(
            ...,
            description="Email адрес пользователя (уникальный)",
            examples=["john.doe@example.com", "alice@fitness.app"],
        )
    ]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "john_doe",
                    "email": "john.doe@example.com",
                }
            ]
        }
    }


class UserCreate(UserBase):
    """Схема для регистрации нового пользователя."""
    
    password: Annotated[
        str,
        Field(
            ...,
            min_length=8,
            max_length=100,
            description="Пароль (минимум 8 символов, должен содержать буквы и цифры)",
            examples=["SecurePass123!", "MyStr0ngP@ssw0rd"],
        )
    ]

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Проверка сложности пароля:
        - Минимум 8 символов (уже проверено Field)
        - Хотя бы одна заглавная буква
        - Хотя бы одна строчная буква
        - Хотя бы одна цифра
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        
        if not any(c.islower() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Проверка, что username не начинается с цифры."""
        if v[0].isdigit():
            raise ValueError("Имя пользователя не может начинаться с цифры")
        return v.lower()  # Приводим к нижнему регистру

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "new_user",
                    "email": "newuser@example.com",
                    "password": "SecurePass123!",
                }
            ]
        }
    }


class UserUpdate(BaseModel):
    """
    Схема для обновления профиля пользователя.
    Передавайте только те поля, которые нужно изменить.
    """
    
    username: Annotated[
        str | None,
        Field(
            None,
            min_length=3,
            max_length=50,
            pattern=r"^[a-zA-Z0-9_]+$",
            description="Новое имя пользователя",
            examples=["updated_username"],
        )
    ]
    
    email: Annotated[
        EmailStr | None,
        Field(
            None,
            description="Новый email адрес",
            examples=["newemail@example.com"],
        )
    ]
    
    password: Annotated[
        str | None,
        Field(
            None,
            min_length=8,
            max_length=100,
            description="Новый пароль (те же требования к сложности)",
            examples=["NewSecurePass456!"],
        )
    ]
    
    is_active: Annotated[
        bool | None,
        Field(
            None,
            description="Статус активности аккаунта (только для администраторов)",
            examples=[True, False],
        )
    ]

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str | None) -> str | None:
        """Та же проверка сложности пароля."""
        if v is None:
            return v
        
        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        
        if not any(c.islower() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "updated_user",
                    "email": "updated@example.com",
                }
            ]
        }
    }


class UserResponse(UserBase):
    """Полная информация о пользователе с системными полями."""
    
    id: Annotated[
        UUID,
        Field(
            ...,
            description="Уникальный идентификатор пользователя (UUID v4)",
            examples=["550e8400-e29b-41d4-a716-446655440000"],
        )
    ]
    
    streak_days: Annotated[
        int,
        Field(
            0,
            ge=0,
            description="Текущая серия дней выполнения привычек подряд",
            examples=[7, 21, 45],
        )
    ]
    
    is_active: Annotated[
        bool,
        Field(
            True,
            description="Активен ли аккаунт (False для забаненных пользователей)",
            examples=[True],
        )
    ]
    
    created_at: Annotated[
        datetime,
        Field(
            ...,
            description="Дата и время регистрации (ISO 8601)",
            examples=["2026-06-09T10:30:00.123456"],
        )
    ]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "john_doe",
                    "email": "john.doe@example.com",
                    "streak_days": 21,
                    "is_active": True,
                    "created_at": "2026-01-15T08:30:00.123456",
                }
            ]
        },
    )


class TokenResponse(BaseModel):
    """Ответ с JWT токенами после успешной аутентификации."""
    
    access_token: Annotated[
        str,
        Field(
            ...,
            description="JWT access token для авторизации запросов",
            examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
        )
    ]
    
    refresh_token: Annotated[
        str,
        Field(
            ...,
            description="JWT refresh token для обновления access token",
            examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
        )
    ]
    
    token_type: Annotated[
        str,
        Field(
            "bearer",
            description="Тип токена (всегда 'bearer')",
            examples=["bearer"],
        )
    ]
    
    expires_in: Annotated[
        int,
        Field(
            ...,
            description="Время жизни access token в секундах",
            examples=[1800, 3600],
        )
    ]
    
    refresh_expires_in: Annotated[
        int,
        Field(
            ...,
            description="Время жизни refresh token в секундах",
            examples=[604800, 2592000],
        )
    ]
    
    user: Annotated[
        UserResponse,
        Field(
            ...,
            description="Информация о пользователе",
        )
    ]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJlbWFpbCI6ImpvaG4uZG9lQGV4YW1wbGUuY29tIiwidXNlcm5hbWUiOiJqb2huX2RvZSIsImV4cCI6MTcxNzkyMjYwMH0...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MTg1MjY2MDB9...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                    "refresh_expires_in": 604800,
                    "user": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "john_doe",
                        "email": "john.doe@example.com",
                        "streak_days": 21,
                        "is_active": True,
                        "created_at": "2026-01-15T08:30:00.123456",
                    }
                }
            ]
        }
    }