# Core Contracts Implementation Decision

**Document ID:** CGSF-IMPL-DECISION-001  
**Layer:** TRAINER-PLATFORM-CERTIFICATION-GRADE-CORE-CONTRACTS-VERTICAL-LAYER-001  
**Date:** 2026-06-07  
**Status:** APPROVED  

## Documents Reviewed

| # | Document | Reviewed |
|---|---|---|
| 00 | Master Index | ✅ |
| 01 | Product Vision & Quality Standard | ✅ |
| 02 | Competency & Exam Blueprint Framework | ✅ |
| 03 | Versioned Knowledge Source Registry | ✅ |
| 04 | Dynamic Item Bank Architecture | ✅ |
| 05 | Controlled Item Generation & Validation Pipeline | ✅ |
| 06 | Item Lifecycle & Governance | ✅ |
| 07 | Rotation, Exposure & Compromise Control | ✅ (deferred) |
| 08 | Exam Form Assembly & Equivalence | ✅ (deferred) |
| 09 | Scoring, Standard Setting & Pass Policy | ✅ (deferred) |
| 10 | Psychometric Calibration & Reliability | ✅ (deferred) |
| 11 | Rubric, AI & Human Evaluator Calibration | ✅ |
| 12 | Adaptive Learning & Readiness Prediction | ✅ (deferred) |
| 13 | Exam Session Integrity & Runtime | ✅ (deferred) |
| 14 | Data Model & API Contracts | ✅ |
| 15 | Analytics, Effectiveness & Evidence | ✅ (deferred) |
| 16 | Human Expert Governance & Roles | ✅ |
| 17 | Domain Pack Specification | ✅ |
| 18 | Quality Assurance & Validation Strategy | ✅ (deferred) |
| 19 | Security, Privacy, Copyright & Legal Boundaries | ✅ (deferred) |
| 20 | BA/QA Migration Plan | ✅ |
| 21 | Implementation Roadmap | ✅ |
| 22 | Acceptance Gates & Proof Contract | ✅ |

## Scope Decision

### Contracts Selected for This Layer

1. **Competency Model Contract** — hierarchical competency framework with versioning, status lifecycle, locale/market binding
2. **Exam Blueprint Contract** — section-based blueprint with weight validation, difficulty distributions, critical sections
3. **Versioned Knowledge Source Registry** — trusted source tracking with content hashes, validity dates, replacement relationships
4. **Dynamic Item Bank Foundation** — item entities, families, versioning, typed schemas, competency/source mapping
5. **Item Family Contract** — template schemas, variant policies, allowed types
6. **Item Lifecycle State Machine** — 12-state lifecycle with explicit allowed/forbidden transitions, role-based gates
7. **Rubric Versioning Contract** — versioned rubrics with weighted criteria, scoring levels, validation constraints
8. **Domain Pack Contract** — reusable domain pack definition tying all entities together
9. **Audit History** — append-only audit trail for all certification-core mutations
10. **BA/QA Migration Readiness Adapter** — mapping layer to assess current trainer readiness

### Dependencies

- Existing `app/db/models.py` for User, Domain, TrainerProduct references
- Existing `app/core/security.py` for JWT auth patterns
- Existing `app/db/base.py` for Base and TimestampMixin
- Existing `app/modules/auth/` for user authentication
- SQLAlchemy async session via `app/db/session.py`

### Deferred Components

- **Item generation pipeline** (doc 05) — will be implemented in next vertical layer
- **Rotation/exposure controls** (doc 07) — requires item bank runtime
- **Exam form assembly** (doc 08) — requires calibrated items
- **Scoring and standard setting** (doc 09) — requires exam form delivery
- **Psychometric calibration** (doc 10) — requires pilot data collection
- **Adaptive learning** (doc 12) — requires calibration and readiness data
- **Exam session runtime** (doc 13) — requires assembled forms
- **Analytics** (doc 15) — requires runtime data
- **Automatic LLM item generation** — explicitly out of scope per task definition
- **Production authoring UI** — out of scope
- **Mass content migration** — out of scope; only readiness adapter created

### Conflicts and Ambiguities Found

1. **Cognitive levels**: Doc 02 defines 6 levels (Remember through Create). Doc 14 implicitly uses fewer. We implement the full 6-level model from doc 02.
2. **Item status**: Doc 06 includes "automated_validation_failed" state not listed in the task body. We include it in the full state machine for completeness.
3. **Role naming**: Doc 16 uses "Assessment Architect" while task body uses "domain_owner". We map task body roles to doc 16 concepts via RBAC configuration.
4. **Locale vs Market**: Some docs use "language" and "jurisdiction_or_market" separately, others conflate. We keep both `locale` and `market` as distinct fields.

## Mapping: Documents to Implementation Modules

| Document | Implementation Module |
|---|---|
| 02 — Competency & Blueprint | `certification_core/models/competency_models.py`, `certification_core/models/blueprint_models.py` |
| 03 — Knowledge Registry | `certification_core/models/knowledge_source_models.py` |
| 04 — Dynamic Item Bank | `certification_core/models/item_models.py`, `certification_core/models/item_family_models.py` |
| 06 — Item Lifecycle | `certification_core/state_machine/item_lifecycle.py` |
| 11 — Rubric Calibration | `certification_core/models/rubric_models.py` |
| 14 — Data & API | `certification_core/schemas/*.py`, `certification_core/routers/*.py` |
| 16 — Governance | `certification_core/services/authorization.py` |
| 17 — Domain Pack | `certification_core/models/domain_pack_models.py` |
| 20 — Migration | `certification_core/migration_adapters/ba_qa_adapter.py` |

## Out-of-Scope Components

- Item generation (LLM or template)
- Psychometric calibration runtime
- Adaptive learning
- Final exam form assembly
- Production authoring UI
- Full migration of BA/QA content
- Mass creation of new trainers
- Browser acceptance tests (no user-facing UI changed)
- DeepSeek provider configuration changes

## Documented Architecture Principles Applied

```json
{
  "static_question_files_as_final_architecture": false,
  "questions_directly_generated_during_exam": false,
  "unreviewed_llm_items_exam_eligible": false,
  "versioned_knowledge_sources_required": true,
  "competency_mapping_required": true,
  "blueprint_mapping_required": true,
  "item_history_required": true,
  "auditability_required": true,
  "hard_delete_of_referenced_items": false,
  "cross_domain_hardcoding": false
}
```
