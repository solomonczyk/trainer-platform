"""Typed quest contracts for the immersive simulator engine (Layer 010).

Defines all Pydantic schemas for quest definitions, steps, interactions,
evaluation results, narrative state, outcomes, and debrief.
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Interaction / Step Type Definitions
# ---------------------------------------------------------------------------

StepType = Literal[
    "single_choice",
    "multiple_choice",
    "free_text",
    "ordering",
    "matching",
    "evidence_select",
    "decision",
    "dialogue",
    "branching",
]

EvaluationMode = Literal["deterministic", "ai_rubric", "hybrid"]


class QuestOption(BaseModel):
    """A single selectable option in a choice step."""

    id: str
    text_key: str
    is_correct: bool = False


class QuestConsequence(BaseModel):
    """Consequence updates applied after a step or choice."""

    risk: int = 0
    time_remaining: int = 0
    team_trust: int = 0
    client_trust: int = 0
    evidence_quality: int = 0
    decision_quality: int = 0
    flags: dict[str, Any] = {}
    next_step_id: Optional[str] = None


class ConsequenceMap(BaseModel):
    """Maps choice IDs to consequences."""

    default: Optional[QuestConsequence] = None
    by_choice: dict[str, QuestConsequence] = {}


class NextStepRule(BaseModel):
    """Rule for determining the next step after a step is completed."""

    default: str = ""
    by_choice: dict[str, str] = {}
    by_flag: dict[str, str] = {}


class ChoiceOption(BaseModel):
    """Option for choice-based steps (single, multiple, decision)."""

    id: str
    text_key: str
    is_correct: bool = False
    consequence: Optional[QuestConsequence] = None
    next_step_id: Optional[str] = None
    dialogue_response: Optional[str] = None


class OrderingItem(BaseModel):
    """Item in an ordering step."""

    id: str
    text_key: str
    correct_order: int = 0


class MatchingPair(BaseModel):
    """Pair in a matching step."""

    left_id: str
    left_text_key: str
    right_id: str
    right_text_key: str


class EvidenceItem(BaseModel):
    """Item in an evidence selection step."""

    id: str
    text_key: str
    is_relevant: bool = False
    category: Optional[str] = None


class RubricCriterion(BaseModel):
    """Single criterion in an AI evaluation rubric."""

    criterion_id: str
    weight: float = Field(ge=0, le=1)
    description_key: str
    max_score: int = Field(default=100, ge=1, le=100)


class AiRubric(BaseModel):
    """Rubric contract for AI evaluation."""

    rubric_version: str = "1.0.0"
    criteria: list[RubricCriterion] = []
    minimum_pass_score: int = Field(default=60, ge=0, le=100)
    evaluation_prompt_key: str = ""
    system_prompt_key: str = ""


class StepInteraction(BaseModel):
    """The interaction payload for a step."""

    # For single_choice / decision / branching
    options: list[ChoiceOption] = []

    # For multiple_choice
    choices: list[ChoiceOption] = []
    min_selections: int = 1
    max_selections: int = 0  # 0 = unlimited

    # For ordering
    items: list[OrderingItem] = []
    shuffle: bool = True

    # For matching
    left_items: list[str] = []
    right_items: list[str] = []
    correct_mappings: dict[str, str] = {}  # left_id -> right_id

    # For evidence_select
    evidence_items: list[EvidenceItem] = []
    min_select: int = 1
    max_select: int = 0
    evidence_panel_key: str = ""  # Optional i18n key for a panel rendered above options

    # For free_text
    max_length: int = 3000
    min_length: int = 50
    placeholder_key: str = ""
    guidance_key: str = ""

    # For dialogue
    character_says_key: str = ""
    predefined_responses: list[ChoiceOption] = []
    allow_free_text: bool = False

    # Rubric for AI evaluation
    ai_rubric: Optional[AiRubric] = None


class QuestStep(BaseModel):
    """A single step in a quest."""

    step_id: str
    step_type: StepType
    story_context_key: str
    prompt_key: str
    interaction: StepInteraction = StepInteraction()
    evaluation_mode: EvaluationMode = "deterministic"
    consequences: QuestConsequence = QuestConsequence()
    next_step_rules: NextStepRule = NextStepRule()
    learning_objectives: list[str] = []
    skill_bindings: list[str] = []


class OutcomeDefinition(BaseModel):
    """A possible quest outcome."""

    outcome_id: str
    title_key: str
    summary_key: str
    condition_flag: Optional[str] = None
    min_decision_quality: int = 0
    min_team_trust: int = 0
    min_client_trust: int = 0
    min_evidence_quality: int = 0
    is_default: bool = False


class DebriefContract(BaseModel):
    """Defines how debrief data is structured."""

    sections: list[str] = [
        "strengths",
        "mistakes",
        "missed_risks",
        "decision_consequences",
        "professional_recommendation",
        "practical_takeaways",
        "skill_profile",
        "suggested_next_practice",
    ]
    skill_dimensions: list[str] = []


class QuestDefinition(BaseModel):
    """Complete typed quest definition."""

    quest_id: str
    trainer_slug: str
    version: str = "1.0.0"
    locale: str = "ru-RU"
    title_key: str
    summary_key: str
    learner_role_key: str
    mission_key: str
    setting_key: str
    estimated_minutes: int = 30
    initial_state: dict[str, Any] = {}
    steps: list[QuestStep] = []
    outcomes: list[OutcomeDefinition] = []
    debrief_contract: DebriefContract = DebriefContract()
    characters: list[dict[str, str]] = []
    tags: list[str] = []

    @model_validator(mode="after")
    def validate_quest(self) -> QuestDefinition:
        """Validate quest contract integrity."""
        seen_ids = set()
        for step in self.steps:
            if step.step_id in seen_ids:
                raise ValueError(f"Duplicate step_id: {step.step_id}")
            seen_ids.add(step.step_id)

        # Validate next-step references
        all_ids = {s.step_id for s in self.steps}
        for step in self.steps:
            rule = step.next_step_rules
            if rule.default and rule.default not in all_ids and rule.default != "__terminal__":
                raise ValueError(f"Step {step.step_id}: default next step '{rule.default}' not found")
            for ref in rule.by_choice.values():
                if ref not in all_ids and ref != "__terminal__":
                    raise ValueError(f"Step {step.step_id}: next step ref '{ref}' not found")
            for ref in rule.by_flag.values():
                if ref not in all_ids and ref != "__terminal__":
                    raise ValueError(f"Step {step.step_id}: next step ref '{ref}' not found")

        # Validate AI evaluation only on supported types
        for step in self.steps:
            if step.evaluation_mode == "ai_rubric" and step.step_type not in ("free_text", "dialogue"):
                raise ValueError(f"Step {step.step_id}: ai_rubric only allowed for free_text or dialogue")

        return self


# ---------------------------------------------------------------------------
# API Request / Response Schemas
# ---------------------------------------------------------------------------


class QuestStartRequest(BaseModel):
    """Request to start a quest."""
    locale: str = "ru-RU"


class QuestStartResponse(BaseModel):
    """Response when starting a quest."""
    session_id: str
    quest: QuestDefinition
    current_step: QuestStep
    narrative_state: dict[str, Any]
    status: str = "started"


class QuestAnswerRequest(BaseModel):
    """Request to submit an answer for a step."""
    step_id: str
    answer: Any = None
    idempotency_key: Optional[str] = None
    locale: str = "ru-RU"


class QuestAnswerResponse(BaseModel):
    """Response after submitting and evaluating a step answer."""
    step_id: str
    status: str
    score: Optional[int] = None
    max_score: Optional[int] = None
    correct: Optional[bool] = None
    feedback_key: Optional[str] = None
    feedback_data: Optional[dict] = None
    consequence_updates: Optional[dict] = None
    narrative_state: dict[str, Any] = {}
    next_step: Optional[QuestStep] = None
    next_step_id: Optional[str] = None
    evaluation_mode: Optional[str] = None
    timed_out: bool = False
    correlation_id: Optional[str] = None


class QuestStepResponse(BaseModel):
    """Response for fetching a quest step."""
    session_id: str
    step: QuestStep
    narrative_state: dict[str, Any]
    completed_step_ids: list[str] = []
    answers: dict[str, Any] = {}
    step_result: Optional[dict] = None


class QuestOutcomeResponse(BaseModel):
    """Response for quest completion with outcome and debrief."""
    session_id: str
    outcome_id: str
    outcome_title_key: str
    outcome_summary_key: str
    narrative_state: dict[str, Any]
    debrief: dict[str, Any]
    status: str = "completed"


class QuestProgressResponse(BaseModel):
    """Response for quest session progress (used on refresh)."""
    session_found: bool
    session_id: Optional[str] = None
    quest: Optional[QuestDefinition] = None
    current_step: Optional[QuestStep] = None
    narrative_state: Optional[dict] = None
    completed_step_ids: list[str] = []
    answers: dict[str, Any] = {}
    step_results: dict[str, Any] = {}
    status: str = ""
    outcome: Optional[dict] = None
    debrief: Optional[dict] = None
