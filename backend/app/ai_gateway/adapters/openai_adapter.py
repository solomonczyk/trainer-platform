"""OpenAI-compatible AI provider adapter using httpx.

Supports any OpenAI-compatible API (OpenAI, Azure OpenAI, local LLM servers
with OpenAI-compatible endpoints like Ollama, vLLM, etc.).
"""

from __future__ import annotations

import json
import os
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

# ---------------------------------------------------------------------------
# JSON field name aliases for normalising provider-specific responses
# ---------------------------------------------------------------------------

_CRITERION_ID_ALIASES = ("criterion_id", "id", "criteria_id", "criterionId")
_OVERALL_SCORE_ALIASES = ("overall_score", "score", "overallScore", "total_score")
_EVIDENCE_ALIASES = ("evidence", "evidences", "justification", "reasoning")
_COMMENT_ALIASES = ("comment", "comments", "notes", "feedback")
_IMPROVEMENT_ALIASES = ("improvement", "improvements", "suggestion", "recommendation")


class OpenAIProviderAdapter(BaseProviderAdapter):
    """AI provider adapter that calls an OpenAI-compatible chat completion API.

    Reads the API key, model, and timeout from application settings.
    Supports both ``settings.ai_gateway_api_key`` and the fallback
    ``settings.openai_api_key`` for backward compatibility.
    """

    provider_name: str = "openai"

    def __init__(self, provider_name: str = "openai") -> None:
        self.provider_name = provider_name
        self.api_key: str = self._resolve_api_key()
        self.model: str = (
            os.environ.get("AI_GATEWAY_MODEL")
            or os.environ.get("AI_MODEL_EVALUATOR")
            or settings.ai_gateway_model
        )
        self.timeout_seconds: int = int(
            os.environ.get("AI_GATEWAY_TIMEOUT_SECONDS")
            or os.environ.get("AI_TIMEOUT_SECONDS")
            or settings.ai_gateway_timeout_seconds
        )
        self.max_retries: int = max(settings.ai_gateway_max_retries, 1)
        env_base = os.environ.get("AI_PROVIDER_BASE_URL") or os.environ.get("OPENAI_BASE_URL")
        if env_base:
            self.base_url = env_base
        elif self.provider_name == "deepseek":
            self.base_url = "https://api.deepseek.com"
        else:
            self.base_url = "https://api.openai.com/v1"

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
                parsed = self._parse_response(raw)
                # Normalise DeepSeek responses to match the expected schema
                if self.provider_name == "deepseek":
                    parsed = self._normalize_response(parsed, request.rubric)
                return parsed
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
        """Resolve the API key from settings, preferring the gateway-specific key.

        Falls back to ``DEEPSEEK_API_KEY`` env var for Railway staging naming compatibility.
        """
        if self.provider_name == "deepseek":
            key = settings.ai_gateway_api_key or os.environ.get("DEEPSEEK_API_KEY")
        else:
            key = settings.ai_gateway_api_key or settings.openai_api_key
        if not key:
            logger.warning("No AI API key configured; provider will fail at runtime")
            return ""
        return key

    def _normalize_response(
        self,
        data: dict[str, Any],
        rubric: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Normalise a DeepSeek response to match the EvaluationOutput schema.

        DeepSeek v4-flash (a reasoning model) may return:
        * ``criteria`` items with ``id`` instead of ``criterion_id``
        * criteria items missing ``evidence`` / ``comment`` / ``improvement``
        * a non-list ``criteria`` value or an empty list
        * extra provider-specific fields (e.g. ``reasoning_content``)

        This method maps alternative field names, supplies safe defaults for
        missing optional fields, fills missing rubric criteria, and strips
        provider-only reasoning fields before the result is persisted.
        """
        normalized = dict(data)
        rubric_criteria = self._rubric_criteria(rubric or {})
        rubric_ids = [criterion_id for criterion_id, _ in rubric_criteria]

        # ------------------------------------------------------------------
        # 1. Normalise criteria to a list of well-typed dicts
        # ------------------------------------------------------------------
        raw_criteria: list[Any] = []
        raw_val = normalized.get("criteria")
        if isinstance(raw_val, list):
            raw_criteria = raw_val
        elif isinstance(raw_val, dict):
            # Some providers wrap criteria in a dict keyed by criterion id
            for key, val in raw_val.items():
                if isinstance(val, dict):
                    criterion = dict(val)
                    criterion["criterion_id"] = key
                    raw_criteria.append(criterion)

        valid_criteria: list[dict[str, Any]] = []
        for idx, item in enumerate(raw_criteria):
            if not isinstance(item, dict):
                continue

            norm: dict[str, Any] = {}

            # criterion_id — try aliases in order, then rubric order.
            cid = ""
            for alias in _CRITERION_ID_ALIASES:
                val = item.get(alias)
                if val is not None and str(val).strip():
                    cid = str(val).strip()
                    break
            if not cid:
                cid = rubric_ids[idx] if idx < len(rubric_ids) else f"criterion_{len(valid_criteria)}"
            norm["criterion_id"] = cid

            # score — 0..100, coerce from float / string
            score_val = item.get("score")
            if score_val is None:
                score_val = self._first_present(normalized, _OVERALL_SCORE_ALIASES) or 0
            score_int = self._normalize_score(score_val)
            norm["score"] = max(0, min(100, score_int))

            # evidence
            evidence = ""
            for alias in _EVIDENCE_ALIASES:
                val = item.get(alias)
                if val is not None and str(val).strip():
                    evidence = str(val).strip()
                    break
            if not evidence:
                evidence = "Provider did not return criterion-specific evidence; normalized from overall evaluation."
            norm["evidence"] = evidence

            # comment
            comment = ""
            for alias in _COMMENT_ALIASES:
                val = item.get(alias)
                if val is not None and str(val).strip():
                    comment = str(val).strip()
                    break
            norm["comment"] = comment

            # improvement
            improvement = ""
            for alias in _IMPROVEMENT_ALIASES:
                val = item.get(alias)
                if val is not None and str(val).strip():
                    improvement = str(val).strip()
                    break
            norm["improvement"] = improvement

            valid_criteria.append(norm)

        if rubric_ids:
            by_id = {item["criterion_id"]: item for item in valid_criteria}
            overall_for_defaults = self._normalize_score(
                self._first_present(normalized, _OVERALL_SCORE_ALIASES) or 0
            )
            for criterion_id, criterion_name in rubric_criteria:
                if criterion_id in by_id:
                    continue
                valid_criteria.append(
                    {
                        "criterion_id": criterion_id,
                        "score": overall_for_defaults,
                        "evidence": (
                            "Provider omitted this rubric criterion; normalized from overall evaluation."
                        ),
                        "comment": f"Criterion normalized for {criterion_name or criterion_id}.",
                        "improvement": "",
                    }
                )

            # Keep only rubric criteria when a rubric is present. This prevents
            # provider-specific extras from causing validation_status=partial.
            valid_criteria = [item for item in valid_criteria if item["criterion_id"] in set(rubric_ids)]
        elif not valid_criteria:
            valid_criteria.append(
                {
                    "criterion_id": "overall",
                    "score": self._normalize_score(
                        self._first_present(normalized, _OVERALL_SCORE_ALIASES) or 0
                    ),
                    "evidence": "Provider returned no rubric criteria; normalized from overall evaluation.",
                    "comment": "Generic criterion inserted because no rubric criteria were available.",
                    "improvement": "",
                }
            )

        normalized["criteria"] = valid_criteria

        # ------------------------------------------------------------------
        # 2. overall_score — int 0..100
        # ------------------------------------------------------------------
        os_val = self._first_present(normalized, _OVERALL_SCORE_ALIASES)
        if os_val is None:
            if valid_criteria:
                os_val = sum(c["score"] for c in valid_criteria) // len(valid_criteria)
            else:
                os_val = 0
        os_int = self._normalize_score(os_val)
        normalized["overall_score"] = max(0, min(100, os_int))
        normalized["score"] = normalized["overall_score"]

        # ------------------------------------------------------------------
        # 3. passed — boolean
        # ------------------------------------------------------------------
        passed = normalized.get("passed")
        if passed is None:
            passed = normalized["overall_score"] >= 70
        normalized["passed"] = self._normalize_bool(passed)

        # ------------------------------------------------------------------
        # 4. List fields — ensure list
        # ------------------------------------------------------------------
        for field in ("strengths", "weak_points", "critical_errors"):
            val = normalized.get(field)
            if not isinstance(val, list):
                normalized[field] = [] if val is None else [str(val)]

        # ------------------------------------------------------------------
        # 5. confidence — float 0..1
        # ------------------------------------------------------------------
        conf = normalized.get("confidence")
        if conf is not None:
            try:
                conf_float = float(conf)
            except (ValueError, TypeError):
                conf_float = 0.0
        else:
            conf_float = 0.0
        normalized["confidence"] = max(0.0, min(1.0, conf_float))

        # ------------------------------------------------------------------
        # 6. Strip reasoning_content if it leaked into the parsed dict
        # ------------------------------------------------------------------
        normalized.pop("reasoning_content", None)
        normalized["feedback"] = self._build_feedback(normalized)

        # next_recommendation — keep as-is if present
        return normalized

    @staticmethod
    def _first_present(data: dict[str, Any], aliases: tuple[str, ...]) -> Any:
        for alias in aliases:
            value = data.get(alias)
            if value is not None:
                return value
        return None

    @staticmethod
    def _normalize_score(value: Any) -> int:
        try:
            return max(0, min(100, int(float(value))))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _normalize_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"true", "1", "yes", "passed", "pass"}
        return bool(value)

    async def generate_items(self, prompt: str) -> dict:
        """Generate item candidates using the OpenAI-compatible API.

        Args:
            prompt: The generation prompt including system instruction, context,
                    and schema requirements.

        Returns:
            A dictionary containing generated items under an "items" key.

        Raises:
            TimeoutError: If the API call times out.
            ConnectionError: If the API is unreachable.
            ValueError: If the response is invalid.
        """
        messages = [
            {"role": "system", "content": "You are a certification item generation assistant. Return only valid JSON."},
            {"role": "user", "content": prompt},
        ]

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 8192,
            "response_format": {"type": "json_object"},
        }

        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout_seconds)) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    raw = response.json()
                    parsed = self._parse_response(raw)
                    return parsed
            except (TimeoutError, httpx.TimeoutException) as exc:
                last_error = exc
                logger.warning(f"Generation timeout (attempt {attempt})")
                if attempt < self.max_retries:
                    continue
                raise TimeoutError(f"Generation timed out after {self.max_retries} retries") from exc
            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                last_error = exc
                logger.warning(f"Generation request error (attempt {attempt}): {exc}")
                if attempt < self.max_retries:
                    continue
                raise ConnectionError(f"Generation API unreachable after {self.max_retries} retries") from exc
            except (json.JSONDecodeError, ValueError) as exc:
                last_error = exc
                logger.warning(f"Generation parse error (attempt {attempt}): {exc}")
                if attempt < self.max_retries:
                    continue
                raise ValueError(f"Failed to parse generation response: {exc}") from exc

        raise RuntimeError("Unexpected error in generation") from last_error

    @staticmethod
    def _rubric_criteria(rubric: dict[str, Any]) -> list[tuple[str, str]]:
        criteria: list[tuple[str, str]] = []
        for item in rubric.get("criteria", []):
            if not isinstance(item, dict):
                continue
            criterion_id = item.get("id") or item.get("criterion_id")
            if criterion_id:
                criteria.append((str(criterion_id), str(item.get("name") or "")))
        return criteria

    @staticmethod
    def _build_feedback(normalized: dict[str, Any]) -> str:
        criteria = normalized.get("criteria") or []
        if isinstance(criteria, list):
            for item in criteria:
                if not isinstance(item, dict):
                    continue
                for field in ("comment", "evidence", "improvement"):
                    value = item.get(field)
                    if value is not None and str(value).strip():
                        return str(value).strip()
        for field in ("strengths", "weak_points", "critical_errors"):
            values = normalized.get(field)
            if isinstance(values, list) and values:
                return str(values[0])
        return "Evaluation completed."

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
            "response_format": {"type": "json_object"},
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
        content: str = (message.get("content") or "").strip()
        if not content:
            # Some reasoning providers can place the JSON payload in a separate
            # field. Use it only as parse input; never persist it as reasoning.
            content = (message.get("reasoning_content") or "").strip()

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

        parsed = json.loads(content)
        if isinstance(parsed, dict):
            parsed.pop("reasoning_content", None)
        return parsed
