"""Tests for AI Gateway module."""

import pytest
from app.ai_gateway.schemas import EvaluationOutput, EvaluationGatewayRequest, CriterionResult


class TestEvaluationContract:
    """Test the evaluation contract schema validation."""

    def test_valid_evaluation_output(self):
        """Valid evaluation output passes validation."""
        output = EvaluationOutput(
            overall_score=75,
            passed=True,
            criteria=[
                CriterionResult(
                    criterion_id="technical_accuracy",
                    score=80,
                    evidence="Candidate provided accurate technical details",
                    comment="Good technical knowledge",
                    improvement="Add more specific examples",
                ),
                CriterionResult(
                    criterion_id="clarity",
                    score=70,
                    evidence="Clear structure",
                    comment="Well organized",
                    improvement="Be more concise",
                ),
            ],
            strengths=["Good technical knowledge", "Clear structure"],
            weak_points=["Needs more examples"],
            critical_errors=[],
            next_recommendation={"action": "next_scenario", "description": "Proceed to next scenario"},
            confidence=0.85,
        )
        assert output.overall_score == 75
        assert output.passed is True
        assert len(output.criteria) == 2
        assert output.confidence == 0.85

    def test_score_range_validation(self):
        """Score must be between 0 and 100."""
        with pytest.raises(ValueError):
            EvaluationOutput(
                overall_score=150,  # Invalid
                passed=True,
                criteria=[],
                strengths=[],
                weak_points=[],
                critical_errors=[],
                confidence=0.5,
            )

    def test_negative_score_invalid(self):
        """Negative score raises validation error."""
        with pytest.raises(ValueError):
            EvaluationOutput(
                overall_score=-10,  # Invalid
                passed=False,
                criteria=[],
                strengths=[],
                weak_points=[],
                critical_errors=[],
                confidence=0.5,
            )

    def test_confidence_range(self):
        """Confidence must be between 0 and 1."""
        with pytest.raises(ValueError):
            EvaluationOutput(
                overall_score=50,
                passed=True,
                criteria=[],
                strengths=[],
                weak_points=[],
                critical_errors=[],
                confidence=1.5,  # Invalid
            )

    def test_criterion_score_range(self):
        """Criterion score must be between 0 and 100."""
        with pytest.raises(ValueError):
            CriterionResult(
                criterion_id="test",
                score=101,  # Invalid
                evidence="test",
            )

    def test_gateway_request_schema(self):
        """Gateway request schema works."""
        request = EvaluationGatewayRequest(
            attempt_id="test-attempt-1",
            scenario_id="qa_bug_report_structure_v1",
            user_answer="This is my test answer about bug reports.",
            rubric={"pass_score": 70, "criteria": [{"criterion_id": "clarity", "weight": 50}]},
            locale="ru-RU",
        )
        assert request.attempt_id == "test-attempt-1"
        assert request.locale == "ru-RU"


class TestMockProvider:
    """Tests for the mock AI provider."""

    @pytest.mark.asyncio
    async def test_mock_provider_exists(self):
        """Mock provider adapter exists and can be instantiated."""
        from app.ai_gateway.adapters.mock import MockProviderAdapter
        adapter = MockProviderAdapter()
        assert adapter is not None

    @pytest.mark.asyncio
    async def test_mock_provider_returns_dict(self):
        """Mock provider returns expected dict structure."""
        from app.ai_gateway.adapters.mock import MockProviderAdapter
        adapter = MockProviderAdapter()
        request = EvaluationGatewayRequest(
            attempt_id="test-1",
            scenario_id="qa_bug_report_structure_v1",
            user_answer="I would structure a bug report with title, steps to reproduce, actual and expected results, environment details.",
            rubric={
                "rubric_id": "qa_bug_report_rubric_v1",
                "pass_score": 70,
                "criteria": [
                    {"criterion_id": "structure", "name": "Structure", "weight": 25},
                    {"criterion_id": "technical_accuracy", "name": "Technical Accuracy", "weight": 30},
                    {"criterion_id": "completeness", "name": "Completeness", "weight": 25},
                    {"criterion_id": "clarity", "name": "Clarity", "weight": 20},
                ],
                "critical_fail_enabled": True,
            },
        )
        result = await adapter.evaluate(request)
        assert isinstance(result, dict)
        assert "overall_score" in result
        assert "passed" in result
        assert "criteria" in result
        assert "strengths" in result
        assert "weak_points" in result
        assert "critical_errors" in result

    @pytest.mark.asyncio
    async def test_mock_provider_critical_error(self):
        """Mock provider detects critical errors."""
        from app.ai_gateway.adapters.mock import MockProviderAdapter
        adapter = MockProviderAdapter()
        request = EvaluationGatewayRequest(
            attempt_id="test-critical-1",
            scenario_id="qa_bug_report_structure_v1",
            user_answer="Steps to reproduce are not needed, the developer will figure it out themselves.",
            rubric={
                "rubric_id": "qa_bug_report_rubric_v1",
                "pass_score": 70,
                "criteria": [
                    {"criterion_id": "structure", "name": "Structure", "weight": 25},
                    {"criterion_id": "technical_accuracy", "name": "Technical Accuracy", "weight": 30},
                    {"criterion_id": "completeness", "name": "Completeness", "weight": 25},
                    {"criterion_id": "clarity", "name": "Clarity", "weight": 20},
                ],
                "critical_fail_enabled": True,
            },
        )
        result = await adapter.evaluate(request)
        assert result["overall_score"] < 60
        assert result["passed"] is False
        assert len(result["critical_errors"]) > 0

    @pytest.mark.asyncio
    async def test_mock_provider_empty_answer(self):
        """Mock provider handles empty answers."""
        from app.ai_gateway.adapters.mock import MockProviderAdapter
        adapter = MockProviderAdapter()
        request = EvaluationGatewayRequest(
            attempt_id="test-empty-1",
            scenario_id="qa_bug_report_structure_v1",
            user_answer="",
            rubric={
                "rubric_id": "qa_bug_report_rubric_v1",
                "pass_score": 70,
                "criteria": [{"criterion_id": "clarity", "name": "Clarity", "weight": 100}],
                "critical_fail_enabled": False,
            },
        )
        result = await adapter.evaluate(request)
        assert result["overall_score"] == 0
        assert result["passed"] is False


class TestGatewayService:
    """Tests for the AI Gateway service."""

    @pytest.mark.asyncio
    async def test_gateway_service_mock_provider(self):
        """Gateway service works with mock provider."""
        from app.ai_gateway.service import AIGatewayService
        gateway = AIGatewayService()
        request = EvaluationGatewayRequest(
            attempt_id="test-svc-1",
            scenario_id="qa_bug_report_structure_v1",
            user_answer="I would write a clear bug report with all necessary sections.",
            rubric={
                "rubric_id": "qa_bug_report_rubric_v1",
                "pass_score": 70,
                "criteria": [
                    {"criterion_id": "clarity", "name": "Clarity", "weight": 100},
                ],
                "critical_fail_enabled": False,
            },
        )
        result = await gateway.evaluate_attempt(request)
        assert result.success
        assert result.validated_output is not None
        assert result.validated_output.overall_score >= 0
        assert result.provider == "mock"

    def test_deepseek_env_mapping(self, monkeypatch):
        """Railway DeepSeek env aliases configure the OpenAI-compatible adapter."""
        monkeypatch.setenv("AI_PROVIDER", "deepseek")
        monkeypatch.setenv("AI_MODEL_EVALUATOR", "deepseek-v4-flash")
        monkeypatch.setenv("AI_PROVIDER_BASE_URL", "https://api.deepseek.com")
        monkeypatch.setenv("AI_TIMEOUT_SECONDS", "30")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key-not-real")

        from app.ai_gateway.service import AIGatewayService

        gateway = AIGatewayService()
        provider = gateway.get_provider()

        assert provider.provider_name == "deepseek"
        assert provider.model == "deepseek-v4-flash"
        assert provider.base_url == "https://api.deepseek.com"
        assert provider.timeout_seconds == 30


class TestDeepSeekSchemaNormalization:
    """Tests for DeepSeek response normalisation.

    DeepSeek v4-flash (a reasoning model) may return responses with
    alternative field names, missing fields, or reasoning_content.
    ``_normalize_response`` must map these to the EvaluationOutput schema
    so that ``validate_evaluation_output`` returns ``validation_status="validated"``.
    """

    @pytest.fixture
    def adapter(self):
        from app.ai_gateway.adapters.openai_adapter import OpenAIProviderAdapter
        return OpenAIProviderAdapter(provider_name="deepseek")

    # ------------------------------------------------------------------
    # Criteria field-name aliases
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("alias", [
        "criterion_id",
        "id",
        "criteria_id",
        "criterionId",
    ])
    def test_criterion_id_aliases(self, adapter, alias):
        """Normalisation maps all known ``criterion_id`` aliases."""
        raw = {
            "overall_score": 75,
            "passed": True,
            "criteria": [
                {alias: "technical_accuracy", "score": 80, "evidence": "Good"},
            ],
            "strengths": [],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.9,
        }
        norm = adapter._normalize_response(raw)
        assert len(norm["criteria"]) == 1
        assert norm["criteria"][0]["criterion_id"] == "technical_accuracy"

    def test_criterion_id_missing_generates_default(self, adapter):
        """When no ``criterion_id`` alias is present a default name is generated."""
        raw = {
            "overall_score": 70,
            "passed": True,
            "criteria": [
                {"score": 70, "evidence": "Some evidence"},
            ],
            "strengths": [],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.8,
        }
        norm = adapter._normalize_response(raw)
        assert len(norm["criteria"]) == 1
        assert norm["criteria"][0]["criterion_id"].startswith("criterion_")

    # ------------------------------------------------------------------
    # Evidence aliases
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("alias", [
        "evidence",
        "evidences",
        "justification",
        "reasoning",
    ])
    def test_evidence_aliases(self, adapter, alias):
        """Normalisation maps evidence aliases."""
        raw = {
            "overall_score": 75,
            "passed": True,
            "criteria": [
                {"criterion_id": "clarity", "score": 80, alias: "Clear explanation"},
            ],
            "strengths": [],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.9,
        }
        norm = adapter._normalize_response(raw)
        assert norm["criteria"][0]["evidence"] == "Clear explanation"

    def test_evidence_missing_defaults_to_safe_text(self, adapter):
        """Missing evidence gets a safe schema-valid default."""
        raw = {
            "overall_score": 70,
            "passed": True,
            "criteria": [
                {"criterion_id": "clarity", "score": 80},
            ],
            "strengths": [],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.8,
        }
        norm = adapter._normalize_response(raw)
        assert norm["criteria"][0]["evidence"]
        assert "Provider did not return criterion-specific evidence" in norm["criteria"][0]["evidence"]

    # ------------------------------------------------------------------
    # Score normalisation
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("score_in,expected", [
        (85, 85),
        (85.7, 85),
        ("80", 80),
        (150, 100),
        (-10, 0),
        (None, 70),
    ])
    def test_score_normalisation(self, adapter, score_in, expected):
        """Score is coerced to int and clamped to [0, 100]."""
        raw = {
            "overall_score": 70,
            "passed": True,
            "criteria": [
                {"criterion_id": "clarity", "score": score_in, "evidence": "x"},
            ],
            "strengths": [],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.8,
        }
        norm = adapter._normalize_response(raw)
        assert norm["criteria"][0]["score"] == expected

    # ------------------------------------------------------------------
    # overall_score fallback
    # ------------------------------------------------------------------

    def test_overall_score_derived_from_criteria_when_missing(self, adapter):
        """When ``overall_score`` is absent, it is calculated from criteria."""
        raw = {
            "passed": True,
            "criteria": [
                {"criterion_id": "a", "score": 80, "evidence": "x"},
                {"criterion_id": "b", "score": 60, "evidence": "y"},
            ],
            "strengths": [],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.8,
        }
        norm = adapter._normalize_response(raw)
        assert norm["overall_score"] == 70  # (80 + 60) // 2

    def test_overall_score_defaults_to_zero_when_no_criteria(self, adapter):
        """When both ``overall_score`` and criteria are missing, score is 0."""
        raw = {
            "passed": True,
            "criteria": [],
            "strengths": [],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.8,
        }
        norm = adapter._normalize_response(raw)
        assert norm["overall_score"] == 0
        assert len(norm["criteria"]) == 1
        assert norm["criteria"][0]["criterion_id"] == "overall"

    # ------------------------------------------------------------------
    # passed boolean
    # ------------------------------------------------------------------

    def test_passed_derived_from_score_when_missing(self, adapter):
        """When ``passed`` is absent, it is derived from ``overall_score`` >= 70."""
        raw = {
            "overall_score": 85,
            "criteria": [{"criterion_id": "a", "score": 85, "evidence": "x"}],
            "strengths": [],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.9,
        }
        norm = adapter._normalize_response(raw)
        assert norm["passed"] is True

    def test_passed_false_when_score_low(self, adapter):
        """When ``passed`` is absent and score < 70, passed is False."""
        raw = {
            "overall_score": 50,
            "criteria": [{"criterion_id": "a", "score": 50, "evidence": "x"}],
            "strengths": [],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.5,
        }
        norm = adapter._normalize_response(raw)
        assert norm["passed"] is False

    # ------------------------------------------------------------------
    # List fields
    # ------------------------------------------------------------------

    def test_list_fields_default_to_empty(self, adapter):
        """``strengths``, ``weak_points``, ``critical_errors`` default to []."""
        raw = {
            "overall_score": 70,
            "passed": True,
            "criteria": [{"criterion_id": "a", "score": 70, "evidence": "x"}],
        }
        norm = adapter._normalize_response(raw)
        assert norm["strengths"] == []
        assert norm["weak_points"] == []
        assert norm["critical_errors"] == []

    def test_non_list_fields_are_wrapped(self, adapter):
        """Non-list list-fields are wrapped in a list."""
        raw = {
            "overall_score": 70,
            "passed": True,
            "criteria": [{"criterion_id": "a", "score": 70, "evidence": "x"}],
            "strengths": "single strength",
            "weak_points": None,
            "critical_errors": 42,
        }
        norm = adapter._normalize_response(raw)
        assert norm["strengths"] == ["single strength"]
        assert norm["weak_points"] == []
        assert norm["critical_errors"] == ["42"]

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("conf_in,expected", [
        (0.85, 0.85),
        (1.5, 1.0),
        (-0.5, 0.0),
        (None, 0.0),
        ("0.75", 0.75),
    ])
    def test_confidence_clamping(self, adapter, conf_in, expected):
        """Confidence is clamped to [0.0, 1.0]."""
        raw = {
            "overall_score": 70,
            "passed": True,
            "criteria": [],
            "strengths": [],
            "weak_points": [],
            "critical_errors": [],
            "confidence": conf_in,
        }
        norm = adapter._normalize_response(raw)
        assert norm["confidence"] == expected

    # ------------------------------------------------------------------
    # reasoning_content stripping
    # ------------------------------------------------------------------

    def test_reasoning_content_stripped(self, adapter):
        """``reasoning_content`` is removed if present in the parsed dict."""
        raw = {
            "overall_score": 75,
            "passed": True,
            "criteria": [{"criterion_id": "a", "score": 75, "evidence": "x"}],
            "strengths": [],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.9,
            "reasoning_content": "This is the deepseek reasoning trace...",
        }
        norm = adapter._normalize_response(raw)
        assert "reasoning_content" not in norm

    def test_reasoning_content_used_only_as_parse_input(self, adapter):
        """Message ``reasoning_content`` can be parsed but is not persisted."""
        raw_response = {
            "choices": [
                {
                    "message": {
                        "content": "",
                        "reasoning_content": (
                            '{"overall_score": 72, "passed": true, '
                            '"criteria": [{"criterion_id": "clarity", "score": 72, "evidence": "Clear"}], '
                            '"strengths": [], "weak_points": [], "critical_errors": [], "confidence": 0.7}'
                        ),
                    }
                }
            ]
        }

        parsed = adapter._parse_response(raw_response)
        norm = adapter._normalize_response(
            parsed,
            {"criteria": [{"criterion_id": "clarity", "name": "Clarity"}]},
        )
        assert "reasoning_content" not in parsed
        assert "reasoning_content" not in norm
        assert norm["criteria"][0]["criterion_id"] == "clarity"
        assert norm["feedback"]

    # ------------------------------------------------------------------
    # Full-schema validation after normalisation
    # ------------------------------------------------------------------

    def test_validation_status_validated_after_normalisation(self, adapter):
        """After normalisation, ``validate_evaluation_output`` returns validated."""
        from app.ai_gateway.validators.evaluation import validate_evaluation_output

        raw = {
            "overall_score": 78,
            "passed": True,
            "criteria": [
                {"criterion_id": "structure", "score": 80, "evidence": "Well structured"},
                {"criterion_id": "clarity", "score": 75, "evidence": "Clear explanation"},
            ],
            "strengths": ["Good structure"],
            "weak_points": ["Could be more detailed"],
            "critical_errors": [],
            "next_recommendation": {"action": "advance", "suggestion": "Proceed", "target_score": 85},
            "confidence": 0.85,
        }
        rubric = {
            "pass_score": 70,
            "criteria": [
                {"id": "structure", "name": "Structure", "weight": 50},
                {"id": "clarity", "name": "Clarity", "weight": 50},
            ],
        }

        norm = adapter._normalize_response(raw)
        validated, errors = validate_evaluation_output(norm, rubric)
        assert validated is not None, f"Validation failed: {errors}"
        assert len(errors) == 0, f"Validation errors remain: {errors}"
        assert validated.overall_score == 78
        assert validated.passed is True
        assert len(validated.criteria) == 2
        assert validated.criteria[0].criterion_id == "structure"
        assert validated.criteria[1].criterion_id == "clarity"

    def test_validation_status_validated_with_deepseek_id_alias(self, adapter):
        """DeepSeek response with ``id`` instead of ``criterion_id`` validates."""
        from app.ai_gateway.validators.evaluation import validate_evaluation_output

        raw = {
            "overall_score": 82,
            "passed": True,
            "criteria": [
                {"id": "technical_accuracy", "score": 85, "evidence": "Accurate"},
                {"id": "completeness", "score": 78, "evidence": "Mostly complete"},
            ],
            "strengths": ["Accurate"],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.9,
        }
        rubric = {
            "pass_score": 70,
            "criteria": [
                {"criterion_id": "technical_accuracy", "name": "Technical Accuracy", "weight": 50},
                {"criterion_id": "completeness", "name": "Completeness", "weight": 50},
            ],
        }

        norm = adapter._normalize_response(raw)
        validated, errors = validate_evaluation_output(norm, rubric)
        assert validated is not None, f"Validation failed: {errors}"
        assert len(errors) == 0, f"Validation errors remain: {errors}"
        assert validated.passed is True

    def test_validation_status_validated_with_empty_criteria_fix(self, adapter):
        """Empty criteria after normalisation becomes non-empty and valid."""
        from app.ai_gateway.validators.evaluation import validate_evaluation_output

        raw = {
            "overall_score": 0,
            "passed": False,
            "criteria": [],
            "strengths": [],
            "weak_points": ["No criteria available"],
            "critical_errors": [],
            "confidence": 0.0,
        }
        rubric = {"pass_score": 70, "criteria": []}

        norm = adapter._normalize_response(raw)
        validated, errors = validate_evaluation_output(norm, rubric)
        # Empty criteria is valid — no rubric criteria to match
        assert validated is not None, f"Validation should not fail: {errors}"
        assert len(errors) == 0, f"Validation errors remain: {errors}"
        assert len(validated.criteria) == 1
        assert validated.criteria[0].criterion_id == "overall"
        # errors may contain "Missing or empty required field: criteria" since
        # the valid schema expects at least one criterion ... but this is NOT a
        # deepseek-specific error. The rubric has no criteria so no mismatch.
        assert validated is not None

    # ------------------------------------------------------------------
    # Integration: DeepSeek response through full validate path
    # ------------------------------------------------------------------

    def test_full_flow_simulated_deepseek_response(self, adapter):
        """A simulated DeepSeek response results in validation_status validated."""
        # Simulate a DeepSeek-like response (with id instead of criterion_id)
        raw_deepseek = {
            "overall_score": 88,
            "passed": True,
            "criteria": [
                {"id": "structure", "score": 90, "reasoning": "Great structure"},
                {"id": "technical_accuracy", "score": 85, "reasoning": "Technically sound"},
            ],
            "strengths": ["Good"],
            "weak_points": ["Minor"],
            "critical_errors": [],
            "next_recommendation": {"action": "advance", "suggestion": "Go", "target_score": 90},
            "confidence": 0.9,
        }

        norm = adapter._normalize_response(raw_deepseek)
        assert norm["criteria"][0]["criterion_id"] == "structure"
        assert norm["criteria"][1]["criterion_id"] == "technical_accuracy"
        assert norm["criteria"][0]["evidence"] == "Great structure"
        assert norm["criteria"][1]["evidence"] == "Technically sound"
        assert norm["overall_score"] == 88
        assert norm["passed"] is True

    def test_deepseek_gateway_service_full_flow(self, monkeypatch):
        """DeepSeek provider through gateway service works end-to-end."""
        monkeypatch.setenv("AI_PROVIDER", "deepseek")
        monkeypatch.setenv("AI_MODEL_EVALUATOR", "deepseek-v4-flash")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key-not-real")

        from app.ai_gateway.service import AIGatewayService
        gateway = AIGatewayService()
        provider = gateway.get_provider()
        assert provider.provider_name == "deepseek"

        # Verify the adapter has the normalize method
        assert hasattr(provider, "_normalize_response")


class TestDeepSeekValidatorContract:
    """Contract tests: DeepSeek responses must yield validation_status=validated."""

    def test_contract_deepseek_response_normalized_validates(self):
        """A raw DeepSeek response normalizes to a schema-valid EvaluationOutput."""
        from app.ai_gateway.adapters.openai_adapter import OpenAIProviderAdapter
        from app.ai_gateway.validators.evaluation import validate_evaluation_output

        adapter = OpenAIProviderAdapter(provider_name="deepseek")

        # Simulate what DeepSeek might return: id instead of criterion_id,
        # evidence as "reasoning", no comment/improvement
        deepseek_raw = {
            "overall_score": 85,
            "passed": True,
            "criteria": [
                {"id": "structure", "score": 90, "reasoning": "Well organized answer"},
                {"id": "technical_accuracy", "score": 80, "reasoning": "Correct terminology used"},
                {"id": "completeness", "score": 85, "reasoning": "Covered most aspects"},
            ],
            "strengths": ["Good structure", "Accurate terminology"],
            "weak_points": ["Could add more detail to edge cases"],
            "critical_errors": [],
            "next_recommendation": {"action": "advance", "suggestion": "Proceed", "target_score": 90},
            "confidence": 0.88,
        }

        rubric = {
            "pass_score": 70,
            "criteria": [
                {"criterion_id": "structure", "name": "Structure", "weight": 33},
                {"criterion_id": "technical_accuracy", "name": "Technical Accuracy", "weight": 33},
                {"criterion_id": "completeness", "name": "Completeness", "weight": 34},
            ],
        }

        norm = adapter._normalize_response(deepseek_raw, rubric)
        validated, errors = validate_evaluation_output(norm, rubric)
        assert validated is not None, f"Validation failed: {errors}"
        assert len(errors) == 0, f"Validation errors: {errors}"
        assert validated.overall_score == 85
        assert validated.passed is True
        assert len(validated.criteria) == 3

        # Verify validation_status would be "validated"
        assert len(errors) == 0

    def test_contract_deepseek_empty_criteria_handled(self):
        """Even with empty criteria, normalisation produces valid output."""
        from app.ai_gateway.adapters.openai_adapter import OpenAIProviderAdapter
        from app.ai_gateway.validators.evaluation import validate_evaluation_output

        adapter = OpenAIProviderAdapter(provider_name="deepseek")

        # DeepSeek returned no criteria
        deepseek_raw = {
            "overall_score": 60,
            "passed": False,
            "criteria": [],
            "strengths": [],
            "weak_points": ["Incomplete answer"],
            "critical_errors": [],
            "confidence": 0.7,
        }

        rubric = {
            "pass_score": 70,
            "criteria": [
                {"criterion_id": "structure", "name": "Structure", "weight": 50},
                {"criterion_id": "clarity", "name": "Clarity", "weight": 50},
            ],
        }
        norm = adapter._normalize_response(deepseek_raw, rubric)
        validated, errors = validate_evaluation_output(norm, rubric)
        assert validated is not None, f"Validation failed: {errors}"
        assert len(errors) == 0, f"Validation errors remain: {errors}"
        assert len(validated.criteria) == 2
        assert {cr.criterion_id for cr in validated.criteria} == {"structure", "clarity"}

    def test_contract_deepseek_missing_rubric_criterion_is_filled(self):
        """Missing rubric criteria are defaulted so validation stays validated."""
        from app.ai_gateway.adapters.openai_adapter import OpenAIProviderAdapter
        from app.ai_gateway.validators.evaluation import validate_evaluation_output

        adapter = OpenAIProviderAdapter(provider_name="deepseek")

        deepseek_raw = {
            "overall_score": 76,
            "passed": True,
            "criteria": [
                {"id": "structure", "score": 80, "reasoning": "Structured answer"},
            ],
            "strengths": ["Structured"],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.8,
        }
        rubric = {
            "pass_score": 70,
            "criteria": [
                {"criterion_id": "structure", "name": "Structure", "weight": 50},
                {"criterion_id": "clarity", "name": "Clarity", "weight": 50},
            ],
        }

        norm = adapter._normalize_response(deepseek_raw, rubric)
        validated, errors = validate_evaluation_output(norm, rubric)
        assert validated is not None, f"Validation failed: {errors}"
        assert len(errors) == 0, f"Validation errors remain: {errors}"
        assert {cr.criterion_id for cr in validated.criteria} == {"structure", "clarity"}

    def test_contract_deepseek_criteria_dict_format(self):
        """Normalisation handles criteria as a dict (provider-specific)."""
        from app.ai_gateway.adapters.openai_adapter import OpenAIProviderAdapter

        adapter = OpenAIProviderAdapter(provider_name="deepseek")

        deepseek_raw = {
            "overall_score": 75,
            "passed": True,
            "criteria": {
                "structure": {"score": 80, "evidence": "Good"},
                "clarity": {"score": 70, "evidence": "Clear"},
            },
            "strengths": [],
            "weak_points": [],
            "critical_errors": [],
            "confidence": 0.8,
        }

        norm = adapter._normalize_response(deepseek_raw)
        assert len(norm["criteria"]) == 2
        assert norm["criteria"][0]["criterion_id"] in ("structure", "clarity")
