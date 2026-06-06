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
