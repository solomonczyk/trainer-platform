# Generated Item Human Review — Known Issues

**Layer 004 — Human Review Infrastructure Regression Closeout**

---

## Known Issues

### KHI-004-001: PostgreSQL Container Stability During Long Test Runs

**Status:** Mitigated
**Severity:** Low
**Layer:** Test Infrastructure

The `trainer-migration-pg` container may receive external shutdown signals during long (>20 min) test suite runs. When the container is shut down mid-suite, migration execution tests that run after ~85% suite completion fail with:

```
Error response from daemon: container <id> is not running
```

**Root Cause:** External process sent a PostgreSQL fast shutdown signal during the full certification-core suite run. The container exits cleanly (exit code 0) but is no longer available for subsequent migration tests.

**Mitigation:** Restart the container (`docker start trainer-migration-pg`) before running migration tests. The migration tests themselves are stable and pass independently.

**Recommendation:** Implement a pytest session-scoped fixture that verifies container health before test collection, or add a Docker health check.

### KHI-004-002: Human Review Layer 004 Tests Not Yet Implemented

**Status:** Acknowledged (not a bug)
**Severity:** N/A
**Layer:** Testing

The human review focused tests listed in the Layer 004 specification do not yet exist:

- test_human_review_contract.py
- test_human_review_rbac.py
- test_human_review_independence.py
- test_human_review_package.py
- test_human_review_criteria.py
- test_human_review_decision.py
- test_human_review_handoff_routing.py
- test_human_review_candidate_immutability.py
- test_human_review_audit.py
- test_human_review_downstream_guards.py

These test files will be created during the Human Review Layer 004 implementation phase.

### KHI-004-003: Migration 007 Not Implemented

**Status:** Acknowledged
**Severity:** N/A
**Layer:** Migrations

Alembic head is revision 006. Migration 007 test file (`test_migration_007_execution.py`) and version script do not exist in the codebase. The closeout spec references migration 007 tests, but no corresponding implementation exists.

### KHI-004-004: Database Connection Uses Test Credentials in Plain Text

**Status:** Accepted (test environment only)
**Severity:** Low
**Layer:** Test Infrastructure

The migration tests use `docker exec` to access PostgreSQL with plain-text credentials (`trainer`/`trainer_test_password`). These credentials are for the isolated test container only and are not exposed via `.env` files or committed configuration.
