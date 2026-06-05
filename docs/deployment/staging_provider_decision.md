# Trainer Platform — Staging Provider Decision

## Layer
TRAINER-PLATFORM-MVP-003-EXTERNAL-STAGING-DEPLOYMENT-OR-STAGING-DECISION

## Date
2026-06-05

## Status
NOT DEPLOYED — Provider evaluated and configs prepared; deployment blocked by absence of cloud provider account and API token in this environment.

## Selected Provider

**Railway (recommended)**

## Reason for Selection

| Criteria | Railway | Render | Fly.io | Vercel + Backend |
|----------|---------|--------|--------|-------------------|
| PostgreSQL managed | ✅ Native | ✅ Native | ✅ Via fly postgres | ❌ Need separate provider |
| Backend (Python FastAPI) | ✅ Nixpacks + Docker | ✅ Web Service | ✅ Docker | ❌ Functions not suitable |
| Frontend (Next.js) | ✅ Nixpacks + Docker | ✅ Web/Static | ✅ Docker | ✅ Native (best) |
| CLI-first deployment | ✅ Excellent CLI | ❌ No official CLI | ✅ flyctl | ✅ Vercel CLI |
| Free tier available | ✅ (limited) | ✅ (limited, 90d PG) | ✅ (limited) | ✅ (Hobby) |
| No-credit-card startup | ❌ Requires card | ❌ Requires card | ❌ Requires card | ❌ Requires card |
| GitHub integration | ✅ Auto-deploy | ✅ Auto-deploy | ✅ Via GH Actions | ✅ Auto-deploy |
| Secret management | ✅ Built-in | ✅ Built-in | ✅ Built-in | ✅ Built-in |
| Custom domains | ✅ | ✅ | ✅ | ✅ |
| Multi-region | ❌ | ❌ | ✅ | ✅ |
| Docker support | ✅ Full | ✅ Full | ✅ Full | ❌ Buildpack only |

**Railway** was selected because:
1. **Best CLI experience** — `railway` CLI is well-documented, supports non-interactive auth via `RAILWAY_TOKEN`, and handles all operations (project create, deploy, env vars, connect to DB).
2. **Native PostgreSQL** — Railway provides managed PostgreSQL with one-command provisioning (`railway add postgres`), automatic backups, and connection string injection.
3. **Nixpacks + Docker dual support** — Can auto-detect Python/FastAPI and Node.js/Next.js via Nixpacks, or use custom Dockerfiles. Our existing Dockerfiles are fully compatible.
4. **Unified platform** — All three tiers (DB + Backend + Frontend) on one platform, simplifying networking and secret management.
5. **Cost effective** — Pay-as-you-go with a generous free starter tier. Estimated cost for staging: $0–$5/month with a single developer.

## Deployment Targets

| Component | Railway Service Type | Port | Notes |
|-----------|---------------------|------|-------|
| PostgreSQL | Railway PostgreSQL plugin | 5432 | Managed, auto-backup |
| Backend | Railway Service (Docker/Nixpacks) | 8000 | FastAPI + uvicorn |
| Frontend | Railway Service (Docker/Nixpacks) | 3000 | Next.js standalone |

## Expected URLs (Example — actual URLs generated on deploy)

| Service | URL Pattern |
|---------|-------------|
| Frontend | `https://trainer-platform-frontend.up.railway.app` |
| Backend API | `https://trainer-platform-backend.up.railway.app` |
| Health | `https://trainer-platform-backend.up.railway.app/health` |
| Ready | `https://trainer-platform-backend.up.railway.app/ready` |
| OpenAPI | `https://trainer-platform-backend.up.railway.app/openapi.json` |

## Expected Cost

| Resource | Estimated Monthly Cost |
|----------|----------------------|
| PostgreSQL (Starter) | $0–$5 |
| Backend service (Starter) | $0–$5 |
| Frontend service (Starter) | $0–$5 |
| Total estimated | $0–$15/month (staging, low traffic) |

## Limitations

1. **Cold starts** — Free/starter tier services spin down after inactivity (~15 min). First request after idle has 5–15s latency.
2. **No multi-region** — Railway deploys to a single region (us-west by default). For global staging, additional configuration needed.
3. **No built-in CDN** — Frontend assets served directly from container, not CDN. For staging this is acceptable.
4. **Logging** — Railway logs have 1-day retention on free tier.
5. **No WAF** — No built-in web application firewall. Relies on application-level security (JWT, rate limiting).

## Rollback Approach

| Scenario | Rollback Method |
|----------|-----------------|
| Bad deployment | `railway down` + redeploy previous version |
| Database corruption | Railway PostgreSQL point-in-time recovery (7-day retention) |
| Configuration error | Update env vars via `railway variable set` + redeploy |
| Full rollback to local staging | Revert git + `docker compose -f docker-compose.staging.yml up -d` |

## Provider-Specific Config Files

The following config files are prepared and ready for use:

| File | Purpose |
|------|---------|
| [`railway.json`](../../railway.json) | Railway project definition (services, build config, watchers) |
| [`backend/nixpacks.toml`](../../backend/nixpacks.toml) | Nixpacks build hints for Python/FastAPI backend |
| [`frontend/nixpacks.toml`](../../frontend/nixpacks.toml) | Nixpacks build hints for Next.js frontend |

## How to Deploy (Once Account Is Available)

```bash
# 1. Install Railway CLI and login
npm install -g @railway/cli
railway login --browserless  # or set RAILWAY_TOKEN

# 2. Create project
railway init --name trainer-platform-staging

# 3. Add PostgreSQL
railway add postgres

# 4. Deploy backend
cd backend
railway deploy --service backend

# 5. Deploy frontend
cd frontend
railway deploy --service frontend

# 6. Set environment variables
railway variable set APP_ENV=staging
railway variable set AI_GATEWAY_PROVIDER=mock
railway variable set ANALYTICS_ENABLED=true
# ... (see staging_env_vars.md for all)

# 7. Run migrations
railway run alembic upgrade head

# 8. Seed QA trainer
railway run python scripts/seed_trainer_package.py \
  ../trainer_packages/qa_engineer_interview_trainer

# 9. Verify health
curl https://<backend-url>/health
curl https://<backend-url>/ready
```

## Alternative: Render

If Railway is not suitable, Render is the recommended alternative:

| Aspect | Render vs Railway |
|--------|------------------|
| PostgreSQL | ✅ 90-day free trial, then $7/month |
| CLI | ❌ No official CLI — web UI or API only |
| Docker | ✅ Full support |
| Blueprint | ✅ Infrastructure-as-code via `render.yaml` |
| Auto-deploy | ✅ From GitHub |

A Render blueprint (`render.yaml`) is prepared but not committed (requires account to test).

## Alternative: Fly.io

Fly.io is recommended if multi-region deployment is required:

| Aspect | Fly.io |
|--------|--------|
| PostgreSQL | ✅ Via `fly postgres` (separate app) |
| CLI | ✅ Excellent (`flyctl` / `fly`) |
| Docker | ✅ Native — deploy any Dockerfile |
| Free tier | ✅ Up to 3 shared VMs |
| Global | ✅ 30+ regions |

## Security Notes

- **No secrets committed** — All secrets in `railway.json` reference Railway env vars
- **Mock AI provider** — Real OpenAI remains disabled in staging
- **Synthetic data only** — QA Engineer Interview Trainer package contains no real user data
- **Separate Railway project** — Staging uses a completely separate project from any future production
- **Environment isolation** — `APP_ENV=staging` prevents accidental production behavior

## Related Documents

- [staging_decision_record.md](staging_decision_record.md) — Formal decision record (Option B)
- [staging_deployment_plan.md](staging_deployment_plan.md) — Original staging deployment plan
- [staging_env_vars.md](staging_env_vars.md) — Environment variable reference
