# Versioned Knowledge Source Registry

**Document ID:** CGSF-KNOWLEDGE-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Create a trusted, auditable and continuously updated source-of-truth layer for all simulator content.

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

## Principle

Knowledge changes and item content must evolve. The system must distinguish stable competencies from versioned source knowledge and dynamic item variants.

## Source classes

- official syllabus and exam specifications;
- standards and regulations;
- recognized professional bodies;
- textbooks and expert-authored references;
- product/framework official documentation;
- market or locale-specific practices;
- internally approved expert guidance.

## Source record

```json
{
  "source_id": "istqb.ctfl.syllabus",
  "publisher": "recognized_owner",
  "title": "Foundation-level syllabus",
  "version": "4.x",
  "jurisdiction_or_market": "global",
  "language": "en",
  "source_type": "official_syllabus",
  "trust_level": "authoritative",
  "license_status": "link_and_transform_only",
  "effective_from": "YYYY-MM-DD",
  "effective_to": null,
  "checksum_or_snapshot_ref": "...",
  "reviewed_by": ["domain_expert_id"],
  "status": "active"
}
```

## Update pipeline

1. Trusted source monitoring.
2. Change detection.
3. Human source verification.
4. Structured knowledge diff.
5. Competency impact mapping.
6. Affected item/rubric search.
7. Revision or retirement plan.
8. Revalidation and pilot.
9. New knowledge-bank version.

## Change categories

```json
{
  "editorial": "no scoring impact",
  "clarification": "review affected explanations",
  "substantive": "revalidate items and rubrics",
  "breaking": "new blueprint or domain-pack version"
}
```

## Required controls

- no untrusted web text automatically becomes exam truth;
- every item records source provenance;
- source license/copyright restrictions are recorded;
- superseded sources remain archived;
- affected items are automatically flagged after source changes;
- exam forms cannot mix incompatible knowledge versions unless explicitly approved.
