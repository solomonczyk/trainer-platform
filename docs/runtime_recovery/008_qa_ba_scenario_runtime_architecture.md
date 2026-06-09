# 008 — QA/BA Scenario Runtime Architecture

## Layer

TRAINER-PLATFORM-QA-BA-SCENARIO-RUNTIME-AND-FULL-I18N-VERTICAL-RECOVERY-008

## Date

2026-06-09

## Overview

This document describes the recovered runtime architecture for QA and BA
scenario execution, including the localization pipeline that serves both
ru-RU and en-US locales across the full user-facing flow.

## Architecture

### Component Diagram

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Next.js UI  │────▶│  API Client      │────▶│  FastAPI      │
│  (React SFC) │     │  (lib/api)       │     │  Backend      │
└──────┬───────┘     └──────────────────┘     └──────┬───────┘
       │                                              │
       ▼                                              ▼
┌──────────────┐                          ┌──────────────────┐
│ i18n Module  │                          │ Scenario Service │
│ (useState)   │                          │ + AI Gateway     │
└──────┬───────┘                          └──────────────────┘
       │
       ▼
┌──────────────┐
│ ru-RU / en-US│
│ JSON dicts   │
└──────────────┘
```

### User Flow

```
Home ─▶ Domains ─▶ Domain Detail ─▶ Trainer Detail
  └──▶ Scenario List ─▶ Scenario Detail ─▶ Answer ─▶ AI Evaluation ─▶ Result ─▶ Progress
```

### API Route Contract

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/v1/domains` | List domains |
| GET | `/api/v1/domains/{slug}` | Domain detail with trainers |
| GET | `/api/v1/trainers/{slug}` | Trainer detail |
| GET | `/api/v1/trainers/{slug}/scenarios` | List trainer scenarios |
| GET | `/api/v1/scenarios/{id}` | Scenario detail |
| POST | `/api/v1/scenarios/{id}/start` | Start scenario session |
| POST | `/api/v1/sessions/{id}/messages` | Submit answer message |
| POST | `/api/v1/sessions/{id}/complete` | Complete session |
| POST | `/api/v1/attempts/{id}/evaluate` | Request AI evaluation |
| GET | `/api/v1/attempts/{id}/evaluation` | Get evaluation result |
| GET | `/api/v1/me/progress` | User progress summary |
| GET | `/api/v1/me/progress/{slug}` | Trainer-specific progress |

### Localization Pipeline

1. Frontend calls `t(key)` from `lib/i18n/index.ts`
2. Resolver traverses namespace chain in `locales[currentLocale]`
3. If key found at terminal string node → return translated text
4. If key not found → return raw key (caller expected to handle via `tl()`)
5. All scenario/domain/trainer content now has entries in both locales

## Key Types

### ScenarioDetail (API Response)

```typescript
interface ScenarioDetail {
  id: string;
  scenario_id: string;
  title_key: string;
  goal_key: string;
  trainer_product_id: string;
  difficulty: string;
  target_skills: Array<string | { skill_id: string; weight: number }>;
  steps?: Array<{ step_id: string; order: number; prompt_key: string; ... }>;
  hints?: string[];
  user_role: string;
  ai_role: string;
}
```

### EvaluationResult (API Response)

```typescript
interface EvaluationResult {
  id: string;
  attempt_id: string;
  overall_score: number;
  passed: boolean;
  criteria: CriterionResult[];
  strengths: string[];
  weak_points: string[];
  critical_errors: string[];
  next_recommendation?: { action: string; description: string };
  confidence: number;
  ai_model_used?: string;
}
```

## Rendering Safety

All React components follow:

```typescript
// Safe object-to-text rendering:
skills.map((skill) => (
  <span key={typeof skill === "string" ? skill : skill.skill_id}>
    {typeof skill === "string" ? skill : skill.skill_id}
  </span>
))

// Safe key-localization:
<h1>{t(scenario.title_key)}</h1>
<p>{t(scenario.goal_key)}</p>

// Localized trainer/domain names:
<h1>{t(`trainer.${id}`) !== t(`trainer.${id}`) ? t(`trainer.${id}`) : apiName}</h1>
```
