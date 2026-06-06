# Exam Form Assembly and Equivalence

**Document ID:** CGSF-FORM-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Build multiple secure exam variants that satisfy the same blueprint, time and difficulty requirements.

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

## Form assembly inputs

- active blueprint version;
- exam-eligible item pool;
- candidate exposure history;
- target length and duration;
- domain/cognitive/difficulty constraints;
- locale and accessibility constraints;
- form overlap policy.

## Form contract

```json
{
  "form_id": "ba-exam-2026-06-001",
  "blueprint_version": "2.1",
  "item_bank_version": "ba-3.4",
  "knowledge_bank_version": "2026.06",
  "scoring_policy_version": "1.3",
  "duration_minutes": 90,
  "scored_items": 60,
  "pilot_items": 5,
  "target_difficulty": 0.55,
  "expected_information": 18.2,
  "assembly_seed_ref": "secure",
  "status": "published"
}
```

## Assembly methods

### Rule-based constrained assembly

Initial implementation: deterministic optimization using blueprint quotas, difficulty bands, time and exposure constraints.

### Automated test assembly

Later implementation: optimization objective minimizes blueprint deviation, difficulty difference, content overlap and measurement error.

## Equivalence checks

- blueprint coverage difference within tolerance;
- mean difficulty within tolerance;
- expected completion time within tolerance;
- content-family overlap below threshold;
- critical-domain coverage exact;
- reliability/information estimate comparable;
- no compromised item.

## Reproducibility

The system must store the exact delivered item versions and ordering. Randomness alone is not acceptable evidence.
