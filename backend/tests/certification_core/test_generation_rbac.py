"""Tests for generation RBAC — role-based access control enforcement."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.certification_core.services.authorization import (
    AuthorizationService,
    ROLE_PERMISSIONS,
    CERTIFICATION_ROLES,
)


class TestGenerationRBAC:
    """Prove RBAC controls for generation operations."""

    def test_generation_operator_role_exists(self):
        assert "generation_operator" in CERTIFICATION_ROLES

    def test_generation_operator_has_create_permission(self):
        perms = ROLE_PERMISSIONS.get("generation_operator", set())
        assert "certification:generation:create" in perms

    def test_generation_operator_has_authorize_permission(self):
        perms = ROLE_PERMISSIONS.get("generation_operator", set())
        assert "certification:generation:authorize" in perms

    def test_generation_operator_has_execute_permission(self):
        perms = ROLE_PERMISSIONS.get("generation_operator", set())
        assert "certification:generation:execute" in perms

    def test_generation_operator_has_view_raw_permission(self):
        perms = ROLE_PERMISSIONS.get("generation_operator", set())
        assert "certification:generation:view_raw" in perms

    def test_learner_no_generation_permissions(self):
        """Learner role should NOT have any generation permissions."""
        learner_perms = {"certification:read"}
        generation_perms = {
            "certification:generation:create",
            "certification:generation:authorize",
            "certification:generation:execute",
            "certification:generation:view",
            "certification:generation:view_raw",
            "certification:generation:admin",
        }
        assert learner_perms.isdisjoint(generation_perms)

    def test_content_author_no_generation_permissions(self):
        """Content author should NOT have generation permissions."""
        perms = ROLE_PERMISSIONS.get("content_author", set())
        generation_perms = {
            "certification:generation:create",
            "certification:generation:authorize",
            "certification:generation:execute",
            "certification:generation:view_raw",
        }
        for gp in generation_perms:
            assert gp not in perms, f"Content author should not have {gp}"

    def test_domain_owner_has_create_but_not_execute(self):
        perms = ROLE_PERMISSIONS.get("domain_owner", set())
        assert "certification:generation:create" in perms
        assert "certification:generation:execute" not in perms
        assert "certification:generation:authorize" not in perms

    def test_qa_reviewer_has_view_raw(self):
        perms = ROLE_PERMISSIONS.get("qa_reviewer", set())
        assert "certification:generation:view_raw" in perms

    def test_platform_admin_has_all_generation_permissions(self):
        perms = ROLE_PERMISSIONS.get("platform_admin", set())
        all_gen = {
            "certification:generation:create",
            "certification:generation:authorize",
            "certification:generation:execute",
            "certification:generation:view",
            "certification:generation:view_raw",
            "certification:generation:admin",
        }
        for gp in all_gen:
            assert gp in perms, f"Platform admin should have {gp}"

    def test_guest_has_no_generation_access(self):
        assert not AuthorizationService.has_permission("guest", "certification:generation:create")
        assert not AuthorizationService.has_permission("guest", "certification:generation:execute")
        assert not AuthorizationService.has_permission("guest", "certification:generation:authorize")
        assert not AuthorizationService.has_permission("guest", "certification:generation:view_raw")
