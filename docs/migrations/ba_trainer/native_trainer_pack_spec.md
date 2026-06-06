# Native Trainer Pack Specification — Business Analyst Interview Trainer

## Target Identity

```json
{
  "trainer_product_id": "business_analyst_interview_trainer",
  "slug": "business-analyst-interview-trainer",
  "title": "Business Analyst Interview Trainer",
  "title_ru": "Тренажёр собеседования бизнес-аналитика",
  "domain": "IT",
  "status": "draft",
  "version": "0.1.0",
  "product_type": "interview_simulator",
  "target_audience": ["junior_ba_candidate", "middle_ba_candidate", "career_switcher"],
  "default_locale": "ru-RU",
  "supported_locales": ["ru-RU"],
  "owner": "platform"
}
```

---

## Pack Manifest (`trainer.json`)

```json
{
  "trainer_product_id": "business_analyst_interview_trainer",
  "domain": "it",
  "slug": "business-analyst-interview-trainer",
  "name": "Business Analyst Interview Trainer",
  "name_ru": "Тренажёр собеседования бизнес-аналитика",
  "product_type": "interview_simulator",
  "target_audience": ["junior_ba_candidate", "middle_ba_candidate", "career_switcher"],
  "default_locale": "ru-RU",
  "supported_locales": ["ru-RU"],
  "status": "draft",
  "owner": "platform",
  "description": "Comprehensive interview simulator for Business Analyst candidates. Covers HR screening, BA fundamentals, requirements engineering, process modeling, methodologies, metrics, communication, technical aspects, and real case studies with deterministic and AI-powered evaluation.",
  "description_ru": "Комплексный тренажёр собеседования для кандидатов на позицию бизнес-аналитика. Охватывает HR-скрининг, основы BA, работу с требованиями, моделирование, методологии, метрики, коммуникацию, технические аспекты и реальные кейсы с детерминированной и AI-оценкой."
}
```

---

## Version Manifest (`trainer_version.json`)

```json
{
  "trainer_product_id": "business_analyst_interview_trainer",
  "version": "0.1.0",
  "release_status": "draft",
  "skill_map_id": "ba_interview_skill_map_v1",
  "rubric_pack_id": "ba_interview_rubric_pack_v1",
  "scenario_ids": [
    "ba_hr_screening_v1",
    "ba_self_presentation_v1",
    "ba_basics_stakeholders_v1",
    "ba_requirements_elicitation_v1",
    "ba_documentation_artifacts_v1",
    "ba_process_data_modeling_v1",
    "ba_methodologies_v1",
    "ba_metrics_prioritization_v1",
    "ba_communication_conflict_v1",
    "ba_technical_aspects_v1",
    "ba_real_cases_v1",
    "ba_diagnostics_assessment_v1",
    "ba_final_exam_v1"
  ],
  "locale_pack_ids": ["ru-RU"],
  "published_at": null,
  "requires_expert_review": true
}
```

---

## Modules

### Module Structure

Each source module maps to a platform track with nested scenarios/activities:

| Track | Module Scenario IDs | Question Types | Evaluation |
|---|---|---|---|
| HR Screening | `ba_hr_track` | 5 scenarios | deterministic + AI |
| BA Basics | `ba_basics_track` | 6 scenarios | deterministic |
| Requirements | `ba_requirements_track` | 4 scenarios | deterministic + AI |
| Documentation | `ba_documentation_track` | 4 scenarios | deterministic + AI |
| Modeling | `ba_modeling_track` | 6 scenarios | deterministic |
| Methodologies | `ba_methodologies_track` | 4 scenarios | deterministic + AI |
| Metrics | `ba_metrics_track` | 4 scenarios | deterministic + AI |
| Communication | `ba_communication_track` | 4 scenarios | deterministic + AI |
| Technical | `ba_technical_track` | 4 scenarios | deterministic + AI |
| Case Studies | `ba_cases_track` | 3 scenarios | AI |
| Diagnostics | `ba_diagnostics` | 1 assessment | hybrid |
| Exam | `ba_exam` | 1 exam session | hybrid |

---

## Scenarios / Activities

### Activity Packaging

Each source question becomes one **activity** within a scenario. Activities are typed:

```json
{
  "activity_id": "ba_hr_q1_radio",
  "type": "single_choice",
  "evaluation_mode": "deterministic",
  "source_question_id": "module-1-Q1",
  "title": "Что такое скрининг резюме?",
  "data": {
    "options": ["...", "..."],
    "correct": "..."
  },
  "explanation": "...",
  "difficulty": "junior",
  "order": 1
}
```

### Deterministic Question Activities

For radio, checkbox, number, fill-blanks, matching:

```json
{
  "activity_type": "single_choice|multiple_choice|numeric|fill_blanks|matching",
  "evaluation_mode": "deterministic",
  "data": {
    "options": [],
    "correct": "value|values[]",
    "blanks": [],
    "template": "",
    "pairs": []
  },
  "explanation": "explanation text"
}
```

### AI-Evaluated Activities

For textarea/open questions:

```json
{
  "activity_type": "free_text|case_study|interview_answer",
  "evaluation_mode": "ai",
  "data": {
    "keywords": ["keyword1", "keyword2"],
    "minMatch": 3,
    "maxLength": 3000
  },
  "rubric_id": "ba_text_answer_rubric_v1",
  "explanation": "explanation text"
}
```

### Hybrid Activities

For textarea with keyword pre-check:

```json
{
  "activity_type": "free_text",
  "evaluation_mode": "hybrid",
  "data": {
    "keywords": ["keyword1", "keyword2"],
    "minMatch": 3,
    "deterministic_weight": 0.3,
    "ai_weight": 0.7
  },
  "rubric_id": "ba_text_answer_rubric_v1",
  "explanation": "explanation text"
}
```

---

## Rubrics

### BA-Specific Skill Map

```json
{
  "skill_map_id": "ba_interview_skill_map_v1",
  "skills": [
    { "skill_id": "ba_knowledge", "category": "ba_core", "name": "BA Knowledge & Methodology" },
    { "skill_id": "requirements_engineering", "category": "ba_core", "name": "Requirements Engineering" },
    { "skill_id": "process_modeling", "category": "ba_core", "name": "Process & Data Modeling" },
    { "skill_id": "documentation", "category": "ba_core", "name": "Documentation & Artifacts" },
    { "skill_id": "stakeholder_management", "category": "soft_skills", "name": "Stakeholder Management" },
    { "skill_id": "communication", "category": "soft_skills", "name": "Communication & Conflict Resolution" },
    { "skill_id": "technical_skills", "category": "ba_core", "name": "Technical Skills (SQL, API, etc.)" },
    { "skill_id": "analytical_thinking", "category": "ba_core", "name": "Analytical Thinking & Problem Solving" }
  ]
}
```

### Rubric Pack (Pattern)

Each scenario has a rubric with criteria matching the deterministic check or AI evaluation dimensions.

---

## Diagnostics

| Property | Value |
|---|---|
| Question count | 8 (fixed) |
| Level tiers | Junior, Middle, Senior |
| Algorithm | Weighted score per tier; ≥60% Senior → Senior, ≥60% Middle → Middle, else Junior |
| Questions per tier | Junior: 3, Middle: 3, Senior: 2 |
| Evaluation | Hybrid (deterministic for radio/checkbox/number/fill-blanks, keyword for textarea) |
| Rerun policy | Allowed any time (overwrites previous result) |
| Persistence | `SkillScore` per skill per user |
| Recommendation | Based on detected level — suggest starting module |

---

## Exam

| Property | Value |
|---|---|
| Question count | 25 (randomly selected from pool per session) |
| Timer | 45 minutes |
| Evaluation | Deterministic for closed types, AI for open-text |
| Scoring | Correct count / total × 100 |
| Pass threshold | 70% |
| Retry policy | Unlimited; each retry generates new random selection |
| Immutability | Each exam attempt is immutable once completed |
| Persistence | `ExamSession` model + `Attempt` records per question |

---

## Progress Model

| Source Field | Target Mapping |
|---|---|
| `answers` | `Attempt` records per activity |
| `answer.status` | `Attempt.status` (correct/incorrect/partial) |
| `attempts` | `Attempt.attempts_count` / retry tracking |
| `diagnosticsResult` | `SkillScore` for diagnostic skills + `TrainerProgress.metadata_json` |
| `examResult` | `ExamSession` + aggregated `Evaluation` |
| `xp` | Optional `XPLedger` table or `TrainerProgress.metadata_json` |
| `lastActive` | `TrainerProgress.last_activity_at` |

---

## Analytics Events

| Event Type | Trigger | Properties |
|---|---|---|
| `ba_trainer_opened` | User visits trainer page | `{training_session_id}` |
| `ba_module_opened` | User opens a module | `{module_id, module_title}` |
| `ba_activity_started` | User starts an activity | `{activity_id, type, evaluation_mode}` |
| `ba_answer_submitted` | User submits an answer | `{activity_id, type, evaluation_mode}` (not raw answer) |
| `ba_answer_evaluated` | Evaluation completed | `{activity_id, status, score, evaluation_mode, latency_ms}` |
| `ba_hint_used` | User requests a hint | `{activity_id}` |
| `ba_diagnostics_started` | User starts diagnostics | `{}` |
| `ba_diagnostics_completed` | Diagnostics finished | `{level, scores}` |
| `ba_exam_started` | User starts exam | `{question_count, duration_minutes}` |
| `ba_exam_completed` | Exam finished | `{score, total, time_spent, passed}` |
| `ba_report_viewed` | User views report | `{report_type}` |

### Privacy Rules

| Rule | Value |
|---|---|
| Raw answers in analytics | false |
| Personal data in analytics | false |
| DeepSeek reasoning in analytics | false |
| Secrets in analytics | false |

---

## Localization Keys

All user-facing strings require `ru-RU` keys. English `en-US` should be added in a later iteration.

```json
{
  "ba_trainer": {
    "name": "Business Analyst Interview Trainer",
    "name_ru": "Тренажёр собеседования бизнес-аналитика",
    "description": "...",
    "description_ru": "..."
  }
}
```

---

## Assets

Required assets to migrate from source:

| Source File | Target Path | Size | Notes |
|---|---|---|---|
| `public/favicon.svg` | `trainer_packages/.../assets/favicon.svg` | 9.5 KB | BA-branded |
| `public/icons.svg` | `trainer_packages/.../assets/icons.svg` | 5.1 KB | BA-branded |
| `public/logo.png` | `trainer_packages/.../assets/logo.png` | 1.6 MB | Compress/resize |
| `public/exam-btn.png` | `trainer_packages/.../assets/exam-btn.png` | 1.3 MB | Compress/resize |

---

## Versioning

| Version | Status | Content |
|---|---|---|
| 0.1.0 | draft | Initial migration spec |
| 0.2.0 | planned | Phase 1 implementation: deterministic questions + basic modules |
| 0.3.0 | planned | Phase 2: AI evaluation + diagnostics |
| 1.0.0 | planned | Phase 3: exam + full parity + production release |

---

## Migration Metadata

Each migrated scenario/activity must carry:

```json
{
  "_migration": {
    "source_repository": "solomonczyk/bi-trainer-local",
    "source_question_id": "module-1-Q1",
    "migration_date": "2026-06-06",
    "migration_version": "0.1.0",
    "requires_human_review": false
  }
}
```
