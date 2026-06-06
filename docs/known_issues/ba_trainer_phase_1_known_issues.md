# BA Trainer Phase 1 — Known Issues

## Critical — Resolved

1. ~~**Railway Deployments Failing**~~ ✅ **RESOLVED** (2026-06-06)
   - **Status**: **Resolved** — Fixed in TRAINER-PLATFORM-BA-PHASE1-RAILWAY-BACKEND-PYTHON-IMAGE-FIX-004
   - **Root cause**: Two issues:
     1. Global `build.builder: "NIXPACKS"` in `railway.json` caused root-level scanning instead of `backend/` directory.
     2. Railway dashboard Build Command (`pip install -r requirements.txt`) ran in non-Python environment.
   - **Fix**: 
     - Removed global NIXPACKS builder from `railway.json`
     - Rewrote `Dockerfile` to single-stage `python:3.12-slim` with `python -m pip`
     - Removed `nixpacks.toml` to avoid conflicts
     - Deployed from repo root with `railway up . --path-as-root --service backend --environment staging`
   - **Evidence**: Deployment `3b91488b` SUCCESS — backend staging has 28 paths with BA activity routes.

## High
None.

## Medium

1. **Explanation key resolution in frontend**: The activity runner page looks up `explanation_key` via `t()` which expects exact locale key paths. If the key format doesn't match the locale file structure, explanations won't display.

2. **FillBlanks template markers**: The FillBlanksActivity component parses `___` markers in the template string. Templates that contain literal `___` strings (not blanks) will be incorrectly parsed.

3. **Numeric input validation**: The NumericActivity uses browser-native `<input type="number">` which accepts certain edge case inputs (e.g., "e", "+-"). No custom validation overlay exists.

4. **Matching activity UI on mobile**: The matching renderer places left items and right dropdowns side by side using flex. On very narrow screens (< 360px), the layout may overlap.

5. **All-localization in single file**: The `ru-RU.json` locale file contains all 164 question titles and explanations in a single file. This is acceptable for Phase 1 but should be split by module for maintainability.

## Low

6. **No en-US translations**: Only Russian locale is provided. English keys fall back to Russian text.

7. **Activity list ordering**: Activities are ordered by `order` field but this field is manually assigned in the generation script. Some modules may benefit from re-ordering.

8. **No progress animation**: Activity submission shows loading state but no animated transition between states.

## Out of Scope (Phase 2+)
- AI evaluation for open-ended questions
- Diagnostics assessment module
- Timed final exam
- XP/gamification
- Drag-sort, drag-group, and other unused interaction types
