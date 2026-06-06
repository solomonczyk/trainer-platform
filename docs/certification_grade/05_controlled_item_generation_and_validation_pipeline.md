# Controlled Item Generation and Validation Pipeline

**Document ID:** CGSF-GENERATION-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Specify how human-authored, template-generated and LLM-generated items are created without unsafe direct delivery.

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

## Forbidden pattern

```text
LLM generates item at exam runtime -> candidate sees item
```

This is forbidden for exam mode because quality, answer correctness, difficulty and fairness are not validated.

## Approved pipeline

```text
Item specification
-> Template/LLM generation
-> Schema validation
-> Source-grounding validation
-> Answer-key verification
-> Distractor quality check
-> Ambiguity and multi-answer check
-> Duplicate/similarity check
-> Bias/accessibility check
-> Difficulty prediction
-> Expert review
-> Pilot delivery
-> Psychometric calibration
-> Exam eligibility
```

## Generation methods

```json
{
  "human_authored": "expert creates full item",
  "template_generated": "validated parameterized family",
  "llm_assisted": "LLM drafts, human/system validates",
  "data_generated": "deterministic generation from datasets"
}
```

## Automated validation gates

- JSON/schema correctness;
- required metadata completeness;
- source references resolve;
- answer key can be independently derived;
- no answer leakage;
- distractors are plausible but incorrect;
- no prohibited or copyrighted reproduction;
- no semantic duplicate above threshold;
- reading level and language are appropriate;
- target cognitive level is plausible;
- estimated completion time is within specification.

## Required decision record

```json
{
  "item_id": "...",
  "generation_method": "llm_assisted",
  "generator_model": "...",
  "source_grounded": true,
  "automated_checks": "passed",
  "expert_decision": "approved_for_pilot",
  "exam_eligible": false
}
```

## Blind regeneration rule

Blind retry is prohibited. A failed item must record a failure category and corrective instruction before regeneration.
