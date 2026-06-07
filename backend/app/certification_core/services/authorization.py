"""Role-based authorization for certification-grade core entities.

Defines roles, permissions, and authorization checks for all certification-core operations.
"""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_403_FORBIDDEN

from app.core.security import decode_token
from app.core.errors import ForbiddenError

bearer_scheme = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# Certification-Grade Roles
# ---------------------------------------------------------------------------

CERTIFICATION_ROLES = [
    "platform_admin",
    "domain_owner",
    "content_author",
    "expert_reviewer",
    "psychometric_reviewer",
    "qa_reviewer",
    "read_only_auditor",
]

# Permission hierarchy (inherits from parent roles where applicable)
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "platform_admin": {
        "certification:admin",
        "certification:read",
        "certification:write",
        "certification:delete",
        "certification:manage_roles",
        "certification:manage_domain_packs",
        "certification:manage_competencies",
        "certification:manage_blueprints",
        "certification:manage_knowledge_sources",
        "certification:manage_items",
        "certification:manage_rubrics",
        "certification:manage_lifecycle",
        "certification:audit:read",
        "certification:answer_key:read",
    },
    "domain_owner": {
        "certification:read",
        "certification:write",
        "certification:manage_domain_packs",
        "certification:manage_competencies",
        "certification:manage_blueprints",
        "certification:manage_knowledge_sources",
        "certification:manage_items",
        "certification:manage_rubrics",
        "certification:manage_lifecycle",
        "certification:audit:read",
        "certification:answer_key:read",
    },
    "content_author": {
        "certification:read",
        "certification:write",
        "certification:manage_items",
        "certification:manage_rubrics",
    },
    "expert_reviewer": {
        "certification:read",
        "certification:manage_lifecycle",
        "certification:audit:read",
    },
    "psychometric_reviewer": {
        "certification:read",
        "certification:manage_lifecycle",
        "certification:audit:read",
    },
    "qa_reviewer": {
        "certification:read",
        "certification:audit:read",
    },
    "read_only_auditor": {
        "certification:read",
        "certification:audit:read",
    },
}

# Learner (not in CERTIFICATION_ROLES — only has minimal read access)
LEARNER_PERMISSIONS: set[str] = {
    "certification:read",
}

# Roles that cannot access answer keys
ANSWER_KEY_RESTRICTED_ROLES: set[str] = {"read_only_auditor", "qa_reviewer"}

# Roles that cannot self-approve expert-level gates
SELF_APPROVAL_RESTRICTED_ROLES: set[str] = {"content_author", "domain_owner"}


class AuthorizationService:
    """Authorization service for certification-core operations."""

    @staticmethod
    def get_role_from_token(credentials: Optional[HTTPAuthorizationCredentials]) -> str:
        """Extract role from JWT token or return 'guest'."""
        if credentials is None:
            return "guest"
        try:
            payload = decode_token(credentials.credentials)
            return payload.get("role", "guest")
        except Exception:
            return "guest"

    @staticmethod
    def get_user_id_from_token(credentials: Optional[HTTPAuthorizationCredentials]) -> str:
        """Extract user ID from token."""
        if credentials is None:
            return "guest"
        try:
            payload = decode_token(credentials.credentials)
            return payload.get("sub", "guest")
        except Exception:
            return "guest"

    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        """Check if a role has a specific permission."""
        if role == "guest":
            return permission in LEARNER_PERMISSIONS
        permissions = ROLE_PERMISSIONS.get(role, set())
        return permission in permissions

    @staticmethod
    def check_permission(role: str, permission: str) -> None:
        """Raise ForbiddenError if role lacks the permission."""
        if not AuthorizationService.has_permission(role, permission):
            raise ForbiddenError(f"Role '{role}' lacks required permission: {permission}")

    @staticmethod
    def can_read_answer_keys(role: str) -> bool:
        """Check if role can read answer keys."""
        if role in ANSWER_KEY_RESTRICTED_ROLES:
            return False
        return AuthorizationService.has_permission(role, "certification:answer_key:read")

    @staticmethod
    def can_self_approve(actor_role: str) -> bool:
        """Check if a role can self-approve items (content_author/domain_owner cannot)."""
        return actor_role not in SELF_APPROVAL_RESTRICTED_ROLES


async def get_current_certification_role(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """Dependency: extract current user role for certification endpoints."""
    return AuthorizationService.get_role_from_token(credentials)


async def require_certification_permission(
    permission: str,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """Dependency: require a specific certification permission."""
    role = AuthorizationService.get_role_from_token(credentials)
    AuthorizationService.check_permission(role, permission)
    return role
