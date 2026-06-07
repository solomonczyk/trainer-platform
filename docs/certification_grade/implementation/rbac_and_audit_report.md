# RBAC and Audit Report

**Document ID:** CGSF-IMPL-RBAC-001  
**Date:** 2026-06-07  

## Roles Implemented

7 certification-specific roles defined in `certification_core/services/authorization.py`:

1. **platform_admin** — Full system access, role management
2. **domain_owner** — Manage domain packs, competencies, blueprints, knowledge sources, items, rubrics, lifecycle
3. **content_author** — Create and edit items and rubrics
4. **expert_reviewer** — Review items, manage lifecycle transitions
5. **psychometric_reviewer** — Manage calibration lifecycle transitions
6. **qa_reviewer** — Read-only QA access with audit
7. **read_only_auditor** — Read-only audit access

## Permission Model

Permissions are string-based (e.g., `certification:read`, `certification:write`). Each role maps to a set of permissions. Learners (guest/unauthenticated) only have `certification:read`.

## Audit Service

Implemented in `certification_core/audit/service.py`.

**Features:**
- Append-only design — no update/delete/purge methods
- SHA-256 before/after hashing for state change tracking
- Specialized methods: `record_create`, `record_update`, `record_transition`, `record_delete`
- Generic `record` method for custom actions
- Query interface with filters: entity_type, entity_id, actor_id, action, date range
- Paginated results
- `entity_version` tracking for versioned entities

**Audit Event Schema:**
```json
{
  "audit_event_id": "aud-{uuid12}",
  "entity_type": "item|competency_framework|exam_blueprint|knowledge_source|rubric|domain_pack",
  "entity_id": "...",
  "entity_version": "1",
  "action": "create|update|transition:draft->generated|delete",
  "actor_id": "user_123",
  "actor_role": "content_author",
  "reason": "Status transition from draft to generated",
  "before_hash": "abc123...",
  "after_hash": "def456..."
}
```

**Security:**
- No secrets, tokens, or raw submissions stored
- No authentication tokens in audit events
- Hash-based state verification (not full state storage)
- Append-only enforced by API design
- Audit query requires `certification:audit:read` permission
