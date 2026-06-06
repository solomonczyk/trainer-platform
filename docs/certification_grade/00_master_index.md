# Master Index - Certification-Grade Simulation Framework

**Document ID:** CGSF-INDEX-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define the complete documentation set required to evolve Trainer Platform from trainer activities into a governed, dynamic, certification-grade simulation platform.

## Current strategic state
```json
{
  "product_type": "certification_grade_assessment_and_exam_simulation_platform",
  "official_certificate_issuer": false,
  "quality_target": "comparable_to_serious_professional_and_language_exams",
  "current_vertical_slice": "BA Trainer Phase 1 REAL_STAGING_ACCEPTED",
  "production_accepted": false,
  "release_allowed": false
}
```

## Mandatory reading order

1. Product vision and quality standard.
2. Competency and exam blueprint framework.
3. Versioned knowledge registry.
4. Dynamic item bank architecture.
5. Controlled item generation and validation.
6. Item lifecycle and governance.
7. Rotation, exposure and compromise control.
8. Exam form assembly and equivalence.
9. Scoring and standard setting.
10. Psychometric calibration.
11. Rubric and AI evaluator calibration.
12. Adaptive learning and readiness prediction.
13. Exam session and integrity controls.
14. Data model and API contracts.
15. Analytics and effectiveness evidence.
16. Human expert governance.
17. Domain pack specification.
18. QA and validation strategy.
19. Security, privacy, copyright and legal boundaries.
20. Migration plan for existing BA and QA trainers.
21. Implementation roadmap.
22. Acceptance gates and proof contract.

## Document map

| # | Document | Primary implementation result |
|---|---|---|
| 01 | Product Vision & Quality Standard | Common definition of certification-grade |
| 02 | Competency & Exam Blueprint | Stable assessment structure |
| 03 | Knowledge Source Registry | Trusted and versioned knowledge |
| 04 | Dynamic Item Bank | Evolving question/scenario storage |
| 05 | Item Generation Pipeline | Controlled content creation |
| 06 | Item Lifecycle Governance | Draft-to-retirement state machine |
| 07 | Rotation & Exposure Control | Anti-memorization and compromise controls |
| 08 | Exam Form Assembly | Equivalent exam variants |
| 09 | Scoring & Standard Setting | Defensible pass/fail rules |
| 10 | Psychometric Calibration | Measured difficulty and reliability |
| 11 | Rubric & AI Calibration | Reliable open-response evaluation |
| 12 | Adaptive Learning | Personal practice and readiness |
| 13 | Exam Session Integrity | Timers, recovery and audit |
| 14 | Data & API Contracts | Implementable schemas/interfaces |
| 15 | Analytics & Effectiveness | Evidence that training works |
| 16 | Expert Governance | Human review and accountability |
| 17 | Domain Pack Specification | Repeatable expansion to any profession |
| 18 | QA Strategy | Full verification model |
| 19 | Security/Legal | Privacy and content boundaries |
| 20 | BA/QA Migration | Safe evolution of current products |
| 21 | Roadmap | Build order and dependencies |
| 22 | Acceptance Gates | Definition of Done and proof JSON |

## Core architecture principle

The platform must not store a one-time static list of questions. It must operate a **versioned, continuously evolving, calibrated and governed knowledge and item ecosystem**.

## Non-negotiable rules

- Simple quizzes are not acceptable as the final product.
- Every scored item maps to competency and blueprint nodes.
- Every exam-eligible item has provenance, validation and lifecycle state.
- Runtime LLM generation cannot directly enter high-stakes exam delivery.
- Exam forms must be equivalent, reproducible and auditable.
- User results must identify blueprint, item-bank, rubric and form versions.
- Human experts retain final authority for exam eligibility and scoring policy.
