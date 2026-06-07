"""Abstract base class for AI provider adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any

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

    async def generate_items(self, prompt: str) -> dict:
        """Generate item candidates using the AI provider.

        Default implementation raises NotImplementedError. Provider adapters
        that support item generation should override this method.

        Args:
            prompt: The generation prompt including system instruction, context,
                    and schema requirements.

        Returns:
            A dictionary containing generated items under an "items" key.

        Raises:
            NotImplementedError: If the provider does not support generation.
        """
        raise NotImplementedError(f"Provider '{self.provider_name}' does not support item generation")
