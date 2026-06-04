from pydantic import BaseModel, Field
from typing import Optional


class CriterionResult(BaseModel):
    criterion_id: str
    score: int = Field(ge=0, le=100)
    evidence: str
    comment: str = ""
    improvement: str = ""


class EvaluationOutput(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    passed: bool
    criteria: list[CriterionResult]
    strengths: list[str] = []
    weak_points: list[str] = []
    critical_errors: list[str] = []
    next_recommendation: Optional[dict] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)


class EvaluationGatewayRequest(BaseModel):
    attempt_id: str
    scenario_id: str
    user_answer: str
    rubric: dict
    locale: str = "ru-RU"
    user_role: str = "candidate"
    ai_role: str = "interviewer"


class EvaluationGatewayResult(BaseModel):
    validated_output: Optional[EvaluationOutput] = None
    raw_output: Optional[dict] = None
    provider: str = "mock"
    model: str = ""
    cost_usd: float = 0.0
    latency_ms: int = 0
    validation_status: str = "validated"
    error_message: str = ""
    success: bool = True
