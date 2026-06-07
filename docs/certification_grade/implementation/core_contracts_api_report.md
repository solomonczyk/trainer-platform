# Core Contracts API Report

**Document ID:** CGSF-IMPL-API-001  
**Date:** 2026-06-07  

## Registered Routes

All routes are registered under `/api/v1` namespace with `Certification-Core` tag.

### Domain Packs
| Method | Path | Description |
|--------|------|-------------|
| GET | `/certification-core/domain-packs` | List domain packs (paginated, filterable) |
| GET | `/certification-core/domain-packs/{domain_pack_id}` | Get domain pack by ID |
| POST | `/certification-core/domain-packs` | Create domain pack |
| PATCH | `/certification-core/domain-packs/{domain_pack_id}` | Update domain pack |

### Competency Frameworks
| Method | Path | Description |
|--------|------|-------------|
| GET | `/certification-core/competency-frameworks` | List frameworks (paginated, filterable) |
| GET | `/certification-core/competency-frameworks/{framework_id}` | Get framework with competencies |
| POST | `/certification-core/competency-frameworks` | Create framework with competencies |
| PATCH | `/certification-core/competency-frameworks/{framework_id}` | Update framework |
| POST | `/certification-core/competency-frameworks/{framework_id}/competencies` | Add competency |

### Exam Blueprints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/certification-core/blueprints` | List blueprints (paginated, filterable) |
| GET | `/certification-core/blueprints/{blueprint_id}` | Get blueprint with sections |
| POST | `/certification-core/blueprints` | Create blueprint with sections |
| PATCH | `/certification-core/blueprints/{blueprint_id}` | Update blueprint |

### Knowledge Sources
| Method | Path | Description |
|--------|------|-------------|
| GET | `/certification-core/knowledge-sources` | List sources (paginated, filterable) |
| GET | `/certification-core/knowledge-sources/{source_id}` | Get source by ID |
| POST | `/certification-core/knowledge-sources` | Create source |
| PATCH | `/certification-core/knowledge-sources/{source_id}` | Update source |

### Item Families
| Method | Path | Description |
|--------|------|-------------|
| GET | `/certification-core/item-families` | List families (paginated, filterable) |
| GET | `/certification-core/item-families/{family_id}` | Get family by ID |
| POST | `/certification-core/item-families` | Create family |
| PATCH | `/certification-core/item-families/{family_id}` | Update family |

### Items
| Method | Path | Description |
|--------|------|-------------|
| GET | `/certification-core/items` | List items (paginated, filterable, answer-key-protected) |
| GET | `/certification-core/items/{item_id}` | Get item (answer-key-protected for learners) |
| POST | `/certification-core/items` | Create item with version snapshot |
| PATCH | `/certification-core/items/{item_id}` | Update item |

### Item Lifecycle Transitions
| Method | Path | Description |
|--------|------|-------------|
| POST | `/certification-core/items/{item_id}/transitions` | Execute lifecycle transition |

### Rubrics
| Method | Path | Description |
|--------|------|-------------|
| GET | `/certification-core/rubrics` | List rubrics (paginated, filterable) |
| GET | `/certification-core/rubrics/{rubric_id}` | Get rubric with criteria |
| POST | `/certification-core/rubrics` | Create rubric with criteria |
| PATCH | `/certification-core/rubrics/{rubric_id}` | Update rubric |

### Audit
| Method | Path | Description |
|--------|------|-------------|
| GET | `/certification-core/audit` | Query audit events (filterable, paginated) |

## Route Count: 26 endpoints

## Role-Based Access Control

| Role | Read | Write | Lifecycle | Audit | Answer Keys |
|------|------|-------|-----------|-------|-------------|
| platform_admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| domain_owner | ✅ | ✅ | ✅ | ✅ | ✅ |
| content_author | ✅ | ✅ | ❌ | ❌ | ❌ |
| expert_reviewer | ✅ | ❌ | ✅ | ✅ | ❌ |
| psychometric_reviewer | ✅ | ❌ | ✅ | ✅ | ❌ |
| qa_reviewer | ✅ | ❌ | ❌ | ✅ | ❌ |
| read_only_auditor | ✅ | ❌ | ❌ | ✅ | ❌ |
| guest (learner) | partial | ❌ | ❌ | ❌ | ❌ |

## Answer Key Protection
- Items returned to learner/guest roles have `answer_key` field stripped
- Restricted roles: `read_only_auditor`, `qa_reviewer`, `guest`
- Protection enforced at the API endpoint layer via `_filter_item_response()`
