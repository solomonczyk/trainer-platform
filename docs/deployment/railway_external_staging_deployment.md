# Railway External Staging Deployment

## Overview

Deployment of Trainer Platform MVP to Railway external staging (MVP-004).

## Project Configuration

- **Railway Project**: `protective-passion`
- **Project ID**: `800b800a-c306-4bcb-aa81-bad8db9e51fc`
- **Environment**: `staging` (forked from `production`)
- **Environment ID**: `51b6eec0-494b-49c2-8a56-f0959f237e42`

## Services

| Service   | Type       | Status  | URL                                             |
|-----------|------------|---------|-------------------------------------------------|
| backend   | FastAPI    | SUCCESS | https://backend-staging-0487.up.railway.app     |
| frontend  | Next.js    | SUCCESS | https://frontend-staging-4146.up.railway.app    |
| Postgres  | PostgreSQL | SUCCESS | Internal: postgres.railway.internal:5432        |

## Deployment Commands

### Backend
```bash
cd backend
railway up --service backend -e staging -p <project_id> --detach
railway domain -s backend -e staging
```

### Frontend
```bash
cd frontend
railway up --service frontend -e staging -p <project_id> --detach
railway domain -s frontend -e staging
```

### Environment Variables
See [railway_env_vars.md](railway_env_vars.md) for the full list.

## Build Method

Both services use Dockerfile-based builds:

- **Backend**: `backend/Dockerfile` — Python 3.12-slim, FastAPI + uvicorn on port 8000
- **Frontend**: `frontend/Dockerfile` — Node.js 20-alpine, Next.js standalone on port 3000

## Data Flow

```
User → https://frontend-staging-4146.up.railway.app
         → API calls to https://backend-staging-0487.up.railway.app
              → PostgreSQL at postgres.railway.internal:5432
```

## Health Endpoints

- Backend: https://backend-staging-0487.up.railway.app/health
- Ready:    https://backend-staging-0487.up.railway.app/ready
- OpenAPI:  https://backend-staging-0487.up.railway.app/openapi.json

## Authentication

- JWT-based auth with Railway-managed `JWT_SECRET`
- Admin user: admin@trainerplatform.com (seeded)
- AI Provider: mock (no real OpenAI keys used)
