from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    """Запрос для аутентификации пользователя."""
    
    email: Annotated[
        EmailStr,
        Field(
            ...,
            description="Email адрес зарегистрированного пользователя",
            examples=["john.doe@example.com", "alice@fitness.app"],
        )
    ]
    
    password: Annotated[
        str,
        Field(
            ...,
            min_length=8,
            max_length=100,
            description="Пароль пользователя",
            examples=["SecurePass123!"],
        )
    ]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "john.doe@example.com",
                    "password": "SecurePass123!",
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """
    Ответ с JWT токенами после успешной аутентификации или обновления токенов.
    Используется для login, register и refresh endpoints.
    """
    
    access_token: Annotated[
        str,
        Field(
            ...,
            description="JWT access token для авторизации запросов (передавать в заголовке Authorization: Bearer <token>)",
            examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MTc5MjI2MDB9..."],
        )
    ]
    
    refresh_token: Annotated[
        str,
        Field(
            ...,
            description="JWT refresh token для получения новой пары токенов без повторной аутентификации",
            examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MTg1MjY2MDB9..."],
        )
    ]
    
    token_type: Annotated[
        str,
        Field(
            "bearer",
            description="Тип токена (всегда 'bearer' для OAuth 2.0)",
            examples=["bearer"],
        )
    ]
    
    expires_in: Annotated[
        int,
        Field(
            ...,
            ge=1,
            description="Время жизни access token в секундах (обычно 30 минут = 1800 сек)",
            examples=[1800, 3600],
        )
    ]
    
    refresh_expires_in: Annotated[
        int,
        Field(
            ...,
            ge=1,
            description="Время жизни refresh token в секундах (обычно 7 дней = 604800 сек)",
            examples=[604800, 2592000],
        )
    ]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJlbWFpbCI6ImpvaG4uZG9lQGV4YW1wbGUuY29tIiwiZXhwIjoxNzE3OTIyNjAwfQ...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MTg1MjY2MDB9...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                    "refresh_expires_in": 604800,
                }
            ]
        }
    }


class RefreshTokenRequest(BaseModel):
    """Запрос для обновления токенов по refresh token."""
    
    refresh_token: Annotated[
        str,
        Field(
            ...,
            description="Валидный refresh token, полученный при login или предыдущем refresh",
            examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MTg1MjY2MDB9..."],
        )
    ]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MTg1MjY2MDB9...",
                }
            ]
        }
    }


class ChangePasswordRequest(BaseModel):
    """Запрос для смены пароля аутентифицированного пользователя."""
    
    current_password: Annotated[
        str,
        Field(
            ...,
            min_length=8,
            max_length=100,
            description="Текущий пароль пользователя для подтверждения личности",
            examples=["CurrentPass123!"],
        )
    ]
    
    new_password: Annotated[
        str,
        Field(
            ...,
            min_length=8,
            max_length=100,
            description="Новый пароль (должен отличаться от текущего)",
            examples=["NewSecurePass456!"],
        )
    ]

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Проверка сложности нового пароля."""
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
                    "current_password": "CurrentPass123!",
                    "new_password": "NewSecurePass456!",
                }
            ]
        }
    }
