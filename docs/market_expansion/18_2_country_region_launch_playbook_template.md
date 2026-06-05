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
