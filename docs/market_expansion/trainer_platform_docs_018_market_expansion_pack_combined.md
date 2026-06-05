# Trainer Platform — DOCS-018 Market Expansion, Localization & Compliance Pack

**Generated:** 2026-06-05

---



<!-- FILE: 18_master_index_market_expansion_pack.md -->

# 18. Master Index — Market Expansion, Localization & Compliance Pack

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05  
**Status:** Draft for development planning  
**Owner:** Product / Architecture / Compliance / Localization

---

## 1. Purpose

This documentation pack prepares Trainer Platform for further development as a multi-market, multi-language, multi-trainer platform.

The core decision is:

```text
One platform core
→ market-specific packs
→ locale packs
→ trainer packs
→ scenario packs
→ rubric packs
→ QA / legal / launch gates
```

This means the platform can be technically global, but each market launch must be treated as a controlled product layer.

---

## 2. Included documents

1. `18_master_index_market_expansion_pack.md` — this index.
2. `18_1_market_expansion_strategy.md` — market selection and expansion strategy.
3. `18_2_country_region_launch_playbook_template.md` — reusable launch template for each country/region.
4. `18_3_localization_cultural_adaptation_guide.md` — localization rules beyond translation.
5. `18_4_market_pack_trainer_pack_specification.md` — technical/product contract for Market Pack / Trainer Pack / Scenario Pack.
6. `18_5_compliance_privacy_by_market_matrix.md` — compliance planning matrix and legal review gates.
7. `18_6_payments_pricing_market_strategy.md` — pricing, payment providers, VAT/tax planning, local affordability.
8. `18_7_go_to_market_channels_validation_plan.md` — B2C/B2B validation and channel strategy.
9. `18_8_country_launch_acceptance_gates.md` — acceptance gates before market launch.
10. `18_9_agent_task_market_expansion_docs_implementation.md` — agent-ready implementation task.
11. `18_10_proof_json_schema_market_expansion_pack.md` — proof JSON schema for acceptance.

---

## 3. Development principle

The platform must not assume that one translated trainer is ready for every market.

For every new market, development must answer:

- Who is the target user?
- What profession/trainer is launched first?
- What language and country variant is required?
- What local job/interview/sales/support context is different?
- What legal/privacy/payment constraints exist?
- What acceptance gates must pass before launch?
- What analytics prove the market is worth deeper investment?

---

## 4. Recommended first expansion sequence

```json
{
  "phase_1": {
    "markets": ["ru-RU audience", "en-US/en-global remote candidates"],
    "trainers": ["QA Engineer Interview Trainer"],
    "goal": "validate core demand and AI scoring"
  },
  "phase_2": {
    "markets": ["uk-UA", "sr-RS / Balkans"],
    "trainers": ["QA Interview", "Prompt Engineer / AI Specialist Interview"],
    "goal": "validate localization and local-market adaptation"
  },
  "phase_3": {
    "markets": ["EU English", "Germany", "France", "Spain"],
    "trainers": ["Interview", "Sales", "Customer Support"],
    "goal": "B2B and broader commercial packaging"
  }
}
```

---

## 5. Source of truth hierarchy

1. Master Project Documentation Index.
2. Architecture and implementation specifications.
3. This Market Expansion Pack.
4. Country/region launch playbooks.
5. Market Pack contracts.
6. Trainer Pack / Scenario Pack / Rubric Pack specs.
7. QA, compliance and launch proofs.

---

## 6. Acceptance status

```json
{
  "market_expansion_pack_created": true,
  "ready_for_development_planning": true,
  "ready_for_market_launch": false,
  "requires_country_specific_validation": true,
  "requires_legal_review_before_paid_launch": true
}
```


<!-- FILE: 18_1_market_expansion_strategy.md -->

# 18.1 Market Expansion Strategy

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05

---

## Goal

Define how Trainer Platform should choose, prepare and validate new markets without breaking product focus.

---

## Strategic decision

Trainer Platform should not launch “everywhere” at once.

Correct strategy:

```text
Core Platform
→ one validated trainer
→ one or two priority markets
→ measured traction
→ controlled expansion
```

---

## Market scoring model

Each candidate market must be scored from 1 to 5.

| Criterion | Meaning |
|---|---|
| Demand | How strongly users need interview/simulation training |
| Payment capacity | Ability to pay for B2C or B2B |
| Localization complexity | How hard it is to adapt language and content |
| Legal/compliance complexity | Privacy, AI, employment, payments |
| Competition | Existing alternatives and differentiation |
| Founder advantage | Language, network, cultural understanding |
| B2B potential | Companies, schools, bootcamps, HR/L&D |

### Score formula

```text
Market Attractiveness =
Demand + Payment Capacity + Founder Advantage + B2B Potential
- Localization Complexity
- Legal Complexity
- Competition Pressure
```

---

## Priority markets

### Tier 1 — fastest validation

```json
{
  "markets": ["ru-RU audience", "en-global remote candidates"],
  "reason": "fast content creation, clear demand, easier first feedback loop",
  "first_trainer": "QA Engineer Interview Trainer",
  "launch_type": "controlled beta"
}
```

### Tier 2 — strategic localization

```json
{
  "markets": ["uk-UA", "sr-RS / Balkans"],
  "reason": "regional relevance, founder context, lower competition in local language",
  "first_trainer": "QA / Prompt Engineer / Customer Support",
  "launch_type": "localized beta"
}
```

### Tier 3 — commercial expansion

```json
{
  "markets": ["EU English", "Germany", "France", "Spain"],
  "reason": "larger B2B and paid market potential",
  "first_trainer": "Interview + Sales + Customer Support",
  "launch_type": "paid pilot"
}
```

---

## Market entry modes

### B2C beta

Best for early validation.

- individual candidates;
- low price or free beta;
- fast feedback;
- analytics-driven iteration.

### B2B pilot

Best after product proof.

- bootcamps;
- language schools;
- HR agencies;
- IT academies;
- recruiting agencies;
- corporate L&D.

### Expert partner launch

Best for specialized trainers.

- local expert creates/reviews scenarios;
- platform provides engine;
- expert provides trust/content;
- revenue share possible later.

---

## Forbidden expansion behavior

Do not:

- launch 10 markets at once;
- translate content without adapting scenarios;
- sell paid product without privacy/payment/legal review;
- claim job placement guarantees;
- claim AI score is an official certification;
- launch medical/legal/regulated simulators without expert review;
- enable real user scale before analytics and support process exist.

---

## Output per market

Each market must produce:

```json
{
  "market_playbook": true,
  "locale_pack": true,
  "trainer_pack": true,
  "scenario_pack": true,
  "rubric_pack": true,
  "qa_test_set": true,
  "legal_privacy_review": true,
  "payment_strategy": true,
  "launch_acceptance_gate": true
}
```


<!-- FILE: 18_2_country_region_launch_playbook_template.md -->

# 18.2 Country / Region Launch Playbook Template

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05

---

## Purpose

This template must be copied for every new country or region before development starts.

Example filenames:

```text
market_playbook_ru_ru.md
market_playbook_en_global.md
market_playbook_sr_rs.md
market_playbook_uk_ua.md
market_playbook_de_de.md
```

---

# Market Playbook Template

## 1. Market identity

```json
{
  "market_id": "",
  "country_or_region": "",
  "primary_language": "",
  "secondary_languages": [],
  "locale_codes": [],
  "launch_type": "B2C_beta|B2B_pilot|paid_public_beta|production",
  "launch_owner": "",
  "status": "draft"
}
```

---

## 2. Target users

Describe:

- primary user segment;
- secondary user segment;
- user pain;
- urgency;
- ability to pay;
- current alternatives.

Example:

```text
Junior QA candidates preparing for interviews in Russian-speaking IT market.
They need practice, structured answers, feedback and confidence before real interviews.
```

---

## 3. First trainer for this market

```json
{
  "trainer_id": "",
  "trainer_type": "interview|sales|support|english|cybersecurity|custom",
  "specialty": "",
  "level": "junior|middle|senior|mixed",
  "language": "",
  "country_context_required": true
}
```

---

## 4. Market-specific content differences

Document:

- interview style;
- common questions;
- expected answer depth;
- local CV/resume expectations;
- salary/motivation discussion norms;
- cultural communication style;
- forbidden or risky examples;
- local terminology.

---

## 5. Localization requirements

```json
{
  "ui_translation_required": true,
  "scenario_translation_required": true,
  "scenario_adaptation_required": true,
  "rubric_adaptation_required": true,
  "examples_adaptation_required": true,
  "human_review_required": true
}
```

---

## 6. Legal / privacy planning

This is a planning artifact, not legal advice.

Must answer:

- Are users from EU/EEA?
- Is GDPR or equivalent privacy law relevant?
- Are minors allowed?
- Are employment/assessment disclaimers needed?
- Do we store user answers?
- Do we store AI feedback?
- What is the retention period?
- What deletion/export rights are offered?
- What consent/cookie banner is required?
- Is B2B DPA needed?

---

## 7. Payments and pricing

```json
{
  "currency": "",
  "b2c_price_hypothesis": "",
  "b2b_price_hypothesis": "",
  "payment_providers": [],
  "tax_vat_review_required": true,
  "refund_policy_required": true
}
```

---

## 8. Launch channels

List:

- communities;
- Telegram/Discord/Facebook/LinkedIn groups;
- job boards;
- local bootcamps;
- language schools;
- recruiters;
- HR/L&D contacts;
- paid ads if applicable.

---

## 9. MVP launch criteria

```json
{
  "market_pack_ready": false,
  "trainer_pack_ready": false,
  "locale_pack_ready": false,
  "qa_passed": false,
  "privacy_review_done": false,
  "payment_review_done": false,
  "support_process_ready": false,
  "analytics_ready": false,
  "launch_allowed": false
}
```

---

## 10. Post-launch metrics

Track:

- visitors;
- signups;
- started simulations;
- completed simulations;
- AI evaluation success rate;
- average score improvement;
- retention;
- feedback quality;
- conversion to paid;
- support issues;
- refunds;
- privacy requests.

---

## 11. Launch verdict

```json
{
  "verdict": "ACCEPTED|ACCEPTED_WITH_BLOCKERS|REJECTED|NEEDS_FIX",
  "launch_allowed": false,
  "paid_launch_allowed": false,
  "production_accepted": false,
  "blockers": []
}
```


<!-- FILE: 18_3_localization_cultural_adaptation_guide.md -->

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


<!-- FILE: 18_4_market_pack_trainer_pack_specification.md -->

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


<!-- FILE: 18_5_compliance_privacy_by_market_matrix.md -->

# 18.5 Compliance & Privacy by Market Matrix

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05  
**Status:** Planning artifact, not legal advice

---

## Important disclaimer

This document is not legal advice. It defines what product and engineering teams must prepare before legal review.

A market launch must not be accepted only because the app works technically.

---

## Goal

Create a repeatable checklist for privacy, AI, employment, payment and data-retention requirements by market.

---

## Core data categories

Trainer Platform may process:

- account data;
- email/login identifiers;
- country/language preferences;
- user answers;
- AI evaluation result;
- progress data;
- analytics events;
- support messages;
- payment data later;
- B2B organization/team data later.

---

## Privacy classification

| Data | Risk | Notes |
|---|---:|---|
| Email/login | Medium | Personal data |
| User answers | Medium/High | May include personal career info |
| AI feedback | Medium | Can affect user perception |
| Progress/score | Medium | Educational/performance data |
| Analytics | Low/Medium | Must avoid raw answers |
| Payment data | High | Use provider; avoid storing card data |
| Voice recordings later | High | Separate consent needed |

---

## Market compliance matrix template

| Market | Privacy regime | Consent needed | Data deletion/export | Cookies/analytics | AI disclaimer | Legal review required |
|---|---|---|---|---|---|---|
| ru-RU audience | TBD | TBD | Yes | Yes | Yes | Yes |
| en-global | Depends on user location | Yes | Yes | Yes | Yes | Yes |
| EU/EEA | GDPR likely relevant | Yes | Yes | Yes | Yes | Yes |
| Serbia | Local privacy review required | Yes | Yes | Yes | Yes | Yes |
| Ukraine | Local privacy review required | Yes | Yes | Yes | Yes | Yes |
| USA | State privacy review may be required | Yes | Yes | Yes | Yes | Yes |

---

## Required legal documents before paid launch

Minimum:

- Privacy Policy;
- Terms of Use;
- AI Evaluation Disclaimer;
- Cookie Policy;
- Data Retention Policy;
- User Data Deletion Request Process;
- Support / Contact Policy;
- B2B DPA template if selling to organizations;
- Refund Policy if paid B2C;
- Acceptable Use Policy.

---

## AI disclaimer requirements

The product must clearly state:

- AI feedback is training feedback, not official certification;
- scores are approximate and rubric-based;
- the platform does not guarantee employment;
- users should not enter highly sensitive personal data;
- AI outputs may need human review in high-stakes contexts.

---

## Engineering controls

Required:

```json
{
  "raw_answers_not_stored_in_analytics": true,
  "data_retention_configurable": true,
  "user_delete_request_process": true,
  "export_user_data_process": true,
  "consent_records_stored": true,
  "ai_prompt_logging_policy_defined": true,
  "sensitive_data_redaction_planned": true,
  "market_launch_blocked_without_privacy_review": true
}
```

---

## Forbidden before compliance acceptance

Do not:

- launch paid public product in a market without privacy/legal review;
- sell B2B without DPA review;
- collect voice recordings without explicit voice consent;
- store raw answers in analytics;
- publish AI score as employment certification;
- target minors without a dedicated age/parental consent policy;
- claim legal compliance without review.

---

## Launch gate

```json
{
  "privacy_policy_ready": false,
  "terms_ready": false,
  "ai_disclaimer_ready": false,
  "cookie_policy_ready": false,
  "data_retention_policy_ready": false,
  "delete_export_process_ready": false,
  "legal_review_done": false,
  "market_launch_allowed": false
}
```


<!-- FILE: 18_6_payments_pricing_market_strategy.md -->

# 18.6 Payments & Pricing Market Strategy

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05

---

## Goal

Define payment and pricing strategy for future B2C/B2B launch across markets.

---

## Current rule

Payments are not part of the current MVP launch.

Before enabling payments:

```json
{
  "payment_provider_selected": false,
  "tax_vat_review_done": false,
  "refund_policy_ready": false,
  "checkout_security_review_done": false,
  "production_accepted": false
}
```

---

## Pricing models

### B2C

Possible models:

- free beta;
- one-time trainer pack purchase;
- monthly subscription;
- 7-day / 30-day interview prep pass;
- pay-per-simulation pack.

Recommended early model:

```json
{
  "model": "controlled beta → low-cost paid pilot",
  "reason": "validate willingness to pay before complex billing"
}
```

### B2B

Possible models:

- per seat per month;
- per cohort;
- per organization package;
- white-label trainer pack;
- expert/academy partnership.

Recommended B2B pilot:

```json
{
  "model": "fixed pilot fee for 1 cohort",
  "duration": "4-8 weeks",
  "includes": ["trainer access", "analytics report", "feedback summary"]
}
```

---

## Market pricing worksheet

For every market:

```json
{
  "market_id": "",
  "currency": "",
  "b2c_price_min": "",
  "b2c_price_target": "",
  "b2c_price_max": "",
  "b2b_pilot_price": "",
  "payment_provider_options": [],
  "tax_vat_review_required": true,
  "refund_policy_required": true,
  "local_affordability_notes": ""
}
```

---

## Payment provider planning

Possible providers to evaluate:

- Stripe;
- Paddle;
- Lemon Squeezy;
- local bank transfer for B2B;
- invoices for organizations.

Selection criteria:

- supported countries;
- supported currencies;
- tax/VAT handling;
- subscription support;
- refund support;
- webhook reliability;
- compliance burden;
- payout availability.

---

## Engineering requirements before payment

Required modules:

- plans;
- subscriptions;
- invoices;
- payment provider abstraction;
- webhook handling;
- entitlement system;
- refund state;
- billing audit log.

---

## Forbidden before payment launch

Do not:

- hardcode one payment provider into core domain logic;
- store card data directly;
- accept payments without refund policy;
- accept payments without Terms/Privacy/AI disclaimer;
- enable paid public launch without tax/VAT review;
- mix staging and production payment credentials;
- use production payment keys in development.

---

## Payment acceptance gate

```json
{
  "provider_selected": false,
  "provider_test_mode_passed": false,
  "webhook_tests_passed": false,
  "entitlement_tests_passed": false,
  "refund_policy_ready": false,
  "tax_vat_review_done": false,
  "no_card_data_stored": true,
  "payment_launch_allowed": false
}
```


<!-- FILE: 18_7_go_to_market_channels_validation_plan.md -->

# 18.7 Go-To-Market Channels & Validation Plan

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05

---

## Goal

Define how to validate demand before scaling development.

---

## Main GTM principle

Do not scale engineering before proving that users complete simulations and value the feedback.

---

## Validation stages

### Stage 1 — Manual beta

Goal:

- 5–10 users;
- observe real behavior;
- collect feedback;
- find confusion points.

Success criteria:

```json
{
  "users_invited": 10,
  "users_completed_simulation": ">=5",
  "critical_bugs": 0,
  "ai_feedback_understood": true,
  "users_want_retry": true
}
```

### Stage 2 — Controlled public beta

Goal:

- 50–100 users;
- validate analytics;
- test conversion to waitlist or paid interest.

Success criteria:

```json
{
  "signups": ">=50",
  "simulation_completion_rate": ">=40%",
  "ai_eval_success_rate": ">=95%",
  "negative_feedback_rate": "<=15%",
  "willingness_to_pay_signal": true
}
```

### Stage 3 — B2B pilot

Goal:

- one organization or course group;
- group analytics;
- cohort report.

Success criteria:

```json
{
  "organization_signed": true,
  "participants": ">=10",
  "completion_rate": ">=50%",
  "manager_report_useful": true,
  "renewal_interest": true
}
```

---

## Channel list

### B2C

- Telegram communities;
- LinkedIn posts;
- Reddit/Discord communities where appropriate;
- job-seeker groups;
- IT bootcamp alumni;
- YouTube/short video demos;
- landing page SEO;
- partner newsletters.

### B2B

- IT schools;
- QA bootcamps;
- language schools;
- HR/recruiting agencies;
- corporate L&D;
- career centers;
- local tech communities.

---

## Validation assets

Required before outreach:

- short landing page;
- product demo video/GIF;
- example AI feedback screenshot;
- beta invitation text;
- feedback form;
- issue registry;
- FAQ;
- privacy/AI disclaimer.

---

## Metrics to track

```json
{
  "landing_opened": true,
  "signup_started": true,
  "signup_completed": true,
  "trainer_opened": true,
  "scenario_started": true,
  "answer_submitted": true,
  "evaluation_completed": true,
  "result_viewed": true,
  "retry_started": true,
  "feedback_submitted": true
}
```

---

## Do not do yet

Do not:

- buy paid ads before organic/manual validation;
- promise job results;
- launch too many trainers;
- start complex marketplace;
- overbuild B2B dashboards before one pilot confirms need.

---

## Output

Every GTM experiment must produce:

```json
{
  "experiment_id": "",
  "market_id": "",
  "target_segment": "",
  "channel": "",
  "users_reached": 0,
  "signups": 0,
  "completed_simulations": 0,
  "feedback_summary": "",
  "decision": "continue|iterate|stop"
}
```


<!-- FILE: 18_8_country_launch_acceptance_gates.md -->

# 18.8 Country / Market Launch Acceptance Gates

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05

---

## Goal

Define objective gates before launching Trainer Platform in a new market.

---

## Gate philosophy

A market launch is not accepted only because pages load.

A market launch is accepted when:

```text
product + localization + compliance + payments + QA + analytics + support are ready for that market level
```

---

# Gate 1 — Market Pack Gate

Accepted when:

```json
{
  "market_playbook_created": true,
  "target_users_defined": true,
  "first_trainer_selected": true,
  "pricing_hypothesis_defined": true,
  "launch_channels_defined": true,
  "market_risks_documented": true
}
```

Rejected when:

- target audience is vague;
- first trainer is not selected;
- market-specific assumptions are not documented.

---

# Gate 2 — Locale Pack Gate

Accepted when:

```json
{
  "ui_locale_complete": true,
  "scenario_locale_complete": true,
  "rubric_locale_complete": true,
  "human_localization_review_done": true,
  "mixed_language_errors_absent": true
}
```

Rejected when:

- only raw machine translation exists;
- scenario examples do not match local context;
- AI feedback uses wrong tone or language.

---

# Gate 3 — Trainer Pack Gate

Accepted when:

```json
{
  "trainer_pack_valid": true,
  "scenario_pack_valid": true,
  "rubric_pack_valid": true,
  "golden_answer_set_valid": true,
  "critical_errors_defined": true,
  "ai_behavior_contract_valid": true
}
```

---

# Gate 4 — Compliance / Privacy Gate

Accepted when:

```json
{
  "privacy_policy_ready": true,
  "terms_ready": true,
  "ai_disclaimer_ready": true,
  "data_retention_policy_ready": true,
  "delete_export_process_ready": true,
  "cookie_analytics_policy_ready": true,
  "legal_review_done_or_formal_beta_exception": true
}
```

---

# Gate 5 — Payment Gate

Required only for paid launch.

Accepted when:

```json
{
  "payment_provider_ready": true,
  "test_payments_passed": true,
  "refund_policy_ready": true,
  "tax_vat_review_done": true,
  "no_card_data_stored": true,
  "webhook_tests_passed": true
}
```

---

# Gate 6 — QA / AI Evaluation Gate

Accepted when:

```json
{
  "golden_answers_pass": true,
  "bad_answers_fail": true,
  "prompt_injection_blocked": true,
  "empty_answers_handled": true,
  "critical_errors_detected": true,
  "score_evidence_present": true,
  "no_invented_feedback": true
}
```

---

# Gate 7 — External Staging Gate

Accepted when:

```json
{
  "external_frontend_reachable": true,
  "external_backend_reachable": true,
  "database_ready": true,
  "migrations_applied": true,
  "trainer_seeded": true,
  "smoke_passed": true,
  "monitoring_ready": true
}
```

---

# Gate 8 — Launch Decision Gate

```json
{
  "market_id": "",
  "launch_type": "free_beta|paid_beta|b2b_pilot|production",
  "all_required_gates_passed": false,
  "production_accepted": false,
  "release_allowed": false,
  "launch_allowed": false,
  "accepted_by": "",
  "blockers": []
}
```

---

## Launch verdict rules

### ACCEPTED

Only if all required gates for that launch type pass.

### ACCEPTED_WITH_BLOCKERS

Allowed for internal beta if blockers are known and safe.

### REJECTED

If privacy/payment/AI safety/secret leakage/production gate is violated.

### NEEDS_FIX

If gate evidence is incomplete.


<!-- FILE: 18_9_agent_task_market_expansion_docs_implementation.md -->

# 18.9 Agent Task — Market Expansion Documentation Implementation

**Task ID:** TRAINER-PLATFORM-DOCS-018-MARKET-EXPANSION-LOCALIZATION-COMPLIANCE-PACK  
**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05

---

## ROLE

You are an architecture, product, localization and compliance documentation agent.

Your task is to integrate the Market Expansion Documentation Pack into the Trainer Platform repository as development-ready documentation.

---

## GOAL

Create a complete documentation layer for future multi-market development.

The layer must enable the team to add new country/region markets through controlled Market Packs, Locale Packs, Trainer Packs, Scenario Packs, Rubric Packs, QA gates and compliance gates.

---

## ALLOWED SCOPE

You may:

- create new docs under `docs/market_expansion/`;
- update the master documentation index;
- create templates for country launch playbooks;
- define Market Pack / Locale Pack / Trainer Pack schemas;
- define localization acceptance gates;
- define compliance/privacy planning matrix;
- define payments/pricing planning template;
- define GTM validation plan;
- define market launch gates;
- create proof JSON;
- create known issues file;
- commit, push and verify clean git.

---

## FORBIDDEN ACTIONS

Do not:

- change product code;
- deploy staging or production;
- enable real OpenAI;
- add new trainer content to database;
- add payments implementation;
- claim legal compliance as final;
- claim paid launch allowed;
- claim production accepted;
- write country-specific legal advice without legal review;
- store secrets;
- modify Railway/Vercel secrets;
- change MVP scope.

---

## REQUIRED IMPLEMENTATION

Create:

```text
docs/market_expansion/18_master_index_market_expansion_pack.md
docs/market_expansion/18_1_market_expansion_strategy.md
docs/market_expansion/18_2_country_region_launch_playbook_template.md
docs/market_expansion/18_3_localization_cultural_adaptation_guide.md
docs/market_expansion/18_4_market_pack_trainer_pack_specification.md
docs/market_expansion/18_5_compliance_privacy_by_market_matrix.md
docs/market_expansion/18_6_payments_pricing_market_strategy.md
docs/market_expansion/18_7_go_to_market_channels_validation_plan.md
docs/market_expansion/18_8_country_launch_acceptance_gates.md
docs/market_expansion/18_10_proof_json_schema_market_expansion_pack.md
docs/proofs/proof_trainer_platform_docs_018_market_expansion_pack.json
docs/known_issues/docs_018_known_issues.md
```

Update:

```text
docs/14.master_project_documentation_index.md
```

or current equivalent master documentation index.

---

## CONTROL POINTS

Before acceptance, verify:

- documents exist;
- master index links the new pack;
- docs do not claim legal compliance is complete;
- docs do not claim paid launch is allowed;
- docs support market-specific trainer packs;
- proof JSON exists;
- git committed/pushed/clean.

---

## REQUIRED TESTS / VERIFICATION

Run:

```bash
git status --short
find docs/market_expansion -type f
grep -R "production_accepted.*true" docs/market_expansion || true
grep -R "legal compliance complete" docs/market_expansion || true
```

If the repo has docs linting, run it.

---

## REQUIRED FINAL REPORT

```markdown
# TRAINER-PLATFORM-DOCS-018-MARKET-EXPANSION-LOCALIZATION-COMPLIANCE-PACK — Completion Report

## Verdict
ACCEPTED / ACCEPTED_WITH_BLOCKERS / REJECTED / NEEDS_FIX

## Summary

## Documents Created

## Master Index Update

## Compliance / Legal Disclaimer Check

## Forbidden Actions Check
- product_code_changed: false
- staging_deployed: false
- production_deployed: false
- real_openai_enabled: false
- payments_enabled: false
- production_accepted: false
- release_allowed: false

## Proof JSON
- path:

## Git
- branch:
- commit:
- pushed:
- clean:

## Known Issues

## Next Allowed Action
```

---

## ACCEPTANCE CRITERIA

```json
{
  "documents_created": true,
  "master_index_updated": true,
  "market_pack_model_defined": true,
  "localization_gate_defined": true,
  "compliance_gate_defined": true,
  "payment_gate_defined": true,
  "gtm_validation_plan_defined": true,
  "launch_acceptance_gates_defined": true,
  "legal_disclaimer_present": true,
  "no_product_code_changed": true,
  "production_accepted": false,
  "release_allowed": false,
  "git_pushed": true,
  "git_clean": true
}
```

---

## NEXT ALLOWED ACTION

After this docs layer is accepted:

```text
TRAINER-PLATFORM-MARKET-PACK-001-RU-EN-QA-TRAINER-LAUNCH-PLAYBOOK
```

or:

```text
TRAINER-PLATFORM-MARKET-PACK-001-EN-GLOBAL-QA-TRAINER-LAUNCH-PLAYBOOK
```


<!-- FILE: 18_10_proof_json_schema_market_expansion_pack.md -->

# 18.10 Proof JSON Schema — Market Expansion Pack

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05

---

## Required proof path

```text
docs/proofs/proof_trainer_platform_docs_018_market_expansion_pack.json
```

---

## Schema

```json
{
  "layer": "TRAINER-PLATFORM-DOCS-018-MARKET-EXPANSION-LOCALIZATION-COMPLIANCE-PACK",
  "date": "YYYY-MM-DD",
  "verdict": "TBD",
  "scope": {
    "documentation_only": true,
    "product_code_changed": false,
    "staging_deployed": false,
    "production_deployed": false,
    "real_openai_enabled": false,
    "payments_enabled": false,
    "production_accepted": false,
    "release_allowed": false
  },
  "documents": {
    "master_index": false,
    "market_expansion_strategy": false,
    "country_launch_playbook_template": false,
    "localization_guide": false,
    "market_pack_specification": false,
    "compliance_privacy_matrix": false,
    "payments_pricing_strategy": false,
    "gtm_validation_plan": false,
    "country_launch_gates": false,
    "agent_task": false,
    "proof_schema": false
  },
  "coverage": {
    "market_selection_model_defined": false,
    "market_pack_model_defined": false,
    "locale_pack_model_defined": false,
    "trainer_pack_model_defined": false,
    "scenario_pack_model_defined": false,
    "rubric_pack_model_defined": false,
    "golden_answer_set_required": false,
    "localization_beyond_translation_defined": false,
    "privacy_legal_review_gate_defined": false,
    "payment_gate_defined": false,
    "gtm_validation_defined": false,
    "launch_acceptance_gates_defined": false
  },
  "safety": {
    "legal_disclaimer_present": false,
    "no_claim_of_final_legal_compliance": true,
    "no_paid_launch_allowed": true,
    "no_market_launch_allowed_without_gates": true,
    "no_secrets_in_docs": true
  },
  "git": {
    "branch": "",
    "commit": "",
    "pushed": false,
    "clean": false
  },
  "known_issues": [],
  "next_allowed_action": "TBD"
}
```

---

## Acceptance values

For ACCEPTED:

```json
{
  "documentation_only": true,
  "all_documents_created": true,
  "all_coverage_true": true,
  "legal_disclaimer_present": true,
  "production_accepted": false,
  "release_allowed": false,
  "git_pushed": true,
  "git_clean": true
}
```


<!-- FILE: docs_018_known_issues.md -->

# Known Issues — DOCS-018 Market Expansion Pack

**Project:** Trainer Platform  
**Date:** 2026-06-05

---

## Known issues

1. Country-specific legal requirements are not final legal advice.
   - Status: expected.
   - Required action: legal review before paid launch in each target market.

2. Pricing is hypothesis-level only.
   - Status: expected.
   - Required action: validate through beta/pilot.

3. Payment provider selection is not final.
   - Status: expected.
   - Required action: provider/country review before implementation.

4. Localization reviewers are not assigned yet.
   - Status: blocker before publication of localized market packs.

5. Market launch priority must be confirmed by operator/product owner.
   - Status: decision required before building first Market Pack.

---

## Not blockers for documentation acceptance

These issues do not block acceptance of DOCS-018 because this layer is documentation/planning only.

They do block paid/public market launch.
