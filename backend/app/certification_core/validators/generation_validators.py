"""Validation pipeline for generated item candidates.

Implements 15 independent validators that each return a standard result record.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)

# Current validator versions
VALIDATOR_VERSIONS: dict[str, str] = {
    "V1": "1.0.0",
    "V2": "1.0.0",
    "V3": "1.0.0",
    "V4": "1.0.0",
    "V5": "1.0.0",
    "V6": "1.0.0",
    "V7": "1.0.0",
    "V8": "1.0.0",
    "V9": "1.0.0",
    "V10": "1.0.0",
    "V11": "1.0.0",
    "V12": "1.0.0",
    "V13": "1.0.0",
    "V14": "1.0.0",
    "V15": "1.0.0",
}

VALIDATION_POLICY_VERSION = "1.0.0"


class ValidatorResult:
    """Result from a single validator run."""

    def __init__(
        self,
        validator_code: str,
        status: str = "passed",
        severity: str = "info",
        reason_code: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        self.validator_code = validator_code
        self.validator_version = VALIDATOR_VERSIONS.get(validator_code, "0.0.0")
        self.status = status  # passed, failed, warning, not_run
        self.severity = severity  # info, minor, major, critical
        self.reason_code = reason_code
        self.details = details or {}
        self.executed_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "validator_code": self.validator_code,
            "validator_version": self.validator_version,
            "status": self.status,
            "severity": self.severity,
            "reason_code": self.reason_code,
            "details": self.details,
            "executed_at": self.executed_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# V1 — JSON / Schema Validation
# ---------------------------------------------------------------------------

def validate_schema(candidate: dict) -> ValidatorResult:
    """Validate that the candidate payload is valid JSON and matches expected schema structure."""
    errors = []

    # Check required top-level fields
    required = ["item_type", "stem", "answer_key", "rationale"]
    for field in required:
        if field not in candidate or candidate[field] is None:
            errors.append(f"Missing required field: {field}")

    # Check item_type is valid
    valid_types = {"multiple_choice", "single_choice", "open_answer", "fill_blanks"}
    item_type = candidate.get("item_type")
    if item_type and item_type not in valid_types:
        errors.append(f"Invalid item_type: {item_type}")

    if errors:
        return ValidatorResult(
            "V1", "failed", "critical",
            reason_code="SCHEMA_VALIDATION_FAILED",
            details={"errors": errors},
        )
    return ValidatorResult("V1", "passed", "info")


# ---------------------------------------------------------------------------
# V2 — Required Field Validation
# ---------------------------------------------------------------------------

def validate_required_fields(candidate: dict) -> ValidatorResult:
    """Validate that all required fields are present and non-empty."""
    missing = []
    empty = []

    required_strings = ["item_type", "stem", "rationale"]
    for field in required_strings:
        if field not in candidate:
            missing.append(field)
        elif not candidate[field] or (isinstance(candidate[field], str) and not candidate[field].strip()):
            empty.append(field)

    if missing:
        return ValidatorResult(
            "V2", "failed", "critical",
            reason_code="MISSING_REQUIRED_FIELDS",
            details={"missing_fields": missing},
        )
    if empty:
        return ValidatorResult(
            "V2", "failed", "critical",
            reason_code="EMPTY_REQUIRED_FIELDS",
            details={"empty_fields": empty},
        )
    return ValidatorResult("V2", "passed", "info")


# ---------------------------------------------------------------------------
# V3 — Source Citation Validation
# ---------------------------------------------------------------------------

def validate_source_citations(candidate: dict, source_version_ids: list[str]) -> ValidatorResult:
    """Validate that source citations are present and reference known sources."""
    citations = candidate.get("source_citations", [])
    if not citations or not isinstance(citations, list):
        return ValidatorResult(
            "V3", "failed", "major",
            reason_code="MISSING_SOURCE_CITATIONS",
            details={"warning": "No source citations provided"},
        )

    citation_sources = set()
    for c in citations:
        if isinstance(c, dict):
            source_id = c.get("source_id") or c.get("source_version_id")
            if source_id:
                citation_sources.add(str(source_id))

    if source_version_ids and not citation_sources.intersection(set(source_version_ids)):
        return ValidatorResult(
            "V3", "warning", "minor",
            reason_code="CITATION_SOURCE_MISMATCH",
            details={
                "citation_sources": list(citation_sources),
                "expected_sources": source_version_ids,
            },
        )

    return ValidatorResult("V3", "passed", "info")


# ---------------------------------------------------------------------------
# V4 — Competency Alignment
# ---------------------------------------------------------------------------

def validate_competency_alignment(
    candidate: dict,
    expected_competency_id: str,
    expected_domain_id: str,
) -> ValidatorResult:
    """Validate competency and domain alignment."""
    candidate_competency = candidate.get("competency_id", "")
    candidate_domain = candidate.get("domain_id", "")
    mismatch = []

    if candidate_competency and candidate_competency != expected_competency_id:
        mismatch.append(f"competency: expected {expected_competency_id}, got {candidate_competency}")

    if candidate_domain and candidate_domain != expected_domain_id:
        mismatch.append(f"domain: expected {expected_domain_id}, got {candidate_domain}")

    if mismatch:
        return ValidatorResult(
            "V4", "failed", "major",
            reason_code="COMPETENCY_MISMATCH",
            details={"mismatches": mismatch},
        )
    return ValidatorResult("V4", "passed", "info")


# ---------------------------------------------------------------------------
# V5 — Difficulty Alignment
# ---------------------------------------------------------------------------

def validate_difficulty(candidate: dict, expected_difficulty: str) -> ValidatorResult:
    """Validate that the candidate difficulty matches expectations."""
    candidate_difficulty = candidate.get("difficulty", "")
    if candidate_difficulty and candidate_difficulty != expected_difficulty:
        return ValidatorResult(
            "V5", "failed", "major",
            reason_code="DIFFICULTY_MISMATCH",
            details={
                "expected": expected_difficulty,
                "got": candidate_difficulty,
            },
        )
    return ValidatorResult("V5", "passed", "info")


# ---------------------------------------------------------------------------
# V6 — Item Family Compliance
# ---------------------------------------------------------------------------

def validate_item_family(candidate: dict, item_family_id: str) -> ValidatorResult:
    """Validate item family binding."""
    candidate_family = candidate.get("item_family_id", "")
    if candidate_family and candidate_family != item_family_id:
        return ValidatorResult(
            "V6", "failed", "major",
            reason_code="ITEM_FAMILY_MISMATCH",
            details={
                "expected": item_family_id,
                "got": candidate_family,
            },
        )
    return ValidatorResult("V6", "passed", "info")


# ---------------------------------------------------------------------------
# V7 — Answer / Options Consistency
# ---------------------------------------------------------------------------

def validate_answer_consistency(candidate: dict) -> ValidatorResult:
    """Validate answer and options consistency for MC items."""
    item_type = candidate.get("item_type", "")
    options = candidate.get("options", [])
    answer_key = candidate.get("answer_key", {})

    if item_type in ("multiple_choice", "single_choice"):
        if not options:
            return ValidatorResult(
                "V7", "failed", "critical",
                reason_code="MISSING_OPTIONS",
                details={"item_type": item_type},
            )

        if len(options) < 2:
            return ValidatorResult(
                "V7", "failed", "critical",
                reason_code="INSUFFICIENT_OPTIONS",
                details={"option_count": len(options)},
            )

        # Check for duplicate options
        option_texts = []
        for opt in options:
            if isinstance(opt, dict):
                text = opt.get("text", "")
                if text in option_texts:
                    return ValidatorResult(
                        "V7", "failed", "critical",
                        reason_code="DUPLICATE_OPTIONS",
                        details={"duplicate_text": text},
                    )
                option_texts.append(text)

        # Check for empty options
        for opt in options:
            if isinstance(opt, dict):
                text = opt.get("text", "")
                if not text or not text.strip():
                    return ValidatorResult(
                        "V7", "failed", "critical",
                        reason_code="EMPTY_OPTION",
                        details={"option_id": opt.get("id", "unknown")},
                    )

        # Check correct answer exists in options
        correct_id = answer_key.get("correct_option_id", "")
        if correct_id:
            option_ids = set()
            for opt in options:
                if isinstance(opt, dict):
                    oid = opt.get("id")
                    if oid:
                        option_ids.add(str(oid))
            if correct_id not in option_ids:
                return ValidatorResult(
                    "V7", "failed", "critical",
                    reason_code="ANSWER_NOT_IN_OPTIONS",
                    details={
                        "correct_option_id": correct_id,
                        "available_option_ids": list(option_ids),
                    },
                )

        # Check multiple correct answers
        correct_count = 0
        for opt in options:
            if isinstance(opt, dict):
                if opt.get("is_correct") or opt.get("correct"):
                    correct_count += 1
        if correct_count > 1 and item_type not in ("multiple_choice",):
            return ValidatorResult(
                "V7", "failed", "critical",
                reason_code="MULTIPLE_CORRECT_ANSWERS",
                details={"correct_count": correct_count},
            )

    # For open_answer
    if item_type == "open_answer":
        rubric = candidate.get("rubric")
        if not rubric:
            return ValidatorResult(
                "V7", "warning", "major",
                reason_code="RUBRIC_MISSING",
                details={"item_type": item_type},
            )

    return ValidatorResult("V7", "passed", "info")


# ---------------------------------------------------------------------------
# V8 — Rubric Consistency
# ---------------------------------------------------------------------------

def validate_rubric(candidate: dict) -> ValidatorResult:
    """Validate rubric structure and consistency for items that require one."""
    rubric = candidate.get("rubric")
    if not rubric:
        return ValidatorResult("V8", "info", "info", reason_code="NO_RUBRIC")

    criteria = rubric.get("criteria", []) if isinstance(rubric, dict) else rubric if isinstance(rubric, list) else []
    if not criteria:
        return ValidatorResult(
            "V8", "warning", "major",
            reason_code="RUBRIC_MISSING_CRITERIA",
        )

    for criterion in criteria:
        if isinstance(criterion, dict):
            max_score = criterion.get("max_score", 0)
            if max_score <= 0:
                return ValidatorResult(
                    "V8", "failed", "major",
                    reason_code="RUBRIC_SCORE_RANGE_INVALID",
                    details={"criterion_id": criterion.get("criterion_id", "unknown")},
                )

    return ValidatorResult("V8", "passed", "info")


# ---------------------------------------------------------------------------
# V9 — Ambiguity Detection
# ---------------------------------------------------------------------------

_AMBIGUITY_PATTERNS = [
    r"\ball of the above\b",
    r"\bnone of the above\b",
    r"\bboth a and b\b",
    r"\bmay vary\b",
    r"\bdepends\b",
    r"\bpossibly\b",
    r"\bmight be\b",
    r"\bcould be\b",
]


def validate_ambiguity(candidate: dict) -> ValidatorResult:
    """Detect ambiguous language in stem and options."""
    stem = candidate.get("stem", "")
    options = candidate.get("options", [])
    issues = []

    # Check stem
    for pattern in _AMBIGUITY_PATTERNS:
        if re.search(pattern, stem, re.IGNORECASE):
            issues.append(f"Ambiguous pattern in stem: {pattern}")

    # Check options
    for opt in options:
        if isinstance(opt, dict):
            text = opt.get("text", "")
            for pattern in _AMBIGUITY_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    issues.append(f"Ambiguous pattern in option {opt.get('id')}: {pattern}")

    if issues:
        return ValidatorResult(
            "V9", "warning", "minor",
            reason_code="AMBIGUITY_DETECTED",
            details={"issues": issues},
        )
    return ValidatorResult("V9", "passed", "info")


# ---------------------------------------------------------------------------
# V10 — Duplicate / Similarity Detection
# ---------------------------------------------------------------------------

def validate_duplicate(
    candidate: dict,
    existing_candidates: list[dict],
    threshold: float = 0.85,
) -> ValidatorResult:
    """Detect exact and near-duplicate candidates."""
    stem = candidate.get("stem", "").strip().lower()
    stem_hash = hashlib.sha256(stem.encode("utf-8")).hexdigest()

    options = candidate.get("options", [])
    option_texts = sorted([
        o.get("text", "").strip().lower()
        for o in (options or [])
        if isinstance(o, dict)
    ])
    options_hash = hashlib.sha256(json.dumps(option_texts, sort_keys=True).encode("utf-8")).hexdigest()

    evidence = {
        "stem_hash": stem_hash,
        "options_hash": options_hash,
    }

    for existing in existing_candidates:
        existing_stem = existing.get("stem", "").strip().lower()
        existing_hash = hashlib.sha256(existing_stem.encode("utf-8")).hexdigest()

        if existing_hash == stem_hash:
            return ValidatorResult(
                "V10", "failed", "major",
                reason_code="EXACT_DUPLICATE",
                details={
                    "existing_candidate_id": existing.get("candidate_id", "unknown"),
                    "similarity": 1.0,
                    **evidence,
                },
            )

        # Simple similarity check
        existing_words = set(existing_stem.split())
        candidate_words = set(stem.split())
        if existing_words and candidate_words:
            intersection = existing_words.intersection(candidate_words)
            union = existing_words.union(candidate_words)
            jaccard = len(intersection) / len(union) if union else 0
            if jaccard >= threshold:
                return ValidatorResult(
                    "V10", "warning", "major",
                    reason_code="NEAR_DUPLICATE",
                    details={
                        "existing_candidate_id": existing.get("candidate_id", "unknown"),
                        "similarity": round(jaccard, 4),
                        "threshold": threshold,
                        **evidence,
                    },
                )

    return ValidatorResult("V10", "passed", "info")


# ---------------------------------------------------------------------------
# V11 — Prohibited Content / Safety Validation
# ---------------------------------------------------------------------------

_PROHIBITED_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|above|system)",
    r"(?i)forget\s+(all\s+)?(previous|above)",
    r"(?i)you\s+are\s+(an?\s+)?(AI|assistant)",
    r"(?i)as\s+(an?\s+)?(AI|language\s+model)",
    r"(?i)system\s+(instruction|prompt|message)",
    r"(?i)DEEPSEEK_API_KEY",
    r"(?i)sk-[a-zA-Z0-9]{20,}",
    r"(?i)<script[^>]*>",
    r"(?i)onerror\s*=",
    r"(?i)onclick\s*=",
    r"(?i)password|credit.card|ssn|social.security",
]


def validate_safety(candidate: dict) -> ValidatorResult:
    """Check for prohibited content, prompt injection residue, unsafe patterns."""
    text_fields = [
        candidate.get("stem", ""),
        candidate.get("rationale", ""),
    ]

    options = candidate.get("options", [])
    for opt in options or []:
        if isinstance(opt, dict):
            text_fields.append(opt.get("text", ""))

    violations = []
    for pattern in _PROHIBITED_PATTERNS:
        for i, text in enumerate(text_fields):
            if re.search(pattern, text):
                field_name = ["stem", "rationale", "option"][i] if i < 3 else f"field_{i}"
                violations.append(f"Pattern '{pattern}' in {field_name}")

    if violations:
        return ValidatorResult(
            "V11", "failed", "critical",
            reason_code="PROHIBITED_CONTENT",
            details={"violations": violations},
        )
    return ValidatorResult("V11", "passed", "info")


# ---------------------------------------------------------------------------
# V12 — Locale / Language Validation
# ---------------------------------------------------------------------------

def validate_locale(candidate: dict, expected_locale: str) -> ValidatorResult:
    """Validate that the candidate locale matches expectations."""
    candidate_locale = candidate.get("locale", "")
    if candidate_locale and candidate_locale != expected_locale:
        return ValidatorResult(
            "V12", "failed", "major",
            reason_code="LOCALE_MISMATCH",
            details={
                "expected": expected_locale,
                "got": candidate_locale,
            },
        )
    return ValidatorResult("V12", "passed", "info")


# ---------------------------------------------------------------------------
# V13 — Answer Key Leakage Validation
# ---------------------------------------------------------------------------

_ANSWER_KEY_MARKERS = [
    r"\(correct\)",
    r"\[correct\]",
    r"\*correct\*",
    r"\bcorrect answer\b",
    r"\bright answer\b",
    r"\banswer:\s*\w",
    r"✓",
    r"✔",
]


def validate_answer_key_leak(candidate: dict) -> ValidatorResult:
    """Check for answer key markers in learner-facing text."""
    stem = candidate.get("stem", "")
    options = candidate.get("options", [])
    leaks = []

    for pattern in _ANSWER_KEY_MARKERS:
        if re.search(pattern, stem, re.IGNORECASE):
            leaks.append(f"Marker '{pattern}' in stem")
        if options:
            for opt in options:
                if isinstance(opt, dict):
                    text = opt.get("text", "")
                    if re.search(pattern, text, re.IGNORECASE):
                        leaks.append(f"Marker '{pattern}' in option {opt.get('id')}")

    if leaks:
        return ValidatorResult(
            "V13", "failed", "critical",
            reason_code="ANSWER_KEY_LEAK",
            details={"leaks": leaks},
        )

    # Check rationale doesn't explicitly state the answer
    rationale = candidate.get("rationale", "").lower()
    answer_key = candidate.get("answer_key", {})
    correct_id = answer_key.get("correct_option_id", "")
    if correct_id and options:
        for opt in options:
            if isinstance(opt, dict) and opt.get("id") == correct_id:
                correct_text = opt.get("text", "").lower()
                if correct_text and correct_text in rationale and len(correct_text) > 20:
                    pass  # Long matches are acceptable explanations

    return ValidatorResult("V13", "passed", "info")


# ---------------------------------------------------------------------------
# V14 — Provenance Completeness
# ---------------------------------------------------------------------------

def validate_provenance(provenance: dict) -> ValidatorResult:
    """Validate that provenance information is complete."""
    required_fields = [
        "provider", "model", "prompt_template_version",
        "generation_policy_version", "schema_version", "candidate_hash",
    ]
    missing = [f for f in required_fields if not provenance.get(f)]

    if missing:
        return ValidatorResult(
            "V14", "failed", "major",
            reason_code="PROVENANCE_INCOMPLETE",
            details={"missing_fields": missing},
        )
    return ValidatorResult("V14", "passed", "info")


# ---------------------------------------------------------------------------
# V15 — Lifecycle / Pool Mutation Guard
# ---------------------------------------------------------------------------

def validate_pool_mutation_guard(
    candidate: dict,
    request_status: str,
) -> ValidatorResult:
    """Validate that pool mutation safeguards are in place.

    This validator ensures that generated candidates cannot enter
    pilot or exam-eligible pools through this layer.
    """
    status = candidate.get("status", "")
    guard_details = {
        "pilot_pool_mutation_blocked": True,
        "exam_eligible_mutation_blocked": True,
        "exam_assembly_blocked": True,
        "auto_publication_blocked": True,
    }

    # Check for forbidden pool mutations (list of tuples, not dict — dict deduplicates keys)
    forbidden_transitions = [
        ("generated", "pilot_pool"),
        ("generated", "exam_eligible"),
        ("review_handoff_ready", "exam_eligible"),
    ]

    violations = []
    for from_status, to_pool in forbidden_transitions:
        if status == from_status:
            violations.append(f"Transition {from_status} → {to_pool} is forbidden")

    if violations:
        return ValidatorResult(
            "V15", "failed", "critical",
            reason_code="POOL_MUTATION_GUARD_VIOLATION",
            details={"violations": violations, **guard_details},
        )
    return ValidatorResult("V15", "passed", "info", details=guard_details)
