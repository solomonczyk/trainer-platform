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
