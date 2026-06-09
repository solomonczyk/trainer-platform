# 008 — React Error #31 Root Cause Analysis

## Error Signature

```
Minified React error #31
object with keys {skill_id, weight}
```

React error #31 = "Objects are not valid as a React child".

## Root Cause

The `ScenarioDetail.target_skills` field is typed as `Array<string | { skill_id: string; weight: number }>`.
When the backend returns skill objects (not plain strings), and any code path attempts
to render these objects directly as React child nodes, React throws #31.

### Affected Scenario

When viewing a QA scenario at `/scenarios/qa_test_case_vs_checklist_v1`, the component
receives `target_skills`:

```json
[
  {"skill_id": "test_design", "weight": 50},
  {"skill_id": "qa_process_knowledge", "weight": 50}
]
```

### Root Cause Chain

1. Backend produces `ScenarioDetailResponse` with `target_skills: list[Any]`
2. Pydantic `Any` type passes through whatever JSON is in the database column
3. QA scenario JSON stores `target_skills` as array of `{skill_id, weight}` objects
4. Frontend code uses string type-guard to extract `skill_id` safely
5. If any code path skips the type guard and renders the object directly → React #31

### Secondary Contributing Factor

The `title_key` and `goal_key` fields were missing from QA scenario JSON files,
causing the seed to generate keys like `scenario.qa_test_case_vs_checklist_v1.title`.
These keys had no entries in frontend i18n dictionaries, producing raw key visible output.

## Fix Applied

### Fix 1: Data Contract

Added `title_key` and `goal_key` to all 5 QA scenario JSON files so the keys are
explicit and stable.

### Fix 2: Localization Dictionaries

Added all 5 QA scenario title/goal entries to both `ru-RU.ts` and `en-US.ts`
frontend dictionaries under the `scenario` namespace.

### Fix 3: Rendering Safety

All `goal_key` fields now use `t()` for translation. All `target_skills` use
type-safe extraction. Added `tl()` helper for safe fallback rendering.

## Audit Results

| Pattern | Status |
|---------|--------|
| skill objects as React children | ✅ Safe |
| rubric objects as React children | ✅ N/A (rubrics not in frontend) |
| criteria objects as React children | ✅ Individual props only |
| weighted competency objects | ✅ N/A (backend-only) |
| evidence objects | ✅ Strings in API response |
| localized content objects | ✅ Strings from `t()` resolver |

## Verification

```bash
npx tsc --noEmit    # PASSED
npm run build       # PASSED
npx vitest run      # 63/63 PASSED
```
