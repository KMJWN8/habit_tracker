from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.logger import get_logger


logger = get_logger(__name__)

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_URL_PREFIX}/auth/login", auto_error=False
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def _create_token(
    data: dict[str, Any], expires_delta: timedelta, token_type: str = "access"
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        **data,
        "exp": expire,
        "type": token_type
    }

    return jwt.encode(
        payload, settings.auth.SECRET_KEY, algorithm=settings.auth.ALGORITHM
    )


def create_access_token(data: dict[str, Any]) -> str:
    expires_delta = timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(data, expires_delta, "access")


def create_refresh_token(data: dict[str, Any]) -> str:
    expires_delta = timedelta(days=settings.auth.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(data, expires_delta, "refresh")


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token, settings.auth.SECRET_KEY, algorithms=[settings.auth.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token decoding failed: Token has expired.")
        return None
    except jwt.InvalidTokenError:
        logger.error("Token decoding failed: Token is invalid, corrupted or tampered with")
        return None
