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
