## Controlled Item Generation Architecture

### Overview

This document describes the architecture of the controlled item generation and automated validation pipeline (Layer 003). The pipeline implements an end-to-end controlled generation flow from authorized request through AI Gateway, validation, and human review handoff.

### Architecture Diagram

```
Authorized Generation Request
  → Generation Policy Gate
    → Source Snapshot Binding
      → Prompt Package Construction
        → AI Gateway
          → Provider Adapter (DeepSeek/Mock)
            → Raw Response Capture
              → Candidate Normalization
                → Schema Validation (V1)
                  → Required Field Validation (V2)
                    → Source Citation Validation (V3)
                      → Competency Alignment (V4)
                        → Difficulty Alignment (V5)
                          → Item Family Compliance (V6)
                            → Answer/Options Consistency (V7)
                              → Rubric Consistency (V8)
                                → Ambiguity Detection (V9)
                                  → Duplicate/Similarity Detection (V10)
                                    → Prohibited Content/Safety (V11)
                                      → Locale Validation (V12)
                                        → Answer Key Leak Detection (V13)
                                          → Provenance Completeness (V14)
                                            → Pool Mutation Guard (V15)
                                              → Decision Aggregation
                                                → Candidate Persistence
                                                  → Provenance Record
                                                    → Audit Record
                                                      → Human Review Queue
```

### Key Components

| Component | Location | Description |
|-----------|----------|-------------|
| GenerationRequest | cert_generation_requests | Authoritative generation request with lifecycle tracking |
| GenerationService | services/generation_service.py | Orchestrates the full pipeline |
| ValidationOrchestrator | services/generation_validation_service.py | Runs 15 independent validators |
| PromptPackage | services/prompt_package.py | Versioned prompt construction |
| GenerationAuditService | services/generation_audit_service.py | Append-only audit trail |

### Forbidden Flows

- LLM → exam item (BLOCKED)
- LLM → pilot pool (BLOCKED)
- LLM → exam_eligible (BLOCKED)
- LLM → automatic publication (BLOCKED)
- Generated candidate → exam assembly (BLOCKED)
- Author → self-review → approved (BLOCKED)
- Provider response → database without schema validation (BLOCKED)
- Failed validation → silent retry (BLOCKED)

### RBAC Matrix

| Action | Allowed Roles |
|--------|---------------|
| Create generation request | platform_admin, generation_operator, domain_owner |
| Authorize generation | platform_admin, generation_operator (not self) |
| Execute generation | platform_admin, generation_operator |
| View raw provider output | platform_admin, generation_operator, qa_reviewer |
| View answer key | platform_admin, generation_operator |
| Accept/publish generated item | FORBIDDEN in this layer |
