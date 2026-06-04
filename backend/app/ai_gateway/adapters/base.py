"""Abstract base class for AI provider adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai_gateway.schemas import EvaluationGatewayRequest


class BaseProviderAdapter(ABC):
    """Base class for all AI provider adapters.

    Each adapter communicates with a specific AI provider (OpenAI, Anthropic,
    local model, mock, etc.) and returns a raw dictionary response that
    should conform to the EvaluationOutput schema.
    """

    provider_name: str = "base"

    @abstractmethod
    async def evaluate(self, request: EvaluationGatewayRequest) -> dict:
        """Send an evaluation request to the AI provider.

        Args:
            request: The evaluation request containing the user answer,
                     rubric, scenario context, and locale.

        Returns:
            A raw dictionary that should match the EvaluationOutput schema.
            Must be JSON-serializable.

        Raises:
            TimeoutError: If the provider call times out.
            ConnectionError: If the provider is unreachable.
            ValueError: If the provider returns non-JSON or malformed content.
        """
        ...
