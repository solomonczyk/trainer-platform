# Competency Model and Exam Blueprint Framework

**Document ID:** CGSF-BLUEPRINT-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define the stable structure that controls what is assessed, at what cognitive level, with what weight and criticality.

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

## Separation of concerns

- **Competency model:** what a capable professional must know and do.
- **Learning objective:** observable outcome expected from the learner.
- **Exam blueprint:** how the assessment samples competencies.
- **Item specification:** constraints for an individual item family.

## Competency schema

```json
{
  "competency_id": "ba.requirements.ambiguity_detection",
  "domain": "business_analysis",
  "name": "Detect ambiguity in requirements",
  "description": "Identify vague, conflicting or untestable requirements",
  "cognitive_levels": ["understand", "apply", "analyze"],
  "criticality": "high",
  "prerequisites": ["ba.requirements.types"],
  "evidence_types": ["selected_response", "constructed_response", "scenario"],
  "version": "1.0"
}
```

## Blueprint node schema

```json
{
  "blueprint_node_id": "ba.bp.requirements_analysis",
  "competency_ids": ["ba.requirements.ambiguity_detection"],
  "weight_percent": 20,
  "minimum_items": 6,
  "maximum_items": 10,
  "difficulty_distribution": {"easy": 0.2, "medium": 0.5, "hard": 0.3},
  "cognitive_distribution": {"remember": 0.1, "understand": 0.2, "apply": 0.4, "analyze": 0.3},
  "critical_domain": true,
  "minimum_domain_score": 60
}
```

## Blueprint validation rules

- weights total 100%;
- all scored items map to at least one active competency;
- every critical competency is sampled;
- cognitive level is compatible with item type;
- difficulty and time budgets fit the form;
- blueprint changes create a new version;
- old candidate results remain linked to old version.

## Cognitive levels

Use a normalized model compatible with common exam practice:

1. Remember - recall terms and facts.
2. Understand - explain or classify.
3. Apply - use a method in a familiar situation.
4. Analyze - resolve ambiguity, compare evidence, diagnose.
5. Evaluate - justify decisions using constraints.
6. Create - produce a professional artifact.

## Required artifacts per domain

- competency tree;
- prerequisite graph;
- blueprint table;
- item-type mapping;
- critical competency policy;
- exam time budget;
- expert approval record.
