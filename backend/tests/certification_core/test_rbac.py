"""Tests for RBAC enforcement and learner answer key protection."""

from __future__ import annotations

import pytest
from app.certification_core.services.authorization import (
    AuthorizationService,
    CERTIFICATION_ROLES,
    ROLE_PERMISSIONS,
    LEARNER_PERMISSIONS,
    ANSWER_KEY_RESTRICTED_ROLES,
)


class TestCertificationRoles:
    """Certification role definition tests."""

    def test_required_roles_exist(self):
        required_roles = [
            "platform_admin",
            "domain_owner",
            "content_author",
            "expert_reviewer",
            "psychometric_reviewer",
            "qa_reviewer",
            "read_only_auditor",
        ]
        for role in required_roles:
            assert role in CERTIFICATION_ROLES, f"Required role '{role}' missing"

    def test_all_roles_have_permissions(self):
        for role in CERTIFICATION_ROLES:
            assert role in ROLE_PERMISSIONS, f"Role '{role}' has no permissions defined"
            assert len(ROLE_PERMISSIONS[role]) > 0


class TestAuthorizationService:
    """Authorization service tests."""

    def test_platform_admin_has_all_permissions(self):
        assert AuthorizationService.has_permission("platform_admin", "certification:admin")
        assert AuthorizationService.has_permission("platform_admin", "certification:read")
        assert AuthorizationService.has_permission("platform_admin", "certification:write")
        assert AuthorizationService.has_permission("platform_admin", "certification:audit:read")

    def test_domain_owner_can_manage(self):
        assert AuthorizationService.has_permission("domain_owner", "certification:write")
        assert AuthorizationService.has_permission("domain_owner", "certification:manage_domain_packs")

    def test_content_author_can_write_items(self):
        assert AuthorizationService.has_permission("content_author", "certification:write")
        assert AuthorizationService.has_permission("content_author", "certification:manage_items")

    def test_content_author_cannot_manage_lifecycle(self):
        assert not AuthorizationService.has_permission("content_author", "certification:manage_lifecycle")

    def test_read_only_auditor_limited(self):
        assert AuthorizationService.has_permission("read_only_auditor", "certification:read")
        assert AuthorizationService.has_permission("read_only_auditor", "certification:audit:read")
        assert not AuthorizationService.has_permission("read_only_auditor", "certification:write")

    def test_guest_limited_permissions(self):
        assert AuthorizationService.has_permission("guest", "certification:read")
        assert not AuthorizationService.has_permission("guest", "certification:write")
        assert not AuthorizationService.has_permission("guest", "certification:audit:read")

    def test_check_permission_raises_for_missing(self):
        with pytest.raises(Exception) as exc_info:
            AuthorizationService.check_permission("guest", "certification:write")
        assert "403" in str(exc_info.value) or "ForbiddenError" in type(exc_info.value).__name__

    def test_unknown_role_has_no_permissions(self):
        assert not AuthorizationService.has_permission("unknown_role", "certification:read")
        assert not AuthorizationService.has_permission("unknown_role", "certification:write")


class TestLearnerAnswerKeyProtection:
    """Tests for answer key protection — learners must not see answer keys."""

    def test_read_only_auditor_cannot_read_answer_keys(self):
        assert not AuthorizationService.can_read_answer_keys("read_only_auditor")

    def test_qa_reviewer_cannot_read_answer_keys(self):
        assert not AuthorizationService.can_read_answer_keys("qa_reviewer")

    def test_admin_can_read_answer_keys(self):
        assert AuthorizationService.can_read_answer_keys("platform_admin")

    def test_domain_owner_can_read_answer_keys(self):
        assert AuthorizationService.can_read_answer_keys("domain_owner")

    def test_learner_cannot_read_answer_keys(self):
        assert not AuthorizationService.can_read_answer_keys("guest")

    def test_answer_key_restricted_roles_defined(self):
        assert "read_only_auditor" in ANSWER_KEY_RESTRICTED_ROLES
        assert "qa_reviewer" in ANSWER_KEY_RESTRICTED_ROLES


class TestSelfApprovalPrevention:
    """Tests for self-approval prevention."""

    def test_content_author_cannot_self_approve(self):
        assert not AuthorizationService.can_self_approve("content_author")

    def test_domain_owner_cannot_self_approve(self):
        assert not AuthorizationService.can_self_approve("domain_owner")

    def test_expert_reviewer_can_self_approve(self):
        assert AuthorizationService.can_self_approve("expert_reviewer")

    def test_platform_admin_can_self_approve(self):
        assert AuthorizationService.can_self_approve("platform_admin")


class TestRolePermissionsComprehensive:
    """Comprehensive permission checks for all roles."""

    def test_admin_permissions(self):
        perms = ROLE_PERMISSIONS["platform_admin"]
        assert "certification:answer_key:read" in perms
        assert "certification:manage_roles" in perms

    def test_expert_reviewer_permissions(self):
        perms = ROLE_PERMISSIONS["expert_reviewer"]
        assert "certification:manage_lifecycle" in perms
        assert "certification:read" in perms
        assert "certification:write" not in perms

    def test_psychometric_reviewer_permissions(self):
        perms = ROLE_PERMISSIONS["psychometric_reviewer"]
        assert "certification:manage_lifecycle" in perms
        assert "certification:audit:read" in perms

    def test_no_role_has_everything(self):
        """No single role (except admin) should have all permissions."""
        for role in CERTIFICATION_ROLES:
            if role == "platform_admin":
                continue
            assert "certification:admin" not in ROLE_PERMISSIONS[role]
