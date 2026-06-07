"""Mock AI provider adapter for local development and testing.

Returns deterministic evaluation results based on answer content analysis
without calling any external AI service.
"""

from __future__ import annotations

import random
from typing import Any

from app.ai_gateway.adapters.base import BaseProviderAdapter
from app.ai_gateway.schemas import EvaluationGatewayRequest


# ---------------------------------------------------------------------------
# Answer-quality classification helpers
# ---------------------------------------------------------------------------

EXCELLENT_TRIGGERS: list[str] = [
    "check", "verify", "validate", "assert", "test case", "equivalence",
    "boundary value", "positive", "negative", "regression", "smoke",
    "coverage", "traceability", "requirements", "acceptance criteria",
    "bug report", "severity", "priority", "environment", "setup", "teardown",
    "precondition", "postcondition", "expected result", "actual result",
    "steps to reproduce", "test plan", "test strategy", "test design",
    "test automation", "test framework", "test report", "test metrics",
    "root cause", "impact analysis", "risk assessment",
]

GOOD_TRIGGERS: list[str] = [
    "test", "scenario", "case", "step", "input", "output",
    "error", "exception", "log", "debug", "performance",
    "security", "usability", "compatibility", "configuration",
    "documentation", "review", "inspection", "walkthrough",
]

MEDIUM_TRIGGERS: list[str] = [
    "maybe", "probably", "i think", "could be", "might be",
    "not sure", "guess", "some", "thing", "stuff",
]

BAD_TRIGGERS: list[str] = [
    "i don't know", "not sure", "no idea", "skip", "pass",
    "next question", "dunno", "idk",
]

CRITICAL_PATTERNS: list[str] = [
    "steps not needed", "no need for steps", "steps not required",
    "unnecessary steps", "dont need steps", "don't need steps",
    "steps to reproduce are not needed",
    "will figure it out",
]


def _classify_answer(answer: str) -> tuple[str, list[str]]:
    """Classify answer quality and collect matched triggers.

    Returns:
        (quality_label, matched_patterns)
    """
    lowered = answer.lower().strip()

    # Empty
    if not lowered:
        return ("empty", [])

    # Critical: "steps not needed" type
    for pattern in CRITICAL_PATTERNS:
        if pattern in lowered:
            return ("critical", [pattern])

    # Bad / incomplete
    bad_matches = [t for t in BAD_TRIGGERS if t in lowered]
    if len(bad_matches) >= 1:
        # Only classify as bad if answer is short (< 50 words)
        if len(lowered.split()) < 30:
            return ("bad", bad_matches)

    # Excellent
    excellent_matches = [t for t in EXCELLENT_TRIGGERS if t in lowered]
    if len(excellent_matches) >= 3:
        return ("excellent", excellent_matches)

    # Good
    good_matches = [t for t in GOOD_TRIGGERS if t in lowered]
    if len(excellent_matches) >= 1 or len(good_matches) >= 3:
        return ("good", excellent_matches + good_matches)

    # Medium
    medium_matches = [t for t in MEDIUM_TRIGGERS if t in lowered]
    if medium_matches:
        return ("medium", medium_matches)

    # Fallback: short answer -> medium, long answer -> good
    word_count = len(lowered.split())
    if word_count < 20:
        return ("bad", [])
    elif word_count < 50:
        return ("medium", [])
    else:
        return ("good", [])


def _score_range(quality: str) -> tuple[int, int, bool]:
    """Return (min_score, max_score, passed) for a quality tier."""
    ranges: dict[str, tuple[int, int, bool]] = {
        "excellent": (85, 95, True),
        "good": (70, 84, True),
        "medium": (50, 69, False),
        "bad": (30, 49, False),
        "empty": (0, 0, False),
        "critical": (10, 10, False),
    }
    return ranges.get(quality, (0, 0, False))


def _build_criteria_results(
    rubric: dict, score: int, quality: str, answer: str, rng: random.Random
) -> list[dict[str, Any]]:
    """Build per-criterion evaluation results based on the rubric structure."""
    criteria_raw = rubric.get("criteria", rubric.get("criterion_ids", []))
    if not criteria_raw:
        # Fallback criteria if rubric has no criteria list
        criteria_raw = [{"id": "general_knowledge", "name": "General Knowledge", "weight": 100}]

    results: list[dict[str, Any]] = []
    criteria_list = list(criteria_raw)

    for i, criterion in enumerate(criteria_list):
        if isinstance(criterion, dict):
            cid = criterion.get("id") or criterion.get("criterion_id", f"criterion_{i}")
        else:
            cid = str(criterion)

        # Base score per criterion with some variance
        variance = rng.randint(-5, 5)
        criterion_score = max(0, min(100, score + variance))

        # Build evidence based on quality
        if quality == "excellent":
            evidence = (
                f"Candidate demonstrated strong proficiency in '{cid}'. "
                f"Provided detailed steps including {rng.choice(['verification', 'validation', 'test case design', 'boundary analysis'])}. "
                f"Answer shows deep understanding and practical experience."
            )
            comment = "Meets or exceeds expectations at senior level."
            improvement = "Consider exploring edge cases and non-functional requirements further."
        elif quality == "good":
            evidence = (
                f"Candidate shows adequate knowledge of '{cid}'. "
                f"Provided relevant {rng.choice(['test scenarios', 'verification steps', 'quality measures'])}. "
                f"Answer covers key aspects but lacks depth in some areas."
            )
            comment = "Solid understanding, minor gaps in depth."
            improvement = "Could elaborate on specific techniques and provide more concrete examples."
        elif quality == "medium":
            evidence = (
                f"Candidate has partial understanding of '{cid}'. "
                f"Answer contains {rng.choice(['general statements', 'high-level concepts', 'basic ideas'])} "
                f"but lacks specific details or structured approach."
            )
            comment = "Foundational knowledge present but needs significant development."
            improvement = "Study structured approaches, practice with real scenarios, and learn industry best practices."
        elif quality == "bad":
            evidence = (
                f"Candidate shows insufficient knowledge of '{cid}'. "
                f"Answer is {rng.choice(['vague', 'incomplete', 'superficial', 'off-topic'])} "
                f"and does not demonstrate required competency."
            )
            comment = "Critical knowledge gap identified."
            improvement = "Requires foundational training and guided practice in this area."
        elif quality == "empty":
            evidence = "No answer provided for this criterion."
            comment = "No response given."
            improvement = "Candidate must provide a substantive answer."
        elif quality == "critical":
            evidence = (
                f"Candidate made a critical error related to '{cid}'. "
                f"The answer indicates misunderstanding of fundamental QA principles "
                f"by suggesting that certain process steps are unnecessary."
            )
            comment = "Critical error detected - fundamental process misunderstanding."
            improvement = "Immediate retraining required on QA fundamentals and process compliance."
        else:
            evidence = f"Criterion '{cid}' evaluated."
            comment = ""
            improvement = ""

        results.append({
            "criterion_id": cid,
            "score": criterion_score,
            "evidence": evidence,
            "comment": comment,
            "improvement": improvement,
        })

    return results


def _build_strengths_and_weaknesses(
    quality: str, matched: list[str], rng: random.Random
) -> tuple[list[str], list[str]]:
    """Derive strengths and weak points from the quality tier and matched triggers."""
    strengths: list[str] = []
    weak_points: list[str] = []

    if quality == "excellent":
        strengths = [
            "Deep understanding of QA methodology and best practices",
            "Structured approach to problem-solving with clear traceability",
            "Ability to design comprehensive test scenarios covering positive and negative cases",
            "Strong analytical skills demonstrated through detailed evidence",
            "Proactive consideration of edge cases and risk factors",
        ]
        # Maybe rotate a couple out
        rng.shuffle(strengths)
        strengths = strengths[: rng.randint(3, 5)]
        weak_points = ["Could improve time management by being more concise"]
    elif quality == "good":
        strengths = [
            "Solid grasp of core QA concepts",
            "Clear communication of test scenarios",
            "Good awareness of quality standards",
        ]
        weak_points = [
            "Lacks depth in certain areas - consider expanding with specific techniques",
            "Could strengthen answer with more concrete examples and evidence",
        ]
    elif quality == "medium":
        strengths = [
            "Basic understanding of QA terminology",
            "Willingness to attempt the answer",
        ]
        weak_points = [
            "Answer lacks structure and specific details",
            "Needs to develop systematic approach to problem-solving",
            "Should study industry standard practices and methodologies",
        ]
    elif quality == "bad":
        strengths = []
        weak_points = [
            "Answer is incomplete or too brief to demonstrate competency",
            "Lacks understanding of fundamental QA concepts",
            "Needs significant preparation and study",
        ]
    elif quality == "empty":
        strengths = []
        weak_points = [
            "No answer provided",
            "Unable to assess candidate knowledge",
        ]
    elif quality == "critical":
        strengths = []
        weak_points = [
            "Fundamental misunderstanding of QA process requirements",
            "Dismissed essential verification steps as unnecessary",
        ]
    else:
        strengths = []
        weak_points = ["Unable to determine competency level"]

    return strengths, weak_points


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


class MockProviderAdapter(BaseProviderAdapter):
    """Mock AI provider that evaluates answers using deterministic rules.

    Useful for development, testing, and CI environments where no real
    AI provider API key is available.
    """

    provider_name: str = "mock"

    async def evaluate(self, request: EvaluationGatewayRequest) -> dict:
        """Generate a mock evaluation based on answer content analysis.

        This method simulates a real AI provider call with a small
        artificial delay to approximate network latency.
        """
        answer = request.user_answer or ""
        rubric = request.rubric or {}
        quality, matched_patterns = _classify_answer(answer)
        min_score, max_score, passed = _score_range(quality)

        # Use scenario_id as seed for reproducibility on the same input
        seed = hash(f"{request.attempt_id}:{request.scenario_id}:{answer}") & 0xFFFFFFFF
        rng = random.Random(seed)

        overall_score = rng.randint(min_score, max_score) if max_score > min_score else min_score

        criteria = _build_criteria_results(rubric, overall_score, quality, answer, rng)

        strengths, weak_points = _build_strengths_and_weaknesses(quality, matched_patterns, rng)

        critical_errors: list[str] = []
        if quality == "critical":
            critical_errors = ["qa_crit_steps_not_needed"]
        elif quality == "empty":
            critical_errors = ["qa_crit_no_answer"]

        # Simulate small latency
        latency_ms = rng.randint(150, 800)

        result: dict[str, Any] = {
            "overall_score": overall_score,
            "passed": passed,
            "criteria": criteria,
            "strengths": strengths,
            "weak_points": weak_points,
            "critical_errors": critical_errors,
            "next_recommendation": self._build_recommendation(quality, overall_score, rubric),
            "confidence": self._confidence_for_quality(quality),
        }

        return result

    def _build_recommendation(
        self, quality: str, score: int, rubric: dict
    ) -> dict | None:
        """Build a next-step recommendation based on evaluation outcome."""
        if quality in ("excellent", "good"):
            return {
                "action": "advance",
                "suggestion": "Proceed to next scenario or increase difficulty level.",
                "target_score": min(100, score + 10),
            }
        elif quality == "medium":
            return {
                "action": "retry",
                "suggestion": "Review the topic materials and retry the scenario after studying.",
                "target_score": 80,
            }
        elif quality == "bad":
            return {
                "action": "restudy",
                "suggestion": "Complete the foundational training module before attempting again.",
                "target_score": 70,
            }
        elif quality == "critical":
            return {
                "action": "restudy",
                "suggestion": "Immediate review of QA fundamentals is required. Repeat training module.",
                "target_score": 85,
            }
        elif quality == "empty":
            return {
                "action": "retry",
                "suggestion": "Please provide a complete answer to receive evaluation.",
                "target_score": 70,
            }
        return None

    def _confidence_for_quality(self, quality: str) -> float:
        """Return confidence score based on how definitive the classification is."""
        confidence_map: dict[str, float] = {
            "excellent": 0.95,
            "good": 0.85,
            "medium": 0.75,
            "bad": 0.90,
            "empty": 1.0,
            "critical": 0.98,
        }
        return confidence_map.get(quality, 0.5)

    async def generate_items(self, prompt: str) -> dict:
        """Generate deterministic mock item candidates.

        Returns a controlled set of generated items for testing.
        No external API call is made.
        """
        import hashlib
        seed = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8]
        rng = random.Random(int(seed, 16))

        # Generate a deterministic item based on the prompt seed
        item_type = rng.choice(["multiple_choice", "single_choice", "open_answer"])

        stem = (
            f"Based on the provided context (seed={seed}), "
            f"which of the following best describes a key principle?"
        )

        options = [
            {"id": "A", "text": "Principle A: Systematic verification ensures quality outcomes"},
            {"id": "B", "text": "Principle B: Ad-hoc testing is sufficient for most cases"},
            {"id": "C", "text": "Principle C: Documentation is optional for experienced teams"},
            {"id": "D", "text": "Principle D: Testing should only occur at the end of development"},
        ]

        if seed[-1] in "01234567":
            correct_id = "A"
        else:
            correct_id = "B"

        items = [{
            "item_type": item_type,
            "stem": stem,
            "options": options if item_type != "open_answer" else [],
            "answer_key": {"correct_option_id": correct_id} if item_type != "open_answer" else {},
            "rationale": (
                f"Option {correct_id} is correct because it aligns with industry best practices "
                f"for quality assurance and verification processes."
            ),
            "rubric": {
                "criteria": [
                    {"criterion_id": "accuracy", "name": "Accuracy", "max_score": 5, "weight": 40},
                    {"criterion_id": "completeness", "name": "Completeness", "max_score": 3, "weight": 30},
                    {"criterion_id": "clarity", "name": "Clarity", "max_score": 2, "weight": 30},
                ]
            },
            "source_citations": [
                {"source_id": "mock-source-001", "version": "1.0", "reference": "Mock Certification Standard §3.2"}
            ],
        }]

        return {"items": items}
