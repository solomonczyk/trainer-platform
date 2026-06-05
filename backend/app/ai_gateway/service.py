"""AI Gateway service — orchestrates evaluation requests across providers.

The :class:`AIGatewayService` selects the appropriate AI provider adapter,
builds the request payload with the relevant prompt template, invokes the
provider, and validates the response against the :class:`EvaluationOutput`
schema.
"""

from __future__ import annotations

import os
import time
from typing import Any

from app.ai_gateway.adapters.base import BaseProviderAdapter
from app.ai_gateway.schemas import (
    EvaluationGatewayRequest,
    EvaluationGatewayResult,
    EvaluationOutput,
)
from app.ai_gateway.validators.evaluation import validate_evaluation_output
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIGatewayService:
    """Central service for AI-powered evaluation.

    Usage::

        service = AIGatewayService()
        result = await service.evaluate_attempt(request)
    """

    def __init__(self) -> None:
        self._provider: BaseProviderAdapter | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def evaluate_attempt(
        self,
        request: EvaluationGatewayRequest,
    ) -> EvaluationGatewayResult:
        """Evaluate a user's attempt using the configured AI provider.

        This method:
        1. Resolves the AI provider based on application settings.
        2. Builds the evaluation prompt incorporating the rubric.
        3. Calls the provider and measures latency.
        4. Validates the raw response against the :class:`EvaluationOutput` schema.
        5. Returns a structured :class:`EvaluationGatewayResult`.

        Args:
            request: The evaluation request containing the user answer,
                     rubric, scenario context, and locale.

        Returns:
            A fully populated :class:`EvaluationGatewayResult`. On failure,
            ``success`` is ``False`` and ``error_message`` contains details.
        """
        provider = self.get_provider()
        raw_output: dict[str, Any] | None = None
        validated_output: EvaluationOutput | None = None
        validation_status: str = "validated"
        error_message: str = ""
        latency_ms: int = 0

        # Log the request
        logger.info(
            "AI evaluation request",
            attempt_id=request.attempt_id,
            scenario_id=request.scenario_id,
            provider=provider.provider_name,
            model=settings.ai_gateway_model,
            locale=request.locale,
            user_role=request.user_role,
        )

        # Invoke the provider
        try:
            start_time = time.monotonic()
            raw_output = await provider.evaluate(request)
            latency_ms = int((time.monotonic() - start_time) * 1000)
        except TimeoutError:
            latency_ms = settings.ai_gateway_timeout_seconds * 1000
            error_message = "AI provider request timed out"
            validation_status = "failed"
            logger.warning(
                "AI evaluation timeout",
                attempt_id=request.attempt_id,
                provider=provider.provider_name,
                timeout_seconds=settings.ai_gateway_timeout_seconds,
            )
        except ConnectionError as exc:
            error_message = f"AI provider connection error: {exc}"
            validation_status = "failed"
            logger.warning(
                "AI evaluation connection error",
                attempt_id=request.attempt_id,
                provider=provider.provider_name,
                error=str(exc),
            )
        except ValueError as exc:
            error_message = f"AI provider returned invalid response: {exc}"
            validation_status = "failed"
            logger.warning(
                "AI evaluation parse error",
                attempt_id=request.attempt_id,
                provider=provider.provider_name,
                error=str(exc),
            )
        except Exception as exc:
            error_message = f"Unexpected AI provider error: {exc}"
            validation_status = "failed"
            logger.exception(
                "AI evaluation unexpected error",
                attempt_id=request.attempt_id,
                provider=provider.provider_name,
            )

        # Validate the raw output (if we got one)
        if raw_output is not None:
            try:
                validated_output, validation_errors = validate_evaluation_output(
                    raw_output,
                    request.rubric,
                )
                if validation_errors:
                    validation_status = "partial"
                    logger.warning(
                        "AI evaluation validation issues",
                        attempt_id=request.attempt_id,
                        errors=validation_errors,
                    )
                if validated_output is None:
                    error_message = (
                        f"Validation failed: {'; '.join(validation_errors)}"
                    )
                    validation_status = "failed"
            except Exception as exc:
                error_message = f"Validation error: {exc}"
                validation_status = "failed"
                validated_output = None

        # Determine overall success
        success = validation_status != "failed"

        # Fallback: if validation failed but fallback is enabled,
        # return a controlled placeholder result
        if not success and settings.ai_gateway_fallback_placeholder_enabled:
            validated_output = self._build_fallback_output(request, error_message)
            validation_status = "fallback"

        result = EvaluationGatewayResult(
            validated_output=validated_output,
            raw_output=raw_output,
            provider=provider.provider_name,
            model=settings.ai_gateway_model,
            cost_usd=self._estimate_cost(raw_output, provider.provider_name),
            latency_ms=latency_ms,
            validation_status=validation_status,
            error_message=error_message,
            success=success or settings.ai_gateway_fallback_placeholder_enabled,
        )

        logger.info(
            "AI evaluation result",
            attempt_id=request.attempt_id,
            provider=provider.provider_name,
            success=result.success,
            validation_status=validation_status,
            latency_ms=latency_ms,
        )

        return result

    # ------------------------------------------------------------------
    # Provider resolution
    # ------------------------------------------------------------------

    def get_provider(self) -> BaseProviderAdapter:
        """Return the configured AI provider adapter (cached).

        Provider selection is driven by ``settings.ai_gateway_provider``
        (or the ``AI_PROVIDER`` env var as a fallback):

        * ``"mock"`` → :class:`MockProviderAdapter <app.ai_gateway.adapters.mock.MockProviderAdapter>`
        * ``"openai"`` or ``"deepseek"`` → :class:`OpenAIProviderAdapter <app.ai_gateway.adapters.openai_adapter.OpenAIProviderAdapter>`

        Raises:
            ValueError: If the provider name is unknown.
        """
        if self._provider is not None:
            return self._provider

        provider_name = settings.ai_gateway_provider
        # Fallback to AI_PROVIDER env var (Railway staging naming convention)
        if provider_name == "mock" and os.environ.get("AI_PROVIDER"):
            provider_name = os.environ["AI_PROVIDER"]

        if provider_name == "mock":
            from app.ai_gateway.adapters.mock import MockProviderAdapter

            self._provider = MockProviderAdapter()
        elif provider_name in ("openai", "deepseek"):
            from app.ai_gateway.adapters.openai_adapter import OpenAIProviderAdapter

            self._provider = OpenAIProviderAdapter()
        else:
            raise ValueError(
                f"Unknown AI gateway provider: '{provider_name}'. "
                f"Valid options: mock, openai, deepseek"
            )

        logger.info(
            "AI provider initialized",
            provider=self._provider.provider_name,
            model=settings.ai_gateway_model,
        )
        return self._provider

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_fallback_output(
        self,
        request: EvaluationGatewayRequest,
        error_message: str,
    ) -> EvaluationOutput:
        """Build a safe fallback evaluation when the provider call fails."""
        from app.ai_gateway.adapters.mock import MockProviderAdapter

        # Use the mock adapter to generate a deterministic "error" evaluation
        mock = MockProviderAdapter()
        # This is a synchronous fallback path; we call the async evaluate but
        # since MockProviderAdapter.evaluate is actually synchronous inside,
        # we can safely run it this way
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # We're inside async context — we'd need to await, but we're in a
            # sync method. This path should not normally happen because
            # evaluate_attempt is async and we'd be in the same event loop.
            # For safety, build a minimal fallback directly.
            pass
        else:
            try:
                raw = asyncio.run(mock.evaluate(request))
                validated, _ = validate_evaluation_output(raw, request.rubric)
                if validated:
                    return validated
            except Exception:
                pass

        # Ultimate fallback — literal zero evaluation
        return EvaluationOutput(
            overall_score=0,
            passed=False,
            criteria=[],
            strengths=[],
            weak_points=["Evaluation unavailable due to provider error"],
            critical_errors=["evaluation_unavailable"],
            next_recommendation={
                "action": "retry",
                "suggestion": "The evaluation service encountered an error. Please try again.",
                "target_score": 70,
            },
            confidence=0.0,
        )

    def _estimate_cost(
        self, raw_output: dict[str, Any] | None, provider: str
    ) -> float:
        """Estimate the cost of the AI call.

        For the mock provider this returns 0. For real providers that do not
        report usage data in the response, a sensible default is returned.
        """
        if provider == "mock":
            return 0.0

        if raw_output is None:
            return 0.0

        # Attempt to extract token usage from the provider response
        usage = raw_output.get("usage", {}) if isinstance(raw_output, dict) else {}
        if usage:
            prompt_tokens = usage.get("prompt_tokens", 0) or 0
            completion_tokens = usage.get("completion_tokens", 0) or 0
            # Rough GPT-4o-mini pricing: $0.15/M input, $0.60/M output
            cost = (prompt_tokens * 0.15 + completion_tokens * 0.60) / 1_000_000
            return round(cost, 6)

        # No usage data — assume a small default
        return 0.001
