"""Validation logic for AI evaluation outputs.

Ensures that raw responses from AI providers conform to the expected
:class:`EvaluationOutput` schema and the rubric requirements.
"""

from __future__ import annotations

from typing import Any

from app.ai_gateway.schemas import CriterionResult, EvaluationOutput


def validate_evaluation_output(
    raw: dict[str, Any],
    rubric: dict[str, Any],
    *,
    evidence_required: bool | None = None,
) -> tuple[EvaluationOutput | None, list[str]]:
    """Validate a raw AI provider response against the expected schema and rubric.

    Args:
        raw: The raw dictionary returned by an AI provider adapter.
        rubric: The rubric dictionary that was used for the evaluation.
        evidence_required: Override for the evidence requirement. If ``None``,
                          the value is inferred from the rubric structure.

    Returns:
        A tuple of ``(validated_output, validation_errors)``.
        * ``validated_output`` is a fully populated :class:`EvaluationOutput`
          if the raw data passes all checks, or ``None`` if critical validation
          fails.
        * ``validation_errors`` is a list of human-readable error strings.
          An empty list means the output is fully valid.
    """
    errors: list[str] = []

    # ------------------------------------------------------------------
    # 1. Structural checks
    # ------------------------------------------------------------------

    if not isinstance(raw, dict):
        return (None, ["Raw output is not a dictionary"])

    overall_score = raw.get("overall_score")
    if overall_score is None:
        errors.append("Missing required field: overall_score")
    elif not isinstance(overall_score, (int, float)):
        errors.append("overall_score must be numeric")
    else:
        overall_score_int = int(overall_score)
        if overall_score_int < 0 or overall_score_int > 100:
            errors.append(f"overall_score out of range [0, 100]: {overall_score_int}")

    passed = raw.get("passed")
    if passed is None:
        errors.append("Missing required field: passed")
    elif not isinstance(passed, bool):
        errors.append("passed must be a boolean")

    criteria_raw = raw.get("criteria")
    if not criteria_raw:
        errors.append("Missing or empty required field: criteria")
    elif not isinstance(criteria_raw, list):
        errors.append("criteria must be a list")

    # ------------------------------------------------------------------
    # 2. Rubric criteria presence check
    # ------------------------------------------------------------------

    rubric_criteria: list[dict[str, Any]] = rubric.get("criteria", [])
    rubric_criterion_ids: set[str] = set()

    if rubric_criteria:
        for rc in rubric_criteria:
            if isinstance(rc, dict):
                cid = rc.get("id") or rc.get("criterion_id")
                if cid:
                    rubric_criterion_ids.add(str(cid))

    if rubric_criterion_ids and isinstance(criteria_raw, list):
        output_criterion_ids: set[str] = set()
        for cr in criteria_raw:
            if isinstance(cr, dict):
                oid = cr.get("criterion_id")
                if oid:
                    output_criterion_ids.add(str(oid))

        missing_ids = rubric_criterion_ids - output_criterion_ids
        extra_ids = output_criterion_ids - rubric_criterion_ids

        if missing_ids:
            errors.append(
                f"Missing criteria in output: {', '.join(sorted(missing_ids))}"
            )
        if extra_ids:
            errors.append(
                f"Unexpected criteria in output: {', '.join(sorted(extra_ids))}"
            )

    # ------------------------------------------------------------------
    # 3. Per-criterion validation
    # ------------------------------------------------------------------

    validated_criteria: list[CriterionResult] = []
    if isinstance(criteria_raw, list):
        for idx, cr in enumerate(criteria_raw):
            if not isinstance(cr, dict):
                errors.append(f"criteria[{idx}] is not a dictionary")
                continue

            cid = cr.get("criterion_id", f"criteria[{idx}]")
            score = cr.get("score")
            if score is None:
                errors.append(f"Missing score in criterion '{cid}'")
            elif not isinstance(score, (int, float)):
                errors.append(f"Score in criterion '{cid}' must be numeric, got {type(score).__name__}")
            else:
                score_int = int(score)
                if score_int < 0 or score_int > 100:
                    errors.append(f"Score in criterion '{cid}' out of range [0, 100]: {score_int}")

            evidence = cr.get("evidence", "")
            # Determine whether evidence is required for this criterion
            if evidence_required is None and rubric_criteria:
                # Check rubric for evidence_required flag
                for rc in rubric_criteria:
                    if isinstance(rc, dict) and (rc.get("id") == cid or rc.get("criterion_id") == cid):
                        if rc.get("evidence_required", True) is False:
                            break
                else:
                    # Not found in rubric or no flag set — default to required
                    req = True
            else:
                req = evidence_required if evidence_required is not None else True

            if req and not evidence:
                errors.append(f"Missing or empty evidence in criterion '{cid}'")

            # Build a CriterionResult even for partial data; Pydantic validation
            # will catch remaining issues, but we collect them here.
            try:
                validated_criteria.append(
                    CriterionResult(
                        criterion_id=cid,
                        score=int(cr.get("score", 0)),
                        evidence=str(evidence or ""),
                        comment=str(cr.get("comment", "")),
                        improvement=str(cr.get("improvement", "")),
                    )
                )
            except (ValueError, TypeError, KeyError) as exc:
                errors.append(f"Invalid data for criterion '{cid}': {exc}")

    # ------------------------------------------------------------------
    # 4. Strengths / weak_points / critical_errors types
    # ------------------------------------------------------------------

    for field_name in ("strengths", "weak_points", "critical_errors"):
        value = raw.get(field_name)
        if value is not None and not isinstance(value, list):
            errors.append(f"{field_name} must be a list, got {type(value).__name__}")

    # ------------------------------------------------------------------
    # 5. Confidence check
    # ------------------------------------------------------------------

    confidence = raw.get("confidence", 0.0)
    if confidence is not None:
        try:
            conf_float = float(confidence)
            if conf_float < 0.0 or conf_float > 1.0:
                errors.append(f"confidence out of range [0.0, 1.0]: {conf_float}")
        except (ValueError, TypeError):
            errors.append(f"confidence must be a float, got {type(confidence).__name__}")

    # ------------------------------------------------------------------
    # 6. Build validated output
    # ------------------------------------------------------------------

    # If there are errors but we can still construct a valid EvaluationOutput,
    # we return it along with the error list for the caller to decide.
    try:
        validated = EvaluationOutput(
            overall_score=int(overall_score) if overall_score is not None else 0,
            passed=bool(passed) if passed is not None else False,
            criteria=validated_criteria if validated_criteria else [],
            strengths=raw.get("strengths", []),
            weak_points=raw.get("weak_points", []),
            critical_errors=raw.get("critical_errors", []),
            next_recommendation=raw.get("next_recommendation"),
            confidence=float(confidence) if confidence is not None else 0.0,
        )
    except (ValueError, TypeError) as exc:
        errors.append(f"Failed to construct EvaluationOutput: {exc}")
        return (None, errors)

    return (validated, errors)
