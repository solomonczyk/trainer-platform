# Certification-Grade Simulation Framework - Complete Documentation Pack

This combined file contains all documents in implementation reading order.



---

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


---

# Product Vision and Certification-Grade Quality Standard

**Document ID:** CGSF-PRODUCT-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Set the product category, quality bar, user promise and boundaries for serious professional and educational exam preparation.

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

## Product definition

Trainer Platform is a universal platform for professional, language and academic simulation. It supports learning, practice and exam simulation for many domains rather than being limited to Business Analysis or Software Testing.

## User promise

A user completing a simulator must receive:

- a realistic representation of target competencies;
- difficulty comparable to the target examination or professional assessment;
- controlled timing and exam conditions;
- detailed diagnostic feedback;
- evidence-based readiness estimation;
- targeted remediation for weak areas;
- repeated practice without simple answer memorization.

## Three mandatory modes

### Learning mode

- explanations and examples;
- hints and guided correction;
- unlimited or policy-controlled attempts;
- direct links to competencies and learning objectives.

### Practice mode

- topic and difficulty selection;
- adaptive item selection;
- controlled hints;
- spaced repetition;
- detailed post-item feedback.

### Exam simulation mode

- blueprint-constrained form;
- strict timer;
- no hints or answer reveal before completion;
- controlled navigation and interruption recovery;
- exposure-limited item selection;
- result, domain profile and confidence interval after submission.

## Certification-grade quality dimensions

| Dimension | Required evidence |
|---|---|
| Content validity | Expert mapping to syllabus/competencies |
| Construct validity | Items test intended skill, not irrelevant ability |
| Reliability | Repeatable scores and acceptable measurement error |
| Difficulty | Measured, not only author-labelled |
| Fairness | Bias and accessibility review |
| Security | Exposure, leakage and compromise controls |
| Reproducibility | Versioned forms, keys, rubrics and runtime |
| Effectiveness | Demonstrated learning gain/readiness relationship |

## Product boundaries

The platform may provide preparation, mock exams and internal readiness credentials. It must not claim to issue an official ISTQB, IELTS or other third-party certificate without a formal authorization agreement.

## Quality levels

```json
{
  "L0": "demo_or_unvalidated_quiz",
  "L1": "learning_activity",
  "L2": "validated_practice_bank",
  "L3": "calibrated_exam_simulator",
  "L4": "certification_grade_readiness_system"
}
```

Only L3-L4 may be marketed as serious exam simulation.

## Release rule

A new simulator cannot be released as certification-grade until all domain-pack, psychometric, security, expert-review and real-browser acceptance gates pass.


---

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


---

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


---

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


---

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


---

# Item Lifecycle and Governance

**Document ID:** CGSF-LIFECYCLE-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define item states, transitions, ownership and evidence required from creation through retirement.

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

## Canonical states

```json
[
  "draft",
  "generated",
  "automated_validation_failed",
  "automated_validation_passed",
  "expert_review_required",
  "approved_for_pilot",
  "pilot",
  "calibration_review",
  "calibrated",
  "exam_eligible",
  "under_review",
  "suspended",
  "retired",
  "archived"
]
```

## Transition controls

| Transition | Required authority |
|---|---|
| generated -> automated_validation_passed | validation service |
| automated_validation_passed -> approved_for_pilot | domain expert |
| pilot -> calibrated | psychometric reviewer |
| calibrated -> exam_eligible | assessment owner + domain expert |
| exam_eligible -> suspended | automated risk rule or authorized reviewer |
| suspended -> exam_eligible | full corrective review |
| any active -> retired | content governance decision |

## Suspension triggers

- suspected answer leakage;
- abnormal response statistics;
- multiple credible ambiguity complaints;
- source knowledge changed;
- bias/fairness concern;
- answer key defect;
- excessive exposure;
- legal/copyright issue.

## Audit event

```json
{
  "event_id": "...",
  "item_id": "...",
  "from_status": "exam_eligible",
  "to_status": "suspended",
  "reason_code": "possible_compromise",
  "actor_type": "automated_rule",
  "evidence_refs": ["..."],
  "timestamp": "..."
}
```

## Governance rule

No LLM, author or single engineer may self-approve an item through every stage.


---

# Rotation, Exposure and Compromise Control

**Document ID:** CGSF-ROTATION-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Prevent memorization, overexposure, repeated forms and compromised questions while preserving comparability.

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

## Objectives

- reduce repeat exposure to the same candidate;
- control global exposure;
- rotate item families and contexts;
- detect leaked or compromised items;
- maintain blueprint and difficulty equivalence.

## Selection constraints

```json
{
  "same_user_repeat_cooldown_days": 90,
  "recent_item_window": 200,
  "max_same_family_per_form": 2,
  "max_form_overlap_percent": 25,
  "max_item_exposure_rate": 0.20,
  "exclude_suspected_compromised": true,
  "reserve_unscored_pilot_slots": 5
}
```

## Exposure metrics

- total deliveries;
- unique candidates;
- exposure rate by form/window;
- repeated exposure per candidate;
- family exposure;
- answer-pattern anomaly;
- external leak signal;
- performance shift after suspected publication.

## Rotation strategy

1. Select eligible items by blueprint node.
2. Exclude recent candidate history.
3. Exclude exposure-limit violations.
4. Balance item families.
5. Match target difficulty and time.
6. reserve pilot items where allowed.
7. record exact selection decision.

## Compromise response

```text
Detect signal -> suspend item -> invalidate future forms -> investigate
-> replace with equivalent item -> measure score impact -> document decision
```

Past candidate scores are not automatically invalidated. Impact analysis and governance decision are required.


---

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


---

# Scoring, Standard Setting and Pass Policy

**Document ID:** CGSF-SCORING-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define defensible scoring, domain minimums, pass thresholds, partial credit and versioned policies.

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

## Scoring principles

- scoring logic is versioned;
- score calculation is deterministic after validated evaluation;
- item weights are blueprint-governed;
- open-response scores use approved rubrics;
- critical-domain failures may override overall score;
- pass thresholds are not arbitrary UI constants.

## Scoring policy

```json
{
  "policy_id": "ba.score.1.0",
  "scale": {"min": 0, "max": 100},
  "pass_score": 70,
  "critical_domain_minimums": {"requirements_analysis": 60},
  "negative_marking": false,
  "partial_credit": true,
  "rounding_rule": "half_up_one_decimal",
  "unscored_pilot_items_excluded": true
}
```

## Standard-setting options

- modified Angoff expert judgment;
- bookmark method;
- contrasting groups after pilot data;
- external target-exam pass standard where legally and methodologically appropriate.

## Required process

1. Define minimally competent candidate.
2. Expert panel estimates item success probability.
3. Aggregate and discuss variance.
4. Pilot against real candidate data.
5. Adjust with documented evidence.
6. Approve threshold and confidence interval.

## Score report

Must include:

- total score;
- pass/fail under policy version;
- domain scores;
- critical-domain status;
- confidence interval or measurement error;
- readiness interpretation;
- limitations and recommended remediation.


---

# Psychometric Calibration and Reliability

**Document ID:** CGSF-PSYCH-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Measure item difficulty, discrimination, reliability, fairness and equivalence instead of relying on author opinion.

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

## Minimum classical test theory metrics

```json
{
  "p_value_difficulty": 0.58,
  "discrimination_index": 0.34,
  "point_biserial": 0.31,
  "median_response_time_seconds": 72,
  "omit_rate": 0.03,
  "sample_size": 850
}
```

## Exam metrics

- Cronbach alpha or suitable reliability estimate;
- standard error of measurement;
- domain score reliability;
- form difficulty comparison;
- score distribution and floor/ceiling effects;
- decision consistency around pass score.

## Calibration phases

1. Expert difficulty prediction.
2. Unscored or low-stakes pilot.
3. Initial statistics.
4. Item review and correction.
5. Calibrated practice eligibility.
6. Exam eligibility after minimum evidence.
7. Continuous monitoring.

## Sample-size policy

Exact thresholds are domain-dependent. Until adequate data exists, the item remains provisional and must not be represented as fully calibrated.

## IRT roadmap

Later phases may implement 1PL/2PL/3PL or graded response models for:

- ability estimation;
- adaptive testing;
- form linking;
- item information;
- more precise readiness confidence.

## Automatic flags

- too easy or too hard;
- negative discrimination;
- time anomaly;
- option never selected;
- sudden performance shift;
- subgroup differential item functioning;
- excessive missing response.


---

# Rubric, AI and Human Evaluator Calibration

**Document ID:** CGSF-RUBRIC-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Make open-response scoring reliable through explicit rubrics, anchor responses, human calibration and monitored AI agreement.

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

The LLM is an evaluator runtime, not the source of truth. Quality comes from rubric design, anchor examples, schema validation and agreement studies.

## Rubric structure

```json
{
  "rubric_id": "ba.user_story.1.0",
  "criteria": [
    {
      "criterion_id": "clarity",
      "weight": 0.20,
      "levels": {
        "0": "unusable or absent",
        "1": "major ambiguity",
        "2": "mostly understandable with gaps",
        "3": "clear and testable",
        "4": "precise, risk-aware and complete"
      }
    }
  ],
  "critical_errors": ["invented stakeholder approval", "untestable acceptance condition"]
}
```

## Anchor set

Every rubric requires:

- multiple weak responses;
- borderline responses;
- passing responses;
- excellent responses;
- expert scores and rationales;
- adversarial/irrelevant responses.

## AI evaluation contract

- provider and model recorded;
- deterministic structured schema;
- criterion scores bounded;
- total score consistent with weights;
- `validation_status=validated` required;
- reasoning content normalized and not exposed as hidden chain-of-thought;
- failure returns safe state, not fabricated score.

## Calibration metrics

- exact agreement rate;
- adjacent agreement rate;
- mean absolute score difference;
- weighted kappa/intraclass correlation where appropriate;
- pass/fail agreement;
- subgroup bias analysis;
- drift over model or prompt versions.

## Human review triggers

- borderline pass score;
- schema repair required;
- low confidence;
- critical error detected;
- AI/human disagreement beyond tolerance;
- candidate appeal;
- new rubric/model version.


---

# Adaptive Learning and Readiness Prediction

**Document ID:** CGSF-ADAPTIVE-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Convert assessment evidence into personalized practice while keeping exam mode secure and interpretable.

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

## Adaptive practice inputs

- competency mastery estimates;
- recent errors;
- item exposure history;
- response time;
- confidence/self-rating where used;
- prerequisite graph;
- forgetting interval;
- target exam date and blueprint.

## Selection policy

Prioritize:

1. critical weak competencies;
2. prerequisites blocking higher skills;
3. items near current ability;
4. spaced repetition due items;
5. under-sampled blueprint nodes;
6. varied item families and contexts.

## Readiness model

```json
{
  "overall_readiness": 0.73,
  "confidence_interval": [0.66, 0.79],
  "estimated_pass_probability": 0.76,
  "critical_domain_risk": ["stakeholder_analysis"],
  "evidence_volume": "moderate",
  "model_version": "readiness-1.0"
}
```

## Communication rules

Never present readiness as certainty. Reports must state evidence limitations, bank calibration status and difference between platform readiness estimate and official examination result.

## Exam-mode separation

Adaptive selection is permitted only if the target exam model supports adaptive testing. Otherwise exam simulation uses fixed blueprint-equivalent forms, while adaptation is limited to practice mode.


---

# Exam Session Integrity and Runtime

**Document ID:** CGSF-SESSION-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define secure, reliable and recoverable exam sessions with strict mode separation.

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

## Exam session states

```json
[
  "created",
  "identity_confirmed",
  "instructions_viewed",
  "started",
  "in_progress",
  "interrupted",
  "resumed",
  "submitted",
  "scoring",
  "scored",
  "invalidated",
  "appeal_pending",
  "closed"
]
```

## Runtime requirements

- server-authoritative timer;
- idempotent answer save;
- autosave and interruption recovery;
- immutable delivered form;
- no answer reveal before completion;
- explicit final submission confirmation;
- duplicate submission prevention;
- audit trail for navigation and state changes;
- controlled accommodation time;
- timezone-independent timestamps.

## Integrity controls by maturity

### Baseline

- authenticated session;
- randomized equivalent form;
- exposure controls;
- browser focus/interruption signals recorded, not automatically punished;
- rate limits and abuse monitoring.

### Advanced optional

- identity verification;
- secure browser;
- proctoring integration;
- plagiarism/similarity analysis;
- organization-specific invigilation.

## Failure handling

A provider or network failure must preserve answers and time policy. Blind re-scoring and duplicate billing are prohibited. Every retry requires idempotency key and reason code.


---

# Core Data Model and API Contracts

**Document ID:** CGSF-DATA-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Translate the framework into implementable database entities, events and service boundaries.

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

## Core entities

- `competency_models`, `competencies`, `competency_edges`;
- `exam_blueprints`, `blueprint_nodes`, `blueprint_versions`;
- `knowledge_sources`, `knowledge_snapshots`, `knowledge_changes`;
- `item_specs`, `item_families`, `items`, `item_versions`;
- `item_reviews`, `item_metrics`, `item_exposure`;
- `rubrics`, `rubric_versions`, `anchor_responses`;
- `exam_forms`, `exam_form_items`, `form_equivalence_reports`;
- `exam_sessions`, `session_responses`, `session_events`;
- `evaluations`, `criterion_scores`, `score_reports`;
- `readiness_estimates`, `learning_recommendations`;
- `governance_decisions`, `audit_events`.

## Service boundaries

```text
Knowledge Registry Service
Item Bank Service
Generation & Validation Service
Blueprint Service
Form Assembly Service
Exam Session Service
Scoring Service
AI Evaluation Gateway
Psychometric Service
Adaptive Learning Service
Analytics & Audit Service
```

## Example API contracts

```text
POST /api/v1/item-families
POST /api/v1/items/generate
POST /api/v1/items/{id}/validate
POST /api/v1/items/{id}/approve-pilot
POST /api/v1/items/{id}/calibration
POST /api/v1/exam-forms/assemble
POST /api/v1/exam-sessions
PUT  /api/v1/exam-sessions/{id}/responses/{item_id}
POST /api/v1/exam-sessions/{id}/submit
GET  /api/v1/score-reports/{id}
```

## Cross-cutting contract requirements

- tenant/user authorization;
- optimistic locking/version checks;
- idempotency keys;
- explicit schema versions;
- audit actor and reason;
- no secrets or raw responses in analytics events;
- immutable links to delivered item/rubric/form versions.


---

# Analytics, Effectiveness and Evidence Model

**Document ID:** CGSF-EVIDENCE-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Measure item quality, learning gain, readiness accuracy and operational health while preserving privacy.

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

## Analytics categories

### Operational

- latency, failure rate, provider cost;
- session abandonment;
- autosave/recovery success;
- browser and API errors.

### Assessment quality

- item difficulty and discrimination;
- reliability and measurement error;
- form equivalence;
- rubric agreement;
- exposure and compromise signals.

### Learning effectiveness

- pre/post score change;
- competency mastery growth;
- retention after delay;
- completion and remediation uptake;
- pass probability calibration.

## Evidence of effectiveness

A simulator may be described as validated only after collecting evidence that:

- domain experts approve content coverage;
- score reliability is acceptable;
- item statistics behave as expected;
- AI scores agree with expert scoring within tolerance;
- readiness predictions are calibrated against later outcomes where available;
- learners demonstrate measurable improvement.

## Privacy-safe event example

```json
{
  "event": "exam_item_answered",
  "item_id": "...",
  "item_version": 7,
  "correct": false,
  "response_time_ms": 64000,
  "competency_ids": ["..."],
  "raw_answer": "FORBIDDEN"
}
```

## Reports

- item health dashboard;
- form equivalence report;
- rubric drift report;
- readiness calibration report;
- domain-pack effectiveness report;
- privacy and retention audit.


---

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


---

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


---

# Quality Assurance and Validation Strategy

**Document ID:** CGSF-QA-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define tests and acceptance evidence for platform runtime, assessment content, psychometrics, AI evaluation and real browser behavior.

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

## Test layers

### Unit and contract tests

- schema and state transitions;
- scoring formulas;
- blueprint validators;
- exposure rules;
- idempotency and authorization;
- analytics privacy filters.

### Content validation

- answer-key correctness;
- ambiguity and duplicate checks;
- source provenance;
- rubric consistency;
- locale review.

### Integration tests

- item generation to review queue;
- form assembly to session delivery;
- session submission to scoring;
- AI evaluation to progress;
- source update to affected-item flags.

### E2E/browser acceptance

- learning, practice and exam modes;
- timers and recovery;
- refresh/relogin persistence;
- user isolation;
- no localhost/critical errors;
- visible, readable and usable result reports.

### Statistical validation

- item metrics;
- reliability;
- form equivalence;
- evaluator agreement;
- readiness calibration.

## Required visual review

Technical success cannot override broken presentation. Operator visual review is mandatory for exam instructions, item rendering, timers, answer controls, feedback and score reports.

## Acceptance verdicts

- `ACCEPTED`: all hard gates and evidence pass.
- `ACCEPTED_WITH_BLOCKERS`: implementation exists but high-impact evidence is incomplete.
- `REJECTED`: security, isolation, scoring integrity or fabricated evidence failure.
- `NEEDS_OPERATOR_ACTION`: explicit external/manual gate required.

## Regression baseline

Every new domain pack must preserve existing accepted BA Trainer and QA Trainer vertical slices until a planned migration supersedes them.


---

# Security, Privacy, Copyright and Legal Boundaries

**Document ID:** CGSF-LEGAL-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Set minimum controls for candidate data, item security, source usage, AI processing and product claims.

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

## Security domains

- secrets management;
- access control and tenant isolation;
- secure item-bank partitions;
- audit logs;
- abuse/rate limits;
- encrypted transport and protected storage;
- backup and disaster recovery;
- secure export and evidence handling.

## Privacy principles

- collect minimum candidate data;
- define retention by data category;
- separate raw responses from analytics;
- support deletion/export where applicable;
- document AI provider processing;
- avoid sensitive data in prompts unless explicitly required and governed.

## Item security

Exam-eligible items require stricter access than learning items. Authors, reviewers, operators and support staff receive least-privilege access. Item exports are logged and watermarked where appropriate.

## Copyright

- do not copy proprietary exam questions;
- use official syllabi/specifications as mapping sources within license terms;
- create original item families and scenarios;
- record source license and transformation rights;
- remove/suspend content with unresolved rights.

## Claims policy

Allowed examples:

- "preparation simulator";
- "mock exam aligned to documented competencies";
- "readiness estimate based on platform evidence".

Forbidden without authorization/evidence:

- "official ISTQB/IELTS exam";
- "guaranteed pass";
- "official certificate";
- unsupported accuracy or validity claims.


---

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


---

# Implementation Roadmap and Dependencies

**Document ID:** CGSF-ROADMAP-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Sequence development into production-moving vertical layers while avoiding isolated documentation or validator micro-tasks.

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

## Recommended build order

### Layer 1 - Certification-Grade Core Contracts

Deliver:

- competency/blueprint schemas;
- knowledge registry;
- item bank entities and lifecycle;
- governance/audit model;
- API contracts;
- migration adapters.

No exam generation yet.

### Layer 2 - Dynamic Item Factory Vertical Slice

One complete flow:

```text
item specification -> controlled generation -> automated validation
-> expert review queue -> pilot eligibility -> artifacts/tests/browser/admin UI
```

### Layer 3 - Pilot and Psychometric Vertical Slice

Deliver pilot assignment, response metrics, calibration calculations, item health UI and controlled promotion to calibrated state.

### Layer 4 - Exam Form and Session Vertical Slice

Deliver constrained form assembly, exposure controls, strict exam session, scoring and auditable report.

### Layer 5 - Adaptive Practice and Readiness

Deliver mastery estimation, personalized practice and readiness report with uncertainty.

### Layer 6 - First Certification-Grade Domain Pack

Upgrade one domain (recommended software testing foundation or BA foundation) to L3 with expert and pilot evidence.

## Dependency graph

```text
Blueprint + Knowledge Registry
    -> Dynamic Item Bank
        -> Generation/Validation
            -> Pilot/Calibration
                -> Exam Form Assembly
                    -> Exam Session/Scoring
                        -> Readiness/Effectiveness
```

## Phase control

Do not launch many new trainers before core framework and one L3 reference domain pack are proven. Expansion without standards would multiply low-quality static content.

## Current BA Phase 2 note

The previously planned BA Phase 2 must be reconciled with this framework. Scenario functionality can proceed only if its artifacts are created under competency, provenance, rubric and lifecycle contracts rather than as another isolated static bank.


---

# Acceptance Gates and Proof Contract

**Document ID:** CGSF-ACCEPTANCE-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define the mandatory Definition of Done, evidence artifacts and proof JSON for future implementation tasks.

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

## Global Definition of Done

A full vertical layer is complete only when it includes:

- implementation;
- database migrations/contracts;
- runtime and UI;
- security and privacy controls;
- tests;
- real browser acceptance where user-facing;
- operator visual review;
- documentation and artifacts;
- proof JSON;
- commit, push and clean git.

## Hard gates

```json
{
  "generation_gate": "separate_authorization_or_approved_pipeline",
  "expert_review_gate": "required_before_pilot",
  "pilot_gate": "required_before_calibrated",
  "calibration_gate": "required_before_exam_eligible",
  "exam_assembly_gate": "only_exam_eligible_items",
  "release_gate": "quality_security_browser_and_evidence_pass",
  "production_accepted_true": "separate_operator_decision"
}
```

## Minimum proof JSON

```json
{
  "layer": "",
  "verdict": "TBD",
  "goal": "",
  "allowed_scope_respected": false,
  "forbidden_actions_absent": false,
  "implementation": {},
  "data_migrations": {},
  "tests": {},
  "browser_acceptance": {},
  "visual_review": {},
  "security_privacy": {},
  "artifacts": [],
  "git": {"commit": "", "pushed": false, "clean": false},
  "production_accepted": false,
  "release_allowed": false,
  "next_allowed_action": ""
}
```

## Certification-grade domain release gates

- approved competency model and blueprint;
- active trusted source registry;
- required item-bank volume and diversity;
- item provenance completeness;
- expert review and pilot evidence;
- psychometric reliability target met;
- equivalent exam forms verified;
- scoring/pass policy approved;
- AI/human calibration passed for open responses;
- exposure and compromise controls active;
- accessibility, bias, privacy and security reviews passed;
- real browser acceptance passed;
- effectiveness claims limited to available evidence.

## Forbidden acceptance shortcuts

- accepting author-labelled difficulty as calibration;
- accepting a real AI response with `validation_status=partial`;
- accepting API-only tests for a browser workflow;
- marking an item exam-eligible directly after generation;
- using static questions indefinitely without rotation/exposure controls;
- claiming serious exam readiness without uncertainty and evidence;
- claiming `production_accepted=true` inside an implementation task.
