# Human Expert Governance and Roles

**Document ID:** CGSF-GOVERNANCE-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define accountability, separation of duties, review panels and appeal authority.

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

## Required roles

| Role | Authority |
|---|---|
| Product Owner | Product outcome and prioritization |
| Assessment Architect | Blueprint and measurement model |
| Domain Expert | Content validity and source accuracy |
| Item Writer | Drafts items under specifications |
| Independent Reviewer | Reviews ambiguity and answer key |
| Psychometrician/Data Specialist | Calibration and reliability |
| AI/LLM Architect | Evaluator contracts and monitoring |
| QA Lead | Test strategy and acceptance evidence |
| Security/Privacy Reviewer | Data and integrity controls |
| Operator | Controlled runtime actions |

## Separation of duties

- item author cannot be sole final reviewer;
- LLM cannot approve exam eligibility;
- engineering cannot redefine pass score without assessment approval;
- production release requires independent QA and security review;
- candidate appeals require review outside the original automated evaluation.

## Decision records

Every high-impact decision must record:

- decision ID;
- scope and version;
- evidence reviewed;
- participants and conflicts of interest;
- decision and rationale;
- expiry/review date;
- downstream impact.

## Expert panel minimum outputs

- competency approval;
- blueprint approval;
- source registry approval;
- item pilot approval;
- standard-setting decision;
- rubric anchor approval;
- release recommendation.
