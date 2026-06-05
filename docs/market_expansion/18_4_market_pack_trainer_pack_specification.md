# 18.4 Market Pack / Trainer Pack / Scenario Pack Specification

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05

---

## Goal

Define the product and technical contract for creating market-specific trainer packages.

---

## Package hierarchy

```text
Market Pack
├── Locale Pack
├── Trainer Pack
│   ├── Scenario Pack
│   ├── Rubric Pack
│   ├── Skill Map
│   ├── Golden Answer Set
│   └── QA Test Set
└── Launch Gate
```

---

## 1. Market Pack

A Market Pack defines market-level context.

```json
{
  "market_id": "ru_ru",
  "market_name": "Russian-speaking IT candidates",
  "country_or_region": "multi-country",
  "primary_locales": ["ru-RU"],
  "secondary_locales": ["en-US"],
  "target_segments": [],
  "legal_review_required": true,
  "payment_review_required": true,
  "launch_status": "draft"
}
```

Required fields:

- market_id;
- country/region;
- target users;
- supported locales;
- launch model;
- payment model;
- privacy model;
- support model;
- accepted trainer packs.

---

## 2. Trainer Pack

A Trainer Pack defines a profession-specific simulator.

```json
{
  "trainer_id": "qa_engineer_interview_ru_ru_v1",
  "trainer_type": "interview",
  "specialty": "QA Engineer",
  "market_id": "ru_ru",
  "locales": ["ru-RU", "en-US"],
  "levels": ["junior"],
  "version": "1.0.0",
  "status": "draft|review|published|deprecated"
}
```

Required fields:

- trainer title;
- specialty;
- market;
- locale list;
- level list;
- scenario list;
- rubric reference;
- skill map;
- AI behavior contract;
- forbidden AI behavior;
- QA test set;
- publication gate.

---

## 3. Scenario Pack

```json
{
  "scenario_id": "bug_report_interview_ru_ru_v1",
  "trainer_id": "qa_engineer_interview_ru_ru_v1",
  "locale": "ru-RU",
  "goal": "Evaluate candidate ability to explain bug report structure",
  "estimated_minutes": 8,
  "mode": "text",
  "rubric_id": "qa_interview_rubric_v1",
  "critical_errors": []
}
```

Scenario must include:

- goal;
- setup;
- user role;
- AI interviewer role;
- steps;
- expected answer patterns;
- weak answer patterns;
- critical errors;
- completion rules;
- evaluation trigger.

---

## 4. Rubric Pack

```json
{
  "rubric_id": "qa_interview_rubric_v1",
  "criteria": [
    {
      "id": "clarity",
      "weight": 20,
      "min_score": 0,
      "max_score": 100,
      "evidence_required": true
    }
  ],
  "critical_error_policy": {
    "critical_error_can_fail_attempt": true
  }
}
```

Rubric must define:

- criteria;
- weights;
- score scale;
- evidence requirements;
- pass threshold;
- critical errors;
- localized feedback rules.

---

## 5. Golden Answer Set

Each scenario needs examples:

- excellent answer;
- good answer;
- average answer;
- weak answer;
- off-topic answer;
- unsafe answer;
- prompt injection attempt;
- empty answer.

Each example must include expected score range and expected feedback.

---

## 6. Publication lifecycle

```text
draft
→ author_review
→ localization_review
→ QA_review
→ AI_regression_test
→ expert_review_if_required
→ staging_publish
→ production_candidate
→ published
```

---

## 7. Required validation commands

Each pack must support validation:

```bash
validate_market_pack <market_id>
validate_locale_pack <locale_id>
validate_trainer_pack <trainer_id>
validate_scenario_pack <scenario_id>
validate_rubric_pack <rubric_id>
validate_golden_answers <trainer_id>
```

---

## Acceptance criteria

```json
{
  "market_pack_valid": false,
  "locale_pack_valid": false,
  "trainer_pack_valid": false,
  "scenario_pack_valid": false,
  "rubric_pack_valid": false,
  "golden_answer_set_valid": false,
  "qa_test_set_valid": false,
  "publish_allowed": false
}
```
