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
