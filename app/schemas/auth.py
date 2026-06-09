from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class Token(BaseModel):
    """Базовая схема токена"""

    access_token: str
    token_type: str = "bearer"


class TokenResponse(Token):
    """Расширенная схема ответа с токенами"""

    refresh_token: str | None = None
    expires_in: int | None = None  # В секундах
    refresh_expires_in: int | None = None  # В секундах
    user: UserResponse | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(Token):
    refresh_token: str | None = None
    expires_in: int | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
