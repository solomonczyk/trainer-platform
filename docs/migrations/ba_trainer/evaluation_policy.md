# Evaluation Policy — Business Analyst Interview Trainer

## Policy ID

BA_EVAL_POLICY_V1

## Date

2026-06-06

## Guiding Principles

1. **Simple tasks do not invoke AI.** Deterministic validation is faster, cheaper, and more reliable for closed-form questions.
2. **AI evaluation is reserved for semantic understanding.** Open-text answers, case studies, and complex reasoning use DeepSeek via the AI Gateway.
3. **Hybrid evaluation is used when structure matters and quality matters.** The deterministic validator checks structure; the AI evaluates quality.
4. **Fallback behavior** ensures the user always receives feedback, even when AI is unavailable.
5. **Cost guardrails** limit AI usage per session and per user.

---

## Deterministic Validation

### Used For

| Type | Validation Method | Rules |
|---|---|---|
| **radio** | Exact string match | `userAnswer === data.correct` |
| **checkbox** | Set equality | `correct.length === user.length && correct.every(c => user.includes(c))` |
| **number** | Numeric comparison | `Math.abs(user - correct) < 0.01` (tolerance for floating point) |
| **fill-blanks** | Positional exact match | Each blank position compared — all match = correct, some = partial |
| **matching** | Pair-wise match | Generate correct pairs from `data.pairs`. Compare with user mapping. All correct = full, partial credit per correct pair. |
| **click-image** | Zone ID match | `userZoneId === correctZoneId` |
| **drag-sort** | Ordered list comparison | `JSON.stringify(userOrder) === JSON.stringify(correctOrder)` |
| **drag-group** | Group membership check | Items placed in correct group = correct |
| **flashcard** | Self-assessment | User declares `known` or `unknown` — always marked as attempted |

### Implementation

```typescript
interface DeterministicEvaluation {
  status: 'correct' | 'partial' | 'incorrect';
  score: number;           // 0-100
  matchedCount: number;
  totalCount: number;
  details?: Record<string, boolean>;
}
```

The deterministic validator is a stateless function that takes `(questionType, data, userAnswer)` and returns the evaluation. It runs client-side for instant feedback and can be mirrored server-side for record integrity.

---

## AI Evaluation (DeepSeek via AI Gateway)

### Used For

| Content Type | Examples |
|---|---|
| **textarea / open answers** | Process descriptions, methodology explanations, stakeholder analysis |
| **Case studies** | Module 10 (Real Cases) — complex scenarios |
| **Self-presentation** | HR interview answers |
| **Stakeholder conflict scenarios** | Module 8 communication questions |
| **Requirements analysis** | Module 3 elicitation and analysis |
| **Process explanation** | Module 5 BPMN/data modeling |
| **SQL/API reasoning** | Module 9 technical questions |
| **Branching dialogue final evaluation** | End-of-dialogue summary assessment |

### Prompt Structure

Each AI-evaluated activity receives a prompt containing:

- The question/task description
- The user's answer
- The evaluation rubric (criteria, weights, levels)
- Expected answer guidelines (if available)
- Locale context

### Rubric Template

```json
{
  "criterion_id": "string",
  "name": "display name",
  "weight": 25,
  "description": "what to evaluate",
  "levels": [
    {"score": 0, "label": "not_observed"},
    {"score": 25, "label": "basic"},
    {"score": 50, "label": "developing"},
    {"score": 75, "label": "ready"},
    {"score": 100, "label": "strong"}
  ]
}
```

### Cost Guardrails

| Guardrail | Limit |
|---|---|
| Max AI evaluations per session | 50 |
| Max AI evaluations per user per day | 200 |
| AI request timeout | 30 seconds |
| Fallback on timeout | Deterministic keyword check results |
| Max answer length for AI | 3000 characters (truncate before sending) |
| Cost alert threshold | $0.50/day per environment |

---

## Hybrid Evaluation

### Used When

A question has both **structural requirements** (deterministic check) and **quality requirements** (AI evaluation).

### Flow

1. User submits answer
2. **Phase 1 — Deterministic:** Keyword matcher checks required terms, structure rules (numbers, examples, length)
3. If Phase 1 passes minimum threshold → proceed to Phase 2
4. **Phase 2 — AI:** DeepSeek evaluates quality, coherence, depth
5. Final score = weighted combination

### Weight Configuration

```json
{
  "deterministic_weight": 0.3,
  "ai_weight": 0.7,
  "min_deterministic_pass": 0.5,
  "fallback_on_ai_failure": true
}
```

---

## Fallback Behavior

| Scenario | Behavior |
|---|---|
| AI provider timeout | Return keyword-check result only with `evaluation_mode: "keyword_fallback"` |
| AI provider error | Same as timeout — deterministic if available, else mark as `unevaluated` |
| Invalid AI response | Retry once; if still invalid, use fallback |
| Both deterministic and AI fail | `status: "error"`, user sees "Evaluation unavailable, please try again" |

---

## Policy Artifact

```json
{
  "no_ai_for_simple_deterministic_tasks": true,
  "deepseek_for_semantic_tasks": true,
  "hybrid_mode_defined": true,
  "fallback_behavior_defined": true,
  "cost_guardrail_defined": true,
  "evaluation_policy_id": "BA_EVAL_POLICY_V1",
  "version": "1.0.0",
  "status": "draft"
}
```
