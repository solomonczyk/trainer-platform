# Core Contracts Data Model

**Document ID:** CGSF-IMPL-DATA-001  
**Layer:** TRAINER-PLATFORM-CERTIFICATION-GRADE-CORE-CONTRACTS-VERTICAL-LAYER-001  
**Date:** 2026-06-07  

## Entity-Relationship Overview

```
DomainPack
  ├── competency_framework_id ──► CompetencyFramework
  │                                └── Competency (hierarchical, parent_id)
  ├── blueprint_ids ──► ExamBlueprint
  │                       └── BlueprintSection
  ├── knowledge_source_ids ──► KnowledgeSource
  ├── rubric_ids ──► Rubric
  │                    └── RubricCriterion
  └── ItemFamily
       └── Item
            └── ItemVersion

AuditEvent (standalone, append-only)
```

## Table: `cert_domain_packs`

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| domain_pack_id | String(100) UNIQUE | Business identifier |
| name | String(255) | |
| version | String(20) | With domain_pack_id: UQ |
| locale | String(10) | default en-US |
| market | String(50) | default global |
| status | String(20) | draft|active|deprecated|retired |
| ...reference_ids | String/JSON | competency_framework, blueprints, knowledge sources, rubrics |
| supported_modes | JSON | learning|practice|exam_simulation |

## Table: `cert_competency_frameworks`

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| framework_id | String(100) UNIQUE | Business identifier |
| domain_pack_id | String(100) | Optional reference |
| version | String(20) | With framework_id: UQ |
| status | String(20) | draft|active|deprecated|retired |
| locale, market | String | Localization binding |
| valid_from/until | DateTime | Temporal validity |

## Table: `cert_competencies`

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| competency_id | String(100) | With framework_id: UQ |
| framework_id | FK → cert_competency_frameworks | |
| parent_id | FK → self (nullable) | Hierarchy support |
| critical | Boolean | Critical competency flag |
| weight | Float | Relative importance |
| cognitive_levels | JSON | Array of cognitive level strings |

## Table: `cert_exam_blueprints`

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| blueprint_id | String(100) UNIQUE | |
| competency_framework_version | String(100) | |
| version | String(20) | With blueprint_id: UQ |
| exam_duration_minutes | Integer | |
| total_items | Integer | |
| pass_policy_id | String(100) | |

## Table: `cert_blueprint_sections`

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| blueprint_id | FK → cert_exam_blueprints | |
| section_id | String(100) | With blueprint_id: UQ |
| weight_percent | Float | Sum across sections = 100 |
| min/max_items | Integer | |
| difficulty/cognitive_distribution | JSON | Distributions |
| critical_section | Boolean | |

## Table: `cert_knowledge_sources`

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| source_id | String(100) UNIQUE | |
| source_type | String(50) | standard|syllabus|law|book|documentation|policy|dataset |
| version | String(50) | With source_id: UQ |
| content_hash | String(128) | SHA-256 for verification |
| status | String(20) | draft|verified|active|superseded|revoked |
| superseded_by | String(100) | Replacement chain |

## Table: `cert_item_families`

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| family_id | String(100) UNIQUE | |
| template_schema | JSON | Parameterization schema |
| allowed_item_types | JSON | Type constraints |
| variant_policy | JSON | Generation limits |

## Table: `cert_items`

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| item_id | String(100) UNIQUE | |
| item_family_id | FK → cert_item_families | |
| version | Integer | Auto-incrementing |
| item_type | String(50) | Discriminated type |
| prompt | JSON | Structured prompt |
| answer_key | JSON | Protected from learners |
| competency_ids | JSON | M×N competency mapping |
| knowledge_source_refs | JSON | Provenance |
| status | String(30) | Lifecycle state (14 states) |

## Table: `cert_item_versions`

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| item_id | FK → cert_items | |
| version | Integer | With item_id: UQ |
| snapshot | JSON | Immutable version copy |
| change_reason | String(500) | |

## Table: `cert_rubrics`

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| rubric_id | String(100) UNIQUE | |
| version | String(20) | With rubric_id: UQ |
| total_weight | Float | Sum of criteria weights = 100 |
| validation_dataset_ref | String(100) | |

## Table: `cert_rubric_criteria`

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| rubric_id | FK → cert_rubrics | |
| criterion_id | String(100) | With rubric_id: UQ |
| weight | Float | |
| levels | JSON | Scoring level definitions |

## Table: `cert_audit_events`

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| audit_event_id | String(100) UNIQUE | |
| entity_type | String(50) | Indexed |
| entity_id | String(100) | Indexed |
| entity_version | String(20) | |
| action | String(50) | create|update|transition|delete |
| actor_id | String(100) | |
| before_hash / after_hash | String(128) | SHA-256 |

## Key Constraints

- All versioned entities enforce `(business_id, version)` unique constraints
- No hard delete of referenced items (soft retirement via status + valid_until)
- Foreign keys maintain referential integrity for core relationships
- Indexes on status, domain_pack_id, entity_type for query performance
