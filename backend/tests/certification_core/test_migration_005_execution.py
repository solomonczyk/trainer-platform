"""Executable test for migration 005 full cycle: upgrade → downgrade → upgrade.

Proves the real PostgreSQL migration cycle against the database in the
Docker container *trainer-item-bank-migration-005*.  The test connects
via ``docker exec`` and psql, so no additional Python database drivers
are needed beyond what Alembic already provides.

The cycle verified:
    alembic upgrade head  → current=005
    alembic downgrade 004  → current=004
    alembic upgrade head  → current=005

Environment variable ``POSTGRES_MIGRATION_URL`` must be set to the
*sync* connection URL when running outside the container session.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

# Set once per module
MIGRATION_URL = os.environ.get("POSTGRES_MIGRATION_URL")
_HAS_PG = MIGRATION_URL is not None

BACKEND = Path(__file__).resolve().parent.parent.parent

MIGRATION_005_COLUMNS: dict[str, list[str]] = {
    "cert_item_rotation_policies": [
        "allowed_locales",
        "domain_balance_quotas",
        "competency_balance_quotas",
        "difficulty_balance_ratios",
        "max_items_per_family",
        "recent_use_window_days",
        "exposure_threshold",
    ],
    "cert_item_exception_approvals": [
        "item_version_id",
        "scope",
        "requested_by",
        "requester_role",
        "first_approver",
        "first_approval_timestamp",
        "second_approval_timestamp",
        "status",
        "audit_correlation_id",
    ],
}

MIGRATION_005_INDEXES: list[str] = [
    "idx_iea_status",
    "ix_cert_item_exception_approvals_item_version_id",
    "ix_cert_item_exception_approvals_status",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _alembic(*args: str) -> str:
    """Run ``alembic <args>`` in the backend directory and return stdout."""
    env = {**os.environ, "DATABASE_URL": MIGRATION_URL} if _HAS_PG else os.environ.copy()
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=str(BACKEND),
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        pytest.fail(f"alembic {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout + result.stderr


def _pg(sql: str) -> list[tuple]:
    """Run SQL against PostgreSQL via docker exec + psql and return rows."""
    cmd = [
        "docker", "exec", "trainer-item-bank-migration-005",
        "psql", "-U", "trainer", "-d", "trainer_item_bank_closeout",
        "-t", "-A", "-F", "|",
        "-c", sql,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        pytest.fail(f"psql command failed:\n{result.stderr}")
    rows = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("("):
            continue
        parts = [p.strip() for p in line.split("|")]
        rows.append(tuple(parts) if len(parts) > 1 else parts[0])
    return rows


def _current_revision() -> str:
    """Return the current Alembic revision label."""
    out = _alembic("current")
    for line in out.splitlines():
        line = line.strip()
        if line and not line.startswith("INFO") and not line.startswith("WARN"):
            return line
    pytest.fail(f"Could not parse alembic current output:\n{out}")


def _columns_for(table: str) -> set[str]:
    rows = _pg(
        "SELECT column_name FROM information_schema.columns "
        f"WHERE table_schema = 'public' AND table_name = '{table}'"
    )
    return {r for r in rows}


# ---------------------------------------------------------------------------
# Connection guard
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def pg_available():
    """Fail fast if PostgreSQL is not reachable via docker exec."""
    try:
        result = _pg("SELECT 1 AS ok")
        assert result and result[0] == "1"
    except Exception as exc:
        pytest.fail(f"PostgreSQL unreachable via docker exec: {exc}")
    return True


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMigration005Execution:
    """Prove the full migration 005 cycle on real PostgreSQL."""

    def test_cycle_upgrade_downgrade_upgrade(self, pg_available):
        """Full cycle: upgrade head → 005 → downgrade 004 → upgrade head → 005."""
        # Step 1: verify we start at 005
        rev = _current_revision()
        assert rev == "005" or rev.startswith("005"), f"Expected 005, got {rev}"

        # Snapshot 005 columns and indexes
        cols_005 = {
            t: _columns_for(t)
            for t in MIGRATION_005_COLUMNS
        }
        idxs_005 = set()
        for t in MIGRATION_005_COLUMNS:
            rows = _pg(f"SELECT indexname FROM pg_indexes WHERE tablename = '{t}'")
            idxs_005.update(r for r in rows)
        for expected_idx in MIGRATION_005_INDEXES:
            assert expected_idx in idxs_005, f"Index {expected_idx} missing before downgrade"

        for table, expected_cols in MIGRATION_005_COLUMNS.items():
            for col in expected_cols:
                assert col in cols_005[table], f"Column {table}.{col} missing before downgrade"

        # Step 2: downgrade to 004
        _alembic("downgrade", "004")
        rev = _current_revision()
        assert rev == "004" or rev.startswith("004"), f"Expected 004, got {rev}"

        # Verify 005 columns removed
        cols_004 = {
            t: _columns_for(t)
            for t in MIGRATION_005_COLUMNS
        }
        for table, expected_cols in MIGRATION_005_COLUMNS.items():
            for col in expected_cols:
                assert col not in cols_004[table], f"Column {table}.{col} still present after downgrade"

        # Verify 005 indexes removed
        idxs_004 = set()
        for t in MIGRATION_005_COLUMNS:
            rows = _pg(f"SELECT indexname FROM pg_indexes WHERE tablename = '{t}'")
            idxs_004.update(r for r in rows)
        for expected_idx in MIGRATION_005_INDEXES:
            assert expected_idx not in idxs_004, f"Index {expected_idx} still present after downgrade"

        # Step 3: upgrade back to head (005)
        _alembic("upgrade", "head")
        rev = _current_revision()
        assert rev == "005" or rev.startswith("005"), f"Expected 005, got {rev}"

        # Verify 005 columns restored
        cols_005_restored = {
            t: _columns_for(t)
            for t in MIGRATION_005_COLUMNS
        }
        for table, expected_cols in MIGRATION_005_COLUMNS.items():
            for col in expected_cols:
                assert col in cols_005_restored[table], f"Column {table}.{col} missing after second upgrade"

        # Verify 005 indexes restored
        idxs_005_restored = set()
        for t in MIGRATION_005_COLUMNS:
            rows = _pg(f"SELECT indexname FROM pg_indexes WHERE tablename = '{t}'")
            idxs_005_restored.update(r for r in rows)
        for expected_idx in MIGRATION_005_INDEXES:
            assert expected_idx in idxs_005_restored, f"Index {expected_idx} missing after second upgrade"

        # Verify no within-table duplicate columns
        for table in MIGRATION_005_COLUMNS:
            rows = _pg(
                "SELECT column_name, count(*) FROM information_schema.columns "
                f"WHERE table_schema = 'public' AND table_name = '{table}' "
                "GROUP BY column_name HAVING count(*) > 1"
            )
            assert len(rows) == 0, f"Duplicate columns found in {table}: {rows}"

        # Verify alembic version table has exactly one row = '005'
        rows = _pg("SELECT version_num FROM alembic_version")
        assert len(rows) == 1, f"Expected 1 row in alembic_version, got {len(rows)}"
        assert rows[0] == "005", f"Expected '005', got '{rows[0]}'"

    def test_all_tables_preserved_after_cycle(self, pg_available):
        """All 51 tables must remain after the cycle."""
        rows = _pg("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        names = {r for r in rows}
        assert len(names) == 51, f"Expected 51 tables, got {len(names)}"

        # Core contracts — spot check
        for core in ("cert_audit_events", "cert_exam_blueprints", "cert_item_rotation_policies",
                     "cert_item_exception_approvals", "cert_competency_frameworks",
                     "cert_items", "cert_item_versions"):
            assert core in names, f"Core table {core} missing"

        # BA/QA tables
        for ba in ("activities", "deterministic_evaluations", "scenarios", "tracks",
                   "trainer_products", "trainer_progress", "trainer_versions",
                   "user_trainer_enrollments"):
            assert ba in names, f"BA/QA table {ba} missing"

    def test_core_contract_table_count(self, pg_available):
        """22 cert_ tables must exist."""
        rows = _pg("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'cert_%'")
        assert rows[0] == "22", f"Expected 22 cert_ tables, got {rows[0]}"

    def test_alembic_revision_matches_005(self, pg_available):
        """Final alembic revision must be 005."""
        rev = _current_revision()
        assert rev == "005" or rev.startswith("005"), f"Expected 005, got {rev}"

    def test_database_queryable(self, pg_available):
        """Database must be queryable after the full cycle."""
        rows = _pg("SELECT 1 AS ok")
        assert rows[0] == "1"
