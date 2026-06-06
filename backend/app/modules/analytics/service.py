"""Business-logic layer for analytics event recording with sanitisation."""

from __future__ import annotations

import re
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import AnalyticsEvent, FeatureFlag
from app.modules.analytics.repository import AnalyticsRepository

# ---------------------------------------------------------------------------
# Allowlist of safe event types
# ---------------------------------------------------------------------------
SAFE_EVENT_TYPES: frozenset[str] = frozenset(
    {
        "page_view",
        "session_start",
        "session_end",
        "scenario_start",
        "scenario_started",
        "scenario_complete",
        "evaluation_complete",
        "evaluation_result_viewed",
        "trainer_enroll",
        "trainer_unenroll",
        "help_viewed",
        "hint_shown",
        "retry_attempt",
        "modal_opened",
        "modal_closed",
        "copy_action",
        "link_click",
        "search_query",
        "filter_applied",
        "locale_changed",
        "domain_catalog_viewed",
        "answer_submitted",
        "user_registered",
        "landing_viewed",
        "answer_evaluated",
        "ba_trainer_opened",
        "ba_module_opened",
        "ba_activity_started",
        "explanation_viewed",
        "module_progress_viewed",
        # BA Phase 2 events
        "ba_phase2_scenario_opened",
        "ba_phase2_scenario_started",
        "ba_phase2_submission_created",
        "ba_phase2_evaluation_started",
        "ba_phase2_evaluation_completed",
        "ba_phase2_evaluation_failed",
        "ba_phase2_result_viewed",
        "ba_phase2_retry_requested",
    }
)

# ---------------------------------------------------------------------------
# Keys whose *values* are blocked from properties
# ---------------------------------------------------------------------------
BLOCKED_PROPERTY_KEYS: frozenset[str] = frozenset(
    {
        "answer",
        "answer_text",
        "content",
    }
)

# ---------------------------------------------------------------------------
# Sensitive key patterns — both key names and string values are scanned
# ---------------------------------------------------------------------------
SENSITIVE_KEY_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"api_key", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"credential", re.IGNORECASE),
    re.compile(r"auth_token", re.IGNORECASE),
    re.compile(r"access_key", re.IGNORECASE),
    re.compile(r"private_key", re.IGNORECASE),
)


def _is_sensitive_key(key: str) -> bool:
    """Check whether a property key matches a known sensitive pattern."""
    return any(p.search(key) for p in SENSITIVE_KEY_PATTERNS)


def _contains_sensitive_value(value: object) -> bool:
    """Check whether a string value looks like a credential."""
    if not isinstance(value, str):
        return False
    # Heuristic: long base64-ish or hex strings that look like keys/tokens
    if len(value) < 16:
        return False
    # Flag if the value is mostly alphanumeric with high entropy
    alpha_ratio = sum(c.isalnum() or c in "-_" for c in value) / max(len(value), 1)
    return alpha_ratio > 0.85 and len(value) < 2048


def _sanitise_properties(properties: Optional[dict]) -> dict:
    """Strip blocked and sensitive data from the properties dict."""
    if not properties:
        return {}

    safe: dict = {}
    for key, value in properties.items():
        # Block known unsafe keys
        if key.lower() in BLOCKED_PROPERTY_KEYS:
            continue
        # Block keys matching sensitive patterns
        if _is_sensitive_key(key):
            continue
        # Block values that look like credentials
        if _contains_sensitive_value(value):
            continue
        # Truncate overly long string values
        if isinstance(value, str) and len(value) > 10_000:
            value = value[:10_000]
        safe[key] = value
    return safe


class AnalyticsService:
    """Orchestrates event recording with feature-flag and safety checks."""

    @staticmethod
    async def record_event(
        db: AsyncSession,
        user_id: str,
        event_type: str,
        session_id: Optional[str],
        trainer_slug: Optional[str],
        scenario_id: Optional[str],
        properties: Optional[dict],
    ) -> Optional[AnalyticsEvent]:
        """
        Record an analytics event after validation and sanitisation.

        Returns ``None`` when the event is silently dropped (feature flag
        disabled or disallowed event type).
        """
        # --- Feature-flag guard ---
        ff_result = await db.execute(
            select(FeatureFlag).where(
                FeatureFlag.flag_key == "ff_analytics_enabled"
            )
        )
        flag: Optional[FeatureFlag] = ff_result.scalar_one_or_none()

        if flag is None:
            # Fall back to the application-level setting when the DB flag
            # hasn't been seeded yet.
            if not settings.ff_analytics_enabled:
                return None
        elif not flag.enabled:
            return None

        # --- Event-type validation ---
        if event_type not in SAFE_EVENT_TYPES:
            return None

        # --- Sanitise payload ---
        safe_properties = _sanitise_properties(properties)

        # --- Persist ---
        event = await AnalyticsRepository.create_event(
            db,
            user_id,
            event_type,
            {
                "session_id": session_id,
                "trainer_slug": trainer_slug,
                "scenario_id": scenario_id,
                "properties": safe_properties,
            },
        )
        return event
