# Migration Plan for Existing BA and QA Trainers

**Document ID:** CGSF-MIGRATION-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Evolve current accepted trainers into the new framework without discarding working vertical slices or falsely claiming calibration.

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

## Current state

BA Trainer Phase 1 is `REAL_STAGING_ACCEPTED` as a working deterministic vertical slice. QA Trainer has real DeepSeek evaluation with validated schema. These are implementation assets, not yet full certification-grade domain packs.

## Migration stages

### Stage A - Classification

Map every existing activity/scenario to:

- competency;
- blueprint node;
- cognitive level;
- item family/type;
- source version;
- current quality level L0-L2.

### Stage B - Registry migration

Move content from static package-only representation into versioned knowledge, item-family and item-version records while preserving existing APIs through adapters.

### Stage C - Quality enrichment

Add:

- provenance;
- independent answer verification;
- expert review state;
- exposure tracking;
- item metrics;
- rubric anchors.

### Stage D - Pilot and calibration

Use existing users/synthetic cohorts to collect pilot evidence. Do not relabel items as calibrated before sufficient data.

### Stage E - Exam mode

Build blueprint-constrained equivalent forms, secure timer/session runtime and readiness reports.

## Compatibility rules

- existing progress is preserved;
- accepted Phase 1 flows remain operational;
- old item IDs map to migrated versions;
- score meaning changes create explicit policy version;
- no silent conversion of unvalidated items to exam-eligible.
