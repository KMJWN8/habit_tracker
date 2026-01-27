from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid
from datetime import datetime
from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Схема для запроса входа"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class RegisterRequest(BaseModel):
    """Схема для запроса регистрации"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class Token(BaseModel):
    """Базовая схема токена"""
    access_token: str
    token_type: str = "bearer"


class TokenResponse(Token):
    """Расширенная схема ответа с токенами"""
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None  # В секундах
    refresh_expires_in: Optional[int] = None  # В секундах
    user: Optional[UserResponse] = None


class RegisterResponse(TokenResponse):
    """Ответ при регистрации"""
    pass


class LoginResponse(TokenResponse):
    """Ответ при входе"""
    pass


class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена"""
    refresh_token: str


class RefreshTokenResponse(Token):
    """Ответ при обновлении токена"""
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None


class ChangePasswordRequest(BaseModel):
    """Запрос на смену пароля"""
    current_password: str = Field(..., min_length=8, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)


class ForgotPasswordRequest(BaseModel):
    """Запрос на восстановление пароля"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Запрос на сброс пароля"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)