# Domain Pack Specification

**Document ID:** CGSF-DOMAINPACK-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Provide a repeatable package contract for expanding the platform to any profession, language or examination domain.

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

## Domain pack contents

```text
manifest.json
competency_model/
exam_blueprints/
knowledge_sources/
item_specifications/
item_families/
scenario_bank/
rubrics/
anchor_responses/
scoring_policies/
locales/
validation_sets/
expert_approvals/
release_evidence/
```

## Manifest

```json
{
  "domain_pack_id": "software_testing_foundation",
  "display_name": "Software Testing Foundation Simulator",
  "version": "1.0.0",
  "markets": ["global"],
  "locales": ["en-US", "ru-RU"],
  "target_quality_level": "L3",
  "blueprint_versions": ["1.0"],
  "knowledge_bank_version": "2026.1",
  "minimum_bank_requirements": {
    "practice_items": 300,
    "exam_eligible_items": 400,
    "equivalent_forms": 10
  }
}
```

## Required domain-pack gates

- content provenance complete;
- competency/blueprint approved;
- item bank reaches required diversity;
- calibration evidence sufficient for claimed level;
- locale adaptation reviewed beyond literal translation;
- browser and API acceptance complete;
- security/privacy reviewed;
- marketing claims match evidence.

## Market adaptation

A locale pack may alter language, examples, legal context and professional conventions, but cannot silently change measured competency or score meaning. Material changes require a market-specific blueprint or scoring version.
