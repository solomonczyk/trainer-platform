"""Auth-related Pydantic schemas for request/response validation."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 chars)")
    display_name: Optional[str] = Field(None, max_length=255, description="Display name")


class LoginRequest(BaseModel):
    """Request body for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Public user data returned in auth responses."""

    id: str
    email: str
    role: str
    is_active: bool
    email_verified: bool = False

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token response returned on successful auth."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class VerifyEmailRequest(BaseModel):
    """Request body for email verification."""

    token: str = Field(..., description="Email verification token")


class ResendVerificationRequest(BaseModel):
    """Request body for resending verification email."""

    email: EmailStr = Field(..., description="User email address")


class VerifyEmailResponse(BaseModel):
    """Response after successful email verification."""

    message: str = "Email verified successfully"
    email_verified: bool = True
