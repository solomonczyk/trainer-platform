# BA Trainer Phase 1 — Known Issues

## Critical
None.

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
