from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Dict

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def _create_token(
    data: Dict[str, Any],
    expires_delta: timedelta,
    token_type: str = "access"
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": token_type})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_access_token(data: Dict[str, Any]) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(data, expires_delta, "access")


def create_refresh_token(data: Dict[str, Any]) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(data, expires_delta, "refresh")


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        return None
