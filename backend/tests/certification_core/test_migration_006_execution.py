"""Executable test for migration 006 full cycle: upgrade → downgrade → upgrade.

Proves the real PostgreSQL migration cycle against the database.
Connects via the POSTGRES_MIGRATION_URL env var or docker exec.
The cycle verified:
    alembic upgrade head  → current=006
    alembic downgrade 005  → current=005
    alembic upgrade head  → current=006
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

MIGRATION_006_TABLES: list[str] = [
    "cert_generation_requests",
    "cert_generation_source_bindings",
    "cert_generation_provider_runs",
    "cert_generation_raw_responses",
    "cert_generated_candidates",
    "cert_candidate_validation_runs",
    "cert_candidate_validation_results",
    "cert_candidate_provenance",
    "cert_candidate_review_handoffs",
]


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
    """Run SQL against PostgreSQL and return rows."""
    if not _HAS_PG and not MIGRATION_URL:
        # Try docker exec
        cmd = [
            "docker", "exec", "trainer-migration-pg",
            "psql", "-U", "trainer", "-d", "trainer_platform",
            "-t", "-A", "-F", "|",
            "-c", sql,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    else:
        cmd = [
            "psql",
            MIGRATION_URL,
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


def _tables_exist() -> set[str]:
    """Get all public table names."""
    rows = _pg(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' ORDER BY table_name"
    )
    return {r for r in rows}


def _table_has_columns(table: str) -> set[str]:
    """Get column names for a table."""
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
    """Fail fast if PostgreSQL is not reachable."""
    try:
        result = _pg("SELECT 1 AS ok")
        assert result and result[0] == "1"
    except Exception as exc:
        pytest.fail(f"PostgreSQL unreachable: {exc}")
    return True


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMigration006Execution:
    """Prove the full migration 006 cycle on real PostgreSQL."""

    def test_cycle_upgrade_downgrade_upgrade(self, pg_available):
        """Full cycle: upgrade head → 006 → downgrade 005 → upgrade head → 006."""
        # Step 1: verify we start at 006
        rev = _current_revision()
        assert rev == "006" or rev.startswith("006"), f"Expected 006, got {rev}"

        # Snapshot 006 tables
        all_tables = _tables_exist()
        for table in MIGRATION_006_TABLES:
            assert table in all_tables, f"Table {table} missing before downgrade"
            cols = _table_has_columns(table)
            assert len(cols) > 2, f"Table {table} has insufficient columns"

        # Count cert_ tables
        cert_tables_before = {t for t in all_tables if t.startswith("cert_")}

        # Step 2: downgrade to 005
        _alembic("downgrade", "005")
        rev = _current_revision()
        assert rev == "005" or rev.startswith("005"), f"Expected 005, got {rev}"

        # Verify 006 tables removed
        tables_after_downgrade = _tables_exist()
        for table in MIGRATION_006_TABLES:
            assert table not in tables_after_downgrade, f"Table {table} still present after downgrade"

        # Step 3: upgrade back to head (006)
        _alembic("upgrade", "head")
        rev = _current_revision()
        assert rev == "006" or rev.startswith("006"), f"Expected 006, got {rev}"

        # Verify 006 tables restored
        tables_after_upgrade = _tables_exist()
        for table in MIGRATION_006_TABLES:
            assert table in tables_after_upgrade, f"Table {table} missing after second upgrade"

        # Verify no duplicate tables
        cert_tables_after = {t for t in tables_after_upgrade if t.startswith("cert_")}
        assert len(cert_tables_after) == len(cert_tables_before), \
            f"cert_ table count changed: {len(cert_tables_before)} → {len(cert_tables_after)}"

        # Verify alembic version
        rows = _pg("SELECT version_num FROM alembic_version")
        assert len(rows) == 1, f"Expected 1 row in alembic_version, got {len(rows)}"
        assert rows[0] == "006", f"Expected '006', got '{rows[0]}'"

    def test_existing_certification_tables_preserved(self, pg_available):
        """Existing cert_ tables must be preserved after the cycle."""
        tables = _tables_exist()
        core_tables = [
            "cert_audit_events", "cert_exam_blueprints", "cert_competency_frameworks",
            "cert_items", "cert_item_versions", "cert_item_families",
            "cert_knowledge_sources", "cert_item_rotation_policies",
            "cert_item_exception_approvals",
        ]
        for table in core_tables:
            assert table in tables, f"Core table {table} missing"

    def test_ba_qa_tables_preserved(self, pg_available):
        """BA/QA tables must be preserved after the cycle."""
        tables = _tables_exist()
        ba_tables = [
            "activities", "deterministic_evaluations", "scenarios",
            "trainer_products", "trainer_progress", "user_trainer_enrollments",
        ]
        for table in ba_tables:
            assert table in tables, f"BA/QA table {table} missing"

    def test_alembic_revision_matches_006(self, pg_available):
        """Final alembic revision must be 006."""
        rev = _current_revision()
        assert rev == "006" or rev.startswith("006"), f"Expected 006, got {rev}"

    def test_database_queryable(self, pg_available):
        """Database must be queryable after the full cycle."""
        rows = _pg("SELECT 1 AS ok")
        assert rows[0] == "1"
