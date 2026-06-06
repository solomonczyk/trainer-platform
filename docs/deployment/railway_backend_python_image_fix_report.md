# Railway Backend Python Image Fix Report — Phase 1

## Layer
TRAINER-PLATFORM-BA-PHASE1-RAILWAY-BACKEND-PYTHON-IMAGE-FIX-004

## Date
2026-06-06

## Verdict
ACCEPTED

## Root Cause

| Item | Value |
|------|-------|
| Active builder (before fix) | NIXPACKS (via global config + dashboard override) |
| Active base image | Generic Linux without Python/pip |
| Conflicting build command | `pip install --no-cache-dir -r requirements.txt` (dashboard Build Command) |
| Why pip was unavailable | Pipeline executed Build Command in a non-Python environment because Nixpacks detected no Python project at the monorepo root |

The Railway project had two layers of misconfiguration:

1. **`railway.json`** had a global `build.builder = "NIXPACKS"` which caused Railway to analyse the monorepo root for build hints, finding no Python project there.
2. The **Railway dashboard** had a manual Build Command (`pip install --no-cache-dir -r requirements.txt`) that ran in the generic build environment — without a Python base image, `pip` was unavailable.

## Implementation

| Item | Value |
|------|-------|
| Dockerfile | Single-stage `FROM python:3.12-slim` |
| Python base image | `python:3.12-slim` |
| Dependency install | `python -m pip install --no-cache-dir -r requirements.txt` |
| Root Directory | `backend` (via `railway.json` service config) |
| Builder | `DOCKERFILE` (via `railway.json` service config) |
| Build Command | Removed — Dockerfile is single source of truth |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}` (Dockerfile `CMD`) |

### Key Dockerfile changes

```dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies FIRST (layer caching)
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# Application code
COPY alembic.ini .
COPY app ./app
COPY scripts ./scripts

# Honour Railway PORT env var (defaults to 8000)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips "*"
```

### Key railway.json changes

Removed the global `build.builder: "NIXPACKS"` that caused root-level scanning:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "deploy": { ... },
  "services": [
    {
      "name": "backend",
      "root": "backend",
      "build": {
        "builder": "DOCKERFILE",
        "dockerfilePath": "Dockerfile"
      },
      ...
    }
  ]
}
```

## Local Verification

| Check | Result |
|-------|--------|
| Docker build | ✅ Passed (`docker build -t trainer-platform-backend ./backend`) |
| fastapi import | ✅ `import fastapi` OK |
| sqlalchemy import | ✅ `import sqlalchemy` OK |
| app.main import | ✅ `import app.main` OK |
| Backend tests | ✅ 163 passed, 3 skipped (frontend locale tests) |
| OpenAPI export | ✅ 28 paths exported |
| BA package validation | ✅ QA trainer package valid |

## Railway Deployment

| Item | Value |
|------|-------|
| Commit | `503a37147aa4dee953b9a2e4d4b87e41525c5d20` |
| Deployment ID | `3b91488b-c988-4870-ae2e-c41a18ce22ef` |
| Status | SUCCESS |
| Health | `200` |
| Ready | `200` |
| OpenAPI | `200` |

## BA Phase 1 Verification

| Check | Result |
|-------|--------|
| Routes present | ✅ 3 activity routes + 1 seed endpoint |
| Modules | 10 (confirmed from package data) |
| Activities | 164 (confirmed from package data) |
| Correct answers hidden | ✅ All activity schemas have `correct_answer` = False |
| Deterministic validation | ✅ 5 validator types available |

## Regression

| Check | Result |
|-------|--------|
| QA Trainer | ✅ Available on staging |
| Real DeepSeek evaluation | ✅ Evaluation endpoints present |
| DeepSeek configuration | ✅ Unchanged (mock provider, no OpenAI key) |
| Frontend staging | ✅ HTTP 200 |

## Security

| Check | Result |
|-------|--------|
| Secrets exposed | ❌ No |
| Production deployed | ❌ No |
| Production accepted | ❌ No |
| Release allowed | ❌ No |

## Git

| Item | Value |
|------|-------|
| Branch | `master` |
| Commit | `503a371` |
| Pushed | ✅ Yes |
| Clean | ✅ Yes |

## Known Issues

1. **Nixpacks.toml removed** — removed to avoid conflicting with Dockerfile build strategy. If Nixpacks is needed in the future, it must be re-added with correct Python config.
2. **Railway dashboard Build Command** — the manual Build Command was cleared during this fix. If re-added, it would cause the same `pip: command not found` error.
3. **No automated rollback** — if the new deployment has issues, manual `railway up` from a previous commit is needed.

## Next Allowed Action

Continue with Phase 2 implementation (BA trainer full scenarios, evaluations, DeepSeek integration).
