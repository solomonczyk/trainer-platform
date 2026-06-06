# Source Content Quality Report — bi-trainer-local

## Audit Date

2026-06-06

## Data Integrity

| Check | Result | Details |
|---|---|---|
| Total questions in JSON | 211 | Verified via node script |
| All questions have explanation | ✅ | 0 missing explanations |
| All closed-form questions have data.correct | ✅ | 0 missing correct answers (textarea and matching excluded by design) |
| Duplicate question IDs | ✅ None | All 211 IDs are unique |
| Question order within modules | ✅ | All have sequential `order` field |
| Module references valid | ✅ | All `moduleId` values match existing modules |
| Level values valid | ✅ | Only `J`, `M`, `S` used |
| Type values valid | ✅ | Only the 7 defined types used |
| Data payloads valid per type | ✅ | radio/checkbox have `options` + `correct`; number has `correct`; fill-blanks has `template` + `blanks` + `correct`; matching has `pairs`; textarea has `keywords` + `minMatch`; flashcard has `{}` |

## Quality Assessment

### Content by Module

| Module | Questions | Quality | Issues |
|---|---|---|---|
| module-1 (HR Screening) | 25 | Good | — |
| module-2 (BA Basics) | 25 | Good | — |
| module-3 (Requirements) | 25 | Good | — |
| module-4 (Documentation) | 25 | Good | — |
| module-5 (Process Modeling) | 20 | Good | — |
| module-6 (Methodologies) | 20 | Good | — |
| module-7 (Metrics) | 20 | Good | — |
| module-8 (Communication) | 20 | Good | — |
| module-9 (Technical) | 25 | Good | — |
| module-10 (Real Cases) | 6 | Sparse | Only 6 questions, should be expanded |

### Content by Difficulty

| Level | Count | % |
|---|---|---|
| Junior (J) | 85 | 40.3% |
| Middle (M) | 84 | 39.8% |
| Senior (S) | 42 | 19.9% |

Well-balanced across Junior and Middle; Senior is underrepresented but acceptable for an interview-focused trainer.

### Content Quality Risks

| Risk | Severity | Description | Recommendation |
|---|---|---|---|
| Module 10 sparse | Low | Only 6 questions for "Real Cases" | Add more case studies after migration |
| Keyword thresholds may vary | Medium | Textarea questions have `minMatch` ranging 1-5. Some thresholds may be too low for meaningful evaluation. | Review during content transformation |
| Senior content limited | Low | Only 42 of 211 questions are Senior level | Supplement with additional Senior-level questions after migration |
| No English localization | Low | All content is in Russian | Add en-US locale after initial migration |
| Diagnostics hardcoded | Medium | 8 diagnostic questions are hardcoded in DiagnosticsPage.tsx, not in questions.json | Extract to content file during migration |
| Large assets | Low | logo.png (1.6 MB) and exam-btn.png (1.3 MB) are unnecessarily large | Compress during migration |
| Dynamic exam selection | Low | Exam picks 25 random questions; no content control for which questions appear | Define exam question pool explicitly |

### Content Ready for Direct Import

**211 out of 211** questions in questions.json are ready for direct import. Data structures are consistent, all required fields are present, and no malformed entries exist.

### Content Requires Transformation

**8 diagnostics questions** currently hardcoded in `DiagnosticsPage.tsx` need to be extracted to a content file.

**25 exam questions** are dynamically selected — the selection algorithm needs to be ported or a fixed exam pool defined.

### Content Requires Human Review

None identified at the data level. Keyword thresholds (`minMatch`) for textarea questions should be reviewed by a domain expert for appropriateness.

### Content Blocked

None.

## Summary

```json
{
  "content_ready_for_direct_import": 211,
  "content_requires_transformation": 33,
  "content_requires_human_review": 0,
  "content_blocked": 0,
  "overall_quality": "GOOD",
  "recommendation": "Content is well-structured and consistent. Proceed with migration."
}
```
