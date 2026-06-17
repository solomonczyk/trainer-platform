"""Backfill email_verified for users who existed before the verification column was added.

Migration 009 added email_verified with server_default=false, making ALL
pre-existing users appear unverified. This migration corrects that by marking
any user with account activity (login, enrollment, session, or attempt) as
verified.  New users created after 009 already go through the verification flow
and are left alone when truly unverified.

Revision ID: 010
Revises: 009
Create Date: 2026-06-17

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE users
        SET email_verified = TRUE
        WHERE id IN (
            SELECT DISTINCT user_id FROM user_trainer_enrollments
            UNION
            SELECT DISTINCT user_id FROM simulation_sessions
            UNION
            SELECT DISTINCT user_id FROM attempts
            UNION
            SELECT id FROM users WHERE last_login_at IS NOT NULL
        )
    """)


def downgrade() -> None:
    # No safe downgrade — we cannot distinguish "truly unverified" from users
    # who were backfilled to true, so this is intentionally a no-op.
    pass
