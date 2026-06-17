"""Add unique index on normalized email to prevent duplicates.

Migration 011 adds a unique index on lower(trim(email)) on the users table
to enforce case-insensitive email uniqueness at the database level.

Before creating the index, any existing duplicate normalized emails are
resolved by keeping the canonical (verified, or most recently active) user
and removing duplicates with data migration to the kept user.

Revision ID: 011
Revises: 010
Create Date: 2026-06-17

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # ── 1. Find and resolve duplicate normalized emails ──────────────
    duplicates = conn.execute(
        sa.text("""
            SELECT lower(trim(email)) AS normalized_email
            FROM users
            GROUP BY lower(trim(email))
            HAVING count(*) > 1
        """)
    ).fetchall()

    for (normalized_email,) in duplicates:
        users = conn.execute(
            sa.text("""
                SELECT id, email_verified, last_login_at
                FROM users
                WHERE lower(trim(email)) = :email
                ORDER BY
                    email_verified DESC,
                    last_login_at DESC NULLS LAST,
                    id ASC
            """),
            {"email": normalized_email},
        ).fetchall()

        if len(users) <= 1:
            continue

        keep_id = users[0][0]
        for dup in users[1:]:
            dup_id = dup[0]

            # Delete the duplicate's profile (1:1 relationship)
            conn.execute(
                sa.text("DELETE FROM user_profiles WHERE user_id = :uid"),
                {"uid": dup_id},
            )

            # Re-assign child records to the kept user
            for table in [
                "user_trainer_enrollments",
                "simulation_sessions",
                "attempts",
                "trainer_progress",
                "analytics_events",
            ]:
                conn.execute(
                    sa.text(
                        f"UPDATE {table} SET user_id = :keep WHERE user_id = :dup"
                    ),
                    {"keep": keep_id, "dup": dup_id},
                )

            # Delete the duplicate user
            conn.execute(
                sa.text("DELETE FROM users WHERE id = :uid"),
                {"uid": dup_id},
            )

    # ── 2. Create the unique index on normalized email ───────────────
    conn.execute(
        sa.text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email_normalized "
            "ON users (lower(trim(email)))"
        )
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_users_email_normalized")
