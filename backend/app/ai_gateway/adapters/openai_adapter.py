"""OpenAI-compatible AI provider adapter using httpx.

Supports any OpenAI-compatible API (OpenAI, Azure OpenAI, local LLM servers
with OpenAI-compatible endpoints like Ollama, vLLM, etc.).
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.ai_gateway.adapters.base import BaseProviderAdapter
from app.ai_gateway.schemas import EvaluationGatewayRequest
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# Default system prompt used when none is provided by the caller
_DEFAULT_SYSTEM_PROMPT = (
    "You are an expert evaluator assessing a candidate's answer in a QA interview "
    "simulation. Analyze the answer against the provided rubric criteria. "
    "Return your evaluation as strict JSON matching the required schema. "
    "Be objective, fair, and provide specific evidence for every score."
)


class OpenAIProviderAdapter(BaseProviderAdapter):
    """AI provider adapter that calls an OpenAI-compatible chat completion API.

    Reads the API key, model, and timeout from application settings.
    Supports both ``settings.ai_gateway_api_key`` and the fallback
    ``settings.openai_api_key`` for backward compatibility.
    """

    provider_name: str = "openai"

    def __init__(self) -> None:
        self.api_key: str = self._resolve_api_key()
        self.model: str = settings.ai_gateway_model
        self.timeout_seconds: int = settings.ai_gateway_timeout_seconds
        self.max_retries: int = max(settings.ai_gateway_max_retries, 1)
        # Default endpoint; override via env OPENAI_BASE_URL if needed
        self.base_url: str = settings.openai_base_url if hasattr(settings, "openai_base_url") and settings.openai_base_url else "https://api.openai.com/v1"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def evaluate(self, request: EvaluationGatewayRequest) -> dict:
        """Call an OpenAI-compatible API and return the parsed JSON response.

        Args:
            request: The evaluation request containing user answer, rubric,
                     scenario context, and locale.

        Returns:
            A dictionary parsed from the model's JSON response.

        Raises:
            TimeoutError: If the API call times out after all retries.
            ConnectionError: If the API is unreachable.
            ValueError: If the response is not valid JSON or is empty.
        """
        messages = self._build_messages(request)
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                raw = await self._call_chat_completion(messages)
                return self._parse_response(raw)
            except TimeoutError as exc:
                last_error = exc
                logger.warning(
                    "OpenAI API timeout",
                    attempt=attempt,
                    max_retries=self.max_retries,
                    model=self.model,
                )
                if attempt < self.max_retries:
                    continue
                raise
            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                last_error = exc
                logger.warning(
                    "OpenAI API request error",
                    attempt=attempt,
                    error=str(exc),
                    model=self.model,
                )
                if attempt < self.max_retries:
                    continue
                raise ConnectionError(f"OpenAI API unreachable after {self.max_retries} retries") from exc
            except (json.JSONDecodeError, ValueError) as exc:
                last_error = exc
                logger.warning(
                    "OpenAI API response parse error",
                    attempt=attempt,
                    error=str(exc),
                )
                if attempt < self.max_retries:
                    continue
                raise ValueError(f"Failed to parse OpenAI response as JSON: {exc}") from exc

        # Should not reach here, but satisfy the type checker
        raise RuntimeError("Unexpected error in OpenAI adapter") from last_error

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_api_key(self) -> str:
        """Resolve the API key from settings, preferring the gateway-specific key."""
        key = settings.ai_gateway_api_key or settings.openai_api_key
        if not key:
            logger.warning("No OpenAI API key configured; provider will fail at runtime")
            return ""
        return key

    def _build_messages(self, request: EvaluationGatewayRequest) -> list[dict[str, str]]:
        """Build the chat messages payload for the evaluation request.

        Constructs a system message with the prompt template (if available)
        and a user message containing the answer, rubric, and context.
        """
        # Attempt to load a prompt from the registry based on the rubric
        prompt_template = self._get_prompt_template(request)

        system_content = (
            f"{prompt_template}\n\n"
            f"Locale: {request.locale}\n"
            f"User role: {request.user_role}\n"
            f"AI role: {request.ai_role}"
        )

        user_content = json.dumps(
            {
                "scenario_id": request.scenario_id,
                "user_answer": request.user_answer,
                "rubric": request.rubric,
            },
            ensure_ascii=False,
            indent=2,
        )

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

    def _get_prompt_template(self, request: EvaluationGatewayRequest) -> str:
        """Resolve a prompt template string for the given request.

        Attempts to load a prompt keyed by scenario or rubric. Falls back
        to the default system prompt when no registry match is found.
        """
        try:
            from app.ai_gateway.prompts.registry import PROMPT_REGISTRY

            scenario_id = request.scenario_id
            # Try a scenario-specific prompt first
            prompt_key = f"evaluator_prompt_scenario_{scenario_id}"
            if prompt_key in PROMPT_REGISTRY:
                return PROMPT_REGISTRY[prompt_key]["template"]

            # Fall back to generic QA interview evaluator
            prompt_key = "evaluator_prompt_qa_interview_v1"
            if prompt_key in PROMPT_REGISTRY:
                return PROMPT_REGISTRY[prompt_key]["template"]
        except ImportError:
            logger.debug("Prompt registry not available, using default system prompt")
        except Exception:
            logger.exception("Error loading prompt template")

        return _DEFAULT_SYSTEM_PROMPT

    async def _call_chat_completion(
        self, messages: list[dict[str, str]]
    ) -> dict[str, Any]:
        """Execute the HTTP POST to the OpenAI-compatible chat endpoint.

        Returns the full JSON response body as a dictionary.
        """
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,  # Low temperature for consistent evaluation
            "max_tokens": 4096,
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout_seconds)) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    def _parse_response(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Extract the JSON evaluation result from the API response body.

        Handles both direct JSON responses and markdown-wrapped JSON blocks.
        """
        choices = raw.get("choices", [])
        if not choices:
            raise ValueError("OpenAI response contains no choices")

        message = choices[0].get("message", {})
        content: str = message.get("content", "").strip()

        if not content:
            raise ValueError("OpenAI response content is empty")

        # Attempt to extract JSON from markdown code fences
        if content.startswith("```"):
            # Find the first ```json or ``` and extract between fences
            lines = content.split("\n")
            start_idx = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("```"):
                    start_idx = i + 1
                    break
            end_idx = len(lines)
            for i in range(start_idx, len(lines)):
                if lines[i].strip().startswith("```"):
                    end_idx = i
                    break
            content = "\n".join(lines[start_idx:end_idx]).strip()

        return json.loads(content)
