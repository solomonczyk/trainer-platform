# Dynamic Item Bank Architecture

**Document ID:** CGSF-ITEMBANK-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define the non-static, evolving database for questions, scenarios, families, variants, metrics and exam eligibility.

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

## Core requirement

The item bank is not a fixed JSON file. It is a governed database containing item families, generated variants, calibrated items, lifecycle events and exposure metrics.

## Entity hierarchy

```text
Domain Pack
  -> Competency
  -> Item Specification
  -> Item Family
  -> Item Variant
  -> Item Version
  -> Calibration Record
  -> Exam Eligibility Record
```

## Item record

```json
{
  "item_id": "qa.test_design.boundary.000482",
  "family_id": "qa.test_design.boundary.numeric_range",
  "version": 7,
  "status": "calibrated",
  "competency_ids": ["qa.test_design.boundary_values"],
  "blueprint_node_ids": ["qa.bp.test_design"],
  "knowledge_source_versions": ["qa.core.2026.1"],
  "item_type": "multiple_choice",
  "locale": "en-US",
  "market": "global",
  "difficulty_target": "medium",
  "difficulty_measured": 0.58,
  "discrimination_measured": 0.34,
  "answer_key_version": 3,
  "review_status": "expert_approved",
  "exposure_count": 184,
  "compromise_risk": "low",
  "valid_from": "YYYY-MM-DD",
  "valid_until": null
}
```

## Item family

A family stores the invariant skill and controlled parameters rather than one fixed question.

```json
{
  "family_id": "ba.requirement.classification",
  "invariant_construct": "classify_requirement_type",
  "parameter_schema": {
    "industry": ["banking", "healthcare", "retail", "logistics"],
    "requirement_type": ["functional", "performance", "security", "usability", "regulatory"],
    "ambiguity_level": ["clear", "subtle", "conflicting"]
  },
  "variant_generation_limit": 1000,
  "max_same_family_per_form": 2
}
```

## Bank partitions

- draft pool;
- automated-validation pool;
- expert-review queue;
- pilot pool;
- calibrated practice pool;
- exam-eligible secure pool;
- suspended pool;
- retired archive.

## Database requirements

- immutable version history;
- structured provenance;
- locale and market variants;
- semantic duplicate index;
- exposure and performance counters;
- audit events;
- soft deletion only for scored artifacts;
- deterministic reconstruction of delivered forms.
