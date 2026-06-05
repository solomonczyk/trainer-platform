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
