# 010a — Primary Flow Architecture

## Overview

This document describes the architecture changes made to integrate immersive quests into the primary QA and BA learner flows, making the quest catalog the default entry point and removing the legacy textarea-only scenario experience from normal user navigation.

## Architecture Decision

### Problem
Layer 010 implemented the Quest Engine but kept it as a parallel feature. The primary user flow still led to the legacy textarea-only scenario UI (`/scenarios/{scenarioId}`). The operator review rejected this state.

### Solution
Three architectural changes:

1. **Trainer page CTA**: Changed from `/trainers/{slug}/scenarios` to `/trainers/{slug}/quests`
2. **Legacy route handler**: The `/scenarios/{scenarioId}` route now checks a scenario-to-quest mapping and redirects to the immersive quest engine
3. **Scenario catalog filtering**: The `/trainers/{slug}/scenarios` API endpoint filters out hidden (HIDE_TEMPORARILY) scenarios by default

## Route Map

### Before (Layer 010)
```
Home → Domain → Trainer → `/trainers/{slug}/scenarios` (legacy catalog)
                                    → `/scenarios/{scenarioId}` (textarea-only UI)
                                    → `/trainers/{slug}/quests` (parallel, not linked)
                                    → `/trainers/{slug}/quests/{questId}` (immersive)
```

### After (Layer 010a)
```
Home → Domain → Trainer → `/trainers/{slug}/quests` (primary CTA)
                                    → `/trainers/{slug}/quests/{questId}` (immersive)
                                    → `/scenarios/{scenarioId}` → redirects to quest
                                    → `/trainers/{slug}/scenarios` (hidden by default, internal)
```

## Component Changes

### Frontend
- `frontend/src/app/trainers/[slug]/page.tsx`: CTA changed to quests, added quest catalog section
- `frontend/src/app/scenarios/[scenarioId]/page.tsx`: Added mapping check on mount, redirects to quest

### Backend
- `backend/app/modules/scenarios/scenario_quest_mapping.py`: New canonical mapping module
- `backend/app/modules/scenarios/router.py`: Added mapping endpoint, hidden scenario filtering
- `backend/app/modules/quests/quest_data.py`: Added `qa_bug_report_structure_v1` mini-quest

## Scenario-to-Quest Mapping Contract

See [010a_scenario_to_quest_mapping.md](010a_scenario_to_quest_mapping.md) for the full mapping.
