# 18.3 Localization & Cultural Adaptation Guide

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05

---

## Goal

Define how Trainer Platform localizes trainers for different markets.

The core rule:

```text
Localization is not translation.
Localization = language + country + market + profession + cultural context.
```

---

## Localization layers

### 1. UI localization

- menus;
- buttons;
- errors;
- navigation;
- system messages;
- empty states;
- notifications.

### 2. Product localization

- trainer names;
- trainer descriptions;
- onboarding text;
- value proposition;
- pricing copy;
- FAQ.

### 3. Scenario localization

- interview questions;
- role-play context;
- company type;
- local examples;
- seniority expectations;
- communication style.

### 4. Rubric localization

Rubrics must adapt to:

- local communication norms;
- expected detail level;
- professional vocabulary;
- interview style;
- directness/indirectness;
- English vs native language expectations.

### 5. Legal/support localization

- privacy policy summary;
- AI disclaimer;
- terms;
- consent;
- support templates;
- refund terms;
- B2B documents.

---

## Locale Pack structure

```json
{
  "locale_id": "sr-RS",
  "language": "Serbian",
  "country": "Serbia",
  "ui_strings": "required",
  "product_copy": "required",
  "scenario_adaptation": "required",
  "rubric_adaptation": "required",
  "legal_copy_review": "required",
  "human_reviewer": "required"
}
```

---

## Quality standards

A localized trainer is accepted only if:

- UI strings are complete;
- no mixed-language user-facing text remains;
- scenarios sound natural for the target audience;
- scoring rubric matches market expectations;
- AI feedback uses appropriate tone;
- examples are locally understandable;
- legal/privacy text is reviewed;
- human reviewer approves content.

---

## Forbidden localization practices

Do not:

- machine-translate scenarios and publish without review;
- reuse salary or job-market examples across countries without checking;
- use slang that may be regionally wrong;
- claim official certification where none exists;
- let AI invent local laws, salaries or hiring norms;
- mix locales accidentally, for example `en-US` content inside `sr-RS`.

---

## Localization QA checklist

```json
{
  "ui_translation_complete": false,
  "scenario_adaptation_complete": false,
  "rubric_adaptation_complete": false,
  "ai_feedback_tone_approved": false,
  "local_examples_approved": false,
  "legal_copy_reviewed": false,
  "human_review_done": false,
  "localization_qa_passed": false
}
```

---

## AI behavior for localized scenarios

AI must:

- speak in selected locale unless task requires another language;
- evaluate according to localized rubric;
- not invent local legal/employment facts;
- admit uncertainty when asked market-specific facts;
- avoid discriminatory hiring advice;
- not store raw sensitive personal data in analytics.

---

## Acceptance

```json
{
  "locale_pack_status": "draft|review|accepted|rejected",
  "accepted_by": "",
  "review_notes": [],
  "publish_allowed": false
}
```
