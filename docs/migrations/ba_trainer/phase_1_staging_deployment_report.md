# BA Trainer Phase 1 — Staging Deployment Report

## Overview

- **Task**: TRAINER-PLATFORM-BA-PHASE1-RAILWAY-BACKEND-PYTHON-IMAGE-FIX-004
- **Implementation Commit**: `503a371`
- **Date**: 2026-06-06

## Deployment Summary

| Service | Environment | Status | URL |
|---------|------------|--------|-----|
| Backend | Railway staging | ✅ SUCCESS (28 paths, BA routes active) | https://backend-staging-0487.up.railway.app |
| Frontend | Railway staging | ✅ SUCCESS (unchanged) | https://frontend-staging-4146.up.railway.app |
| Database | Railway Postgres | Migration 002 applied | N/A |

## Build Fix Applied

The Railway backend build was failing because:

1. **Global NIXPACKS builder** in `railway.json` caused Railway to scan the monorepo root — no Python project detected there → `Nixpacks was unable to generate a build plan for this app`.
2. **Dashboard Build Command** (`pip install --no-cache-dir -r requirements.txt`) ran in a non-Python environment → `pip: command not found`.

### Fixes

| Change | Description |
|--------|-------------|
| `railway.json` | Removed global `build.builder: "NIXPACKS"`. Services use `DOCKERFILE` with `root: "backend"`. |
| `backend/Dockerfile` | Rewritten to single-stage `python:3.12-slim`. Uses `python -m pip`. Added `PYTHONDONTWRITEBYTECODE` and `PYTHONUNBUFFERED`. |
| `backend/nixpacks.toml` | Removed — was conflicting with Dockerfile build strategy. |
| `backend/.dockerignore` | Added — excludes `.venv`, `__pycache__`, test databases from build context. |

### Deployment

Deployed from repo root with:
```bash
railway up . --path-as-root --service backend --environment staging
```

This ensures `railway.json` is included in the build archive and its `root: "backend"` directive is respected.

## Database Migration

- **Migration**: `002_ba_trainer_activities.py`
- **Revision**: 002 (down_revision: 001)
- **Applied via**: Alembic upgrade head on staging Postgres
- **Status**: SUCCESS
- **Tables created**: `activities`, `deterministic_evaluations`
- **Columns modified on `attempts`**: Added `activity_id`, `activity_type`, `evaluation_mode`, `submitted_answer`, `idempotency_key`

### BA Trainer Seed

```json
{
  "domain": 0,
  "trainer": 1,
  "version": 1,
  "localization": 1,
  "track": 1,
  "module": 10,
  "activities": 164,
  "total_activities": 164
}
```

## Runtime Verification

| Check | URL | Status |
|-------|-----|--------|
| Health | `/health` | 200 |
| Ready | `/ready` | 200 |
| OpenAPI | `/openapi.json` | 200 (28 paths) |

### BA Activity Routes (3 new)

| Route | Method | Description |
|-------|--------|-------------|
| `/api/v1/trainers/{trainer_slug}/modules/{module_id}/activities` | GET | List activities in a module (no correct answers) |
| `/api/v1/trainers/{trainer_slug}/activities/{activity_id}/start` | GET | Start an activity (prompt without correct answers) |
| `/api/v1/trainers/{trainer_slug}/activities/submit` | POST | Submit answer for deterministic validation |

### Other new routes

| Route | Method | Description |
|-------|--------|-------------|
| `/api/v1/admin/seed/ba-trainer` | POST | Seed BA trainer data from package |

## Deployment History

| Attempt | Deployment ID | Status | Notes |
|---------|--------------|--------|-------|
| 1-8 | Various | FAILED | Railway infra + build config issues |
| 9 | `3b91488b` | ✅ SUCCESS | Fixed Dockerfile + railway.json, deployed from repo root |

## QA Verification

- **QA Trainer**: ✅ Available on staging (`GET /api/v1/trainers/qa-engineer-interview-trainer`)
- **Correct answers hidden**: ✅ All activity response schemas exclude `correct` field
- **Deterministic validation**: ✅ 5 validator types (single_choice, multiple_choice, numeric, fill_blanks, matching)
- **Frontend staging**: ✅ HTTP 200
- **Production**: ❌ Not deployed
