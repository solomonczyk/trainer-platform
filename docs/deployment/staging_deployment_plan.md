# Trainer Platform — Staging Deployment Plan

## Layer
TRAINER-PLATFORM-MVP-002-STAGING-DEPLOY-PREPARATION

## Date
2026-06-05

## Status
IN PROGRESS — Local staging profile created

## Overview

This document describes the staging deployment strategy for Trainer Platform MVP.
Since no external staging provider was available at the time of this layer, a
**local-staging deployment profile** using Docker Compose has been created.

## Deployment Approach

| Component | Technology | Staging Method |
|-----------|-----------|----------------|
| Frontend  | Next.js 14 (standalone output) | Docker container |
| Backend   | FastAPI (Python 3.12, uvicorn) | Docker container |
| Database  | PostgreSQL 16 Alpine | Docker container |
| API Proxy | Next.js rewrites (built-in) | Frontend container |

## Infrastructure

### Local Staging Profile

Uses Docker Compose to run all three tiers on a single host:

```
┌─────────────────────────────────────────────────────┐
│                    Docker Host                        │
│                                                       │
│  ┌──────────────┐    ┌──────────────┐                 │
│  │  Frontend     │    │   Backend    │                 │
│  │  :3000        │───▶│  :8000       │                 │
│  │  Next.js      │    │  FastAPI     │                 │
│  └──────────────┘    └──────┬───────┘                 │
│                              │                         │
│                              ▼                         │
│                    ┌──────────────────┐               │
│                    │   PostgreSQL     │               │
│                    │   :5432          │               │
│                    └──────────────────┘               │
└─────────────────────────────────────────────────────┘
```

### File: `docker-compose.staging.yml`

Contains three services:
- `postgres` — PostgreSQL 16 Alpine, port 5433 (host) → 5432 (container)
- `backend` — FastAPI with uvicorn, port 8000
- `frontend` — Next.js standalone, port 3000

## Usage

### Start staging
```bash
docker compose -f docker-compose.staging.yml up -d
```

### Run migrations
```bash
docker compose -f docker-compose.staging.yml exec backend alembic upgrade head
```

### Seed QA trainer package
```bash
docker compose -f docker-compose.staging.yml exec backend \
  python scripts/seed_trainer_package.py ../trainer_packages/qa_engineer_interview_trainer
```

### Check health
```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

### Run smoke tests
```bash
cd backend && python tests/e2e/test_smoke.py
```

### View logs
```bash
docker compose -f docker-compose.staging.yml logs -f
```

### Stop staging
```bash
docker compose -f docker-compose.staging.yml down
```

### Full teardown (including volumes)
```bash
docker compose -f docker-compose.staging.yml down -v
```

## URLs

| Service     | URL                          |
|-------------|------------------------------|
| Frontend    | http://localhost:3000        |
| Backend API | http://localhost:8000        |
| Health      | http://localhost:8000/health |
| Ready       | http://localhost:8000/ready  |
| API Docs    | http://localhost:8000/docs   |
| OpenAPI     | http://localhost:8000/openapi.json |

## Environment Variables

See [staging_env_vars.md](staging_env_vars.md) for the full list.

## CI / Quality

- CI runs on push to `master` / `main` / `release/**` branches
- CI includes: backend tests, trainer package validation, migration check,
  frontend build, frontend tests, OpenAPI export
- All continue-on-error flags removed

## Future: External Staging

When an external staging provider becomes available (Render, Railway, Fly.io, etc.),
the `docker-compose.staging.yml` configuration serves as the reference for:
- Environment variables (all secrets via platform secret manager)
- Service architecture (PostgreSQL + Backend + Frontend)
- Health check endpoints
- Migration and seed procedures

## Security Notes

- Mock AI provider used (real OpenAI disabled)
- Separate staging database credentials (not production)
- No real user data used
- Secrets managed via Docker Compose env vars (for local staging) or
  platform secret manager (for external staging)
