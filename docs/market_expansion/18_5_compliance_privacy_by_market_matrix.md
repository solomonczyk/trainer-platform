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
