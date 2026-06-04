"""Security utilities — JWT, password hashing, role checks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.errors import UnauthorizedError, ForbiddenError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(
    user_id: str,
    role: str = "registered_user",
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = {
        "sub": user_id,
        "role": role,
        "iat": datetime.now(timezone.utc),
    }
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise UnauthorizedError("Invalid or expired token")


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """Extract user_id from Bearer token. Returns 'guest' if no token."""
    if credentials is None:
        return "guest"
    payload = decode_token(credentials.credentials)
    return payload.get("sub", "guest")


async def get_current_user_id_required(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Extract user_id — requires valid token."""
    if credentials is None:
        raise UnauthorizedError("Authentication required")
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")
    return user_id


async def get_current_user_role(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Extract user role from token."""
    if credentials is None:
        return "guest"
    payload = decode_token(credentials.credentials)
    return payload.get("role", "guest")


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Require admin role."""
    payload = decode_token(credentials.credentials)
    if payload.get("role") != "admin":
        raise ForbiddenError("Admin access required")
    return payload.get("sub", "")
