# 008 — Localization Coverage Report

## Complete User Flow Coverage (ru-RU)

| Step | Localized | Raw Keys |
|------|-----------|----------|
| Home ❯ Hero | ✅ | 0 |
| Home ❯ CTA | ✅ | 0 |
| Home ❯ Features | ✅ | 0 |
| Domains ❯ List | ✅ | 0 |
| Domains ❯ Detail (IT) | ✅ | 0 |
| Domains ❯ Trainer List | ✅ | 0 |
| QA Trainer ❯ Detail | ✅ | 0 |
| QA Trainer ❯ Scenarios | ✅ | 0 |
| QA Scenario ❯ Detail | ✅ | 0 |
| QA Scenario ❯ Execution | ✅ | 0 |
| QA Scenario ❯ Evaluation | ✅ | 0 |
| BA Trainer ❯ Detail | ✅ | 0 |
| BA Trainer ❯ Phase 2 List | ✅ | 0 |
| BA Scenario ❯ Detail | ✅ | 0 |
| BA Scenario ❯ Execution | ✅ | 0 |
| BA Scenario ❯ Evaluation | ✅ | 0 |

## QA Scenario Translations

| Scenario ID | ru-RU title | ru-RU goal | en-US title | en-US goal | Raw Key |
|-------------|-------------|-------------|-------------|-------------|---------|
| `qa_self_presentation_v1` | ✅ | ✅ | ✅ | ✅ | 0 |
| `qa_test_case_vs_checklist_v1` | ✅ | ✅ | ✅ | ✅ | 0 |
| `qa_bug_report_structure_v1` | ✅ | ✅ | ✅ | ✅ | 0 |
| `qa_regression_vs_retest_v1` | ✅ | ✅ | ✅ | ✅ | 0 |
| `qa_login_form_testing_v1` | ✅ | ✅ | ✅ | ✅ | 0 |

## BA Scenario Translations

BA Phase 2 scenarios use top-level keys (e.g., `ba_phase2_stakeholder_requirements_title`).
These are already present in both ru-RU and en-US dictionaries with 6 entries each.

| Scenario ID | ru-RU title | en-US title |
|-------------|-------------|-------------|
| `ba_phase2_stakeholder_requirements` | ✅ | ✅ |
| `ba_phase2_process_analysis` | ✅ | ✅ |
| `ba_phase2_documentation_artifacts` | ✅ | ✅ |
| `ba_phase2_conflict_resolution` | ✅ | ✅ |
| `ba_phase2_traceability_impact` | ✅ | ✅ |
| `ba_phase2_real_case_analysis` | ✅ | ✅ |

## Key Counts

| Dictionary | Top-Level Namespaces | Total Keys |
|------------|---------------------|------------|
| `ru-RU.ts` | 14 | ~180+ |
| `en-US.ts` | 14 | ~180+ |

## Missing Keys

| Locale | Missing |
|--------|---------|
| ru-RU | 0 (zero for user-facing flow) |
| en-US | 0 (zero for user-facing flow) |

## Raw Key Detection

Automated search across loaded dictionaries found zero unresolved
`scenario.*.title` or `scenario.*.goal` patterns.
