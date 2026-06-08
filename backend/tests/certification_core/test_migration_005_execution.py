"""Executable test for migration 005 full cycle: upgrade → downgrade → upgrade.

Proves the real PostgreSQL migration cycle against the database.
Connects via the ``MIGRATION_DATABASE_URL`` (primary) or
``POSTGRES_MIGRATION_URL`` (fallback) environment variable, or falls
back to ``docker exec`` for local developer environments.

The cycle verified:
    alembic upgrade head  → current=005
    alembic downgrade 004  → current=004
    alembic upgrade head  → current=005
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Connection URL — highest precedence wins
#   1. MIGRATION_DATABASE_URL (primary, used in CI & explicit configs)
#   2. POSTGRES_MIGRATION_URL (legacy fallback)
#   3. None → docker exec trainer-migration-pg (local developer fallback)
# ---------------------------------------------------------------------------
MIGRATION_URL = os.environ.get("MIGRATION_DATABASE_URL") or os.environ.get("POSTGRES_MIGRATION_URL")
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

def _to_async_url(url: str) -> str:
    """Convert a sync ``postgresql://`` URL to async ``postgresql+asyncpg://``.

    Alembic's ``env.py`` uses ``create_async_engine`` which requires an async
    driver scheme.  If the URL already includes a driver (``+asyncpg``, etc.)
    it is returned unchanged.
    """
    if url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _alembic(*args: str) -> str:
    """Run ``alembic <args>`` in the backend directory and return stdout."""
    db_url = _to_async_url(MIGRATION_URL) if _HAS_PG else None
    env = {**os.environ, "DATABASE_URL": db_url} if _HAS_PG else os.environ.copy()
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
    """Run SQL against PostgreSQL and return rows.

    When ``MIGRATION_DATABASE_URL`` (or ``POSTGRES_MIGRATION_URL`` fallback)
    is set, connects via psycopg2 directly — no external ``psql`` binary needed.
    Falls back to ``docker exec`` for local developer environments.
    """
    if MIGRATION_URL:
        # Use Python psycopg2 driver — cross-platform, no psql dependency.
        try:
            import psycopg2
        except ImportError:
            pytest.fail(
                "psycopg2 is required when using MIGRATION_DATABASE_URL.\n"
                "Install: pip install psycopg2-binary"
            )
        try:
            conn = psycopg2.connect(MIGRATION_URL)
            cur = conn.cursor()
            cur.execute(sql)
            rows = []
            for row in cur.fetchall():
                if len(row) == 1:
                    rows.append(str(row[0]))
                else:
                    rows.append(tuple(str(v) for v in row))
            cur.close()
            conn.close()
            return rows
        except Exception as exc:
            pytest.fail(f"psycopg2 query failed: {exc}")

    # Docker exec fallback (local developer environment)
    cmd = [
        "docker", "exec", "trainer-migration-pg",
        "psql", "-U", "trainer", "-d", "trainer_platform",
        "-t", "-A", "-F", "|",
        "-c", sql,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        pytest.fail(f"docker exec psql failed:\n{result.stderr}")
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
        """Full cycle: start at head → downgrade 004 → upgrade head. Verify 005 migration artifacts."""
        # Step 1: record the current head revision
        head_rev = _current_revision()

        # Snapshot 005 columns and indexes before any downgrade
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

        # Step 3: upgrade back to head
        _alembic("upgrade", "head")
        rev = _current_revision()
        # After upgrade, head revision should be 006 (or whatever the current head is)
        HEAD_REVISION = "006"

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

        # Verify alembic version table has exactly one row at HEAD_REVISION
        rows = _pg("SELECT version_num FROM alembic_version")
        assert len(rows) == 1, f"Expected 1 row in alembic_version, got {len(rows)}"
        assert rows[0] == HEAD_REVISION, f"Expected '{HEAD_REVISION}', got '{rows[0]}'"

    def test_all_tables_preserved_after_cycle(self, pg_available):
        """All tables must remain after the cycle."""
        rows = _pg("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        names = {r for r in rows}
        # With migration 006 applied, total tables = 60 (31 cert_ + 29 non-cert)
        assert len(names) == 60, f"Expected 60 tables (005 + 006 inclusive), got {len(names)}"

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
        """31 cert_ tables must exist (22 from 005 + 9 from 006)."""
        rows = _pg("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'cert_%'")
        assert rows[0] == "31", f"Expected 31 cert_ tables, got {rows[0]}"

    def test_alembic_revision_matches_head(self, pg_available):
        """Final alembic revision must be current head (006)."""
        rev = _current_revision()
        assert rev == "006" or rev.startswith("006"), f"Expected 006 (head), got {rev}"

    def test_database_queryable(self, pg_available):
        """Database must be queryable after the full cycle."""
        rows = _pg("SELECT 1 AS ok")
        assert rows[0] == "1"
