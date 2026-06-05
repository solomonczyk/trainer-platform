# Trainer Platform — Staging Decision Record

## Layer
TRAINER-PLATFORM-MVP-003-EXTERNAL-STAGING-DEPLOYMENT-OR-STAGING-DECISION

## Date
2026-06-05

## Decision
**LOCAL STAGING ACCEPTED TEMPORARILY**

External staging deployment is **blocked**. The team continues using the local Docker Compose staging profile as the accepted temporary staging environment.

## Reason External Staging Is Unavailable

| # | Blocker | Detail |
|---|---------|--------|
| 1 | No cloud provider account | No Railway, Render, or Fly.io account exists — all require interactive web browser signup (email verification, GitHub OAuth, or credit card) |
| 2 | No API tokens/credentials | No `RAILWAY_TOKEN`, `RENDER_API_KEY`, `FLY_API_TOKEN`, or similar credentials are available in this environment |
| 3 | Railway CLI requires auth | `railway login --browserless` requires an interactive terminal; non-interactive environments need `RAILWAY_TOKEN` env var |
| 4 | No interactive browser | The environment has no interactive web browser for provider account creation |
| 5 | Render has no CLI | Render does not offer a CLI — account setup and deployment require a web browser |
| 6 | No VPS/server | No external server (DigitalOcean droplet, AWS EC2, VPS) exists for Docker-based deployment |

These constraints are **environment-specific** and can be resolved with a single action: creating an account on a supported cloud provider and generating an API token.

## Local Staging Status

Local Docker Compose staging is **fully operational** and meets all current testing needs:

| Capability | Status |
|------------|--------|
| PostgreSQL database | ✅ Running in Docker |
| Backend (FastAPI) | ✅ Running in Docker |
| Frontend (Next.js) | ✅ Running in Docker |
| Health endpoint | ✅ Passing |
| Ready endpoint | ✅ Passing |
| OpenAPI available | ✅ Available |
| Migrations | ✅ Applied |
| QA trainer seeded | ✅ Seeded |
| Full smoke test | ✅ Passed (18/18 steps) |
| CI integration | ✅ All CI checks pass |

## Blocker Remains Open

**The external staging blocker is preserved and remains open.**

This means the following restrictions continue to apply:

| Restriction | Status |
|-------------|--------|
| `production_accepted` | ❌ false — blocked by no external staging |
| `release_allowed` | ❌ false — blocked by no external staging |
| Production deployment | ❌ Not allowed |

## Exact External Staging Requirements

For the blocker to be resolved, ALL of the following must be true:

### Account & Access
- [ ] Account created on a supported cloud provider (Railway recommended)
- [ ] API token generated and available as `RAILWAY_TOKEN` (or equivalent)
- [ ] Team member(s) with admin access to the staging project

### Infrastructure
- [ ] PostgreSQL database provisioned and reachable
- [ ] Backend service deployed and healthy (`/health` returns 200)
- [ ] Frontend service deployed and reachable
- [ ] CORS configured between frontend and backend
- [ ] SSL/TLS enabled (included by default on Railway/Render/Fly.io)

### Configuration
- [ ] `APP_ENV=staging` set
- [ ] `FRONTEND_URL` and `CORS_ALLOWED_ORIGINS` point to external staging URLs
- [ ] `NEXT_PUBLIC_API_URL` points to external staging backend URL
- [ ] `AI_GATEWAY_PROVIDER=mock` (real OpenAI disabled)
- [ ] `OPENAI_API_KEY` remains empty
- [ ] `SECRET_KEY` is a unique, randomly generated value (not a default)
- [ ] `ADMIN_API_KEY` is a unique, randomly generated value (not a default)
- [ ] `ANALYTICS_ENABLED=true`
- [ ] `RATE_LIMIT_ENABLED=true`

### Data & Migrations
- [ ] Migrations applied (`alembic upgrade head`)
- [ ] QA Engineer Interview Trainer seeded
- [ ] Seed validation passed

### Smoke Test
- [ ] External frontend URL loads in browser
- [ ] Register/login synthetic user works
- [ ] Domain catalog visible
- [ ] QA Engineer Interview Trainer accessible
- [ ] Enrollment created
- [ ] Scenario started (Bug Report)
- [ ] Answer submitted
- [ ] Mock AI evaluation returns structured result
- [ ] Result visible to user
- [ ] Progress updated
- [ ] Analytics events recorded
- [ ] Raw answers absent from analytics events

### CI & Quality
- [ ] CI passes with external staging configuration
- [ ] Git committed and pushed
- [ ] Working tree clean

### Security
- [ ] No secrets committed to repository
- [ ] Staging secrets separate from production secrets
- [ ] Production secrets not used anywhere in staging
- [ ] Synthetic data only (no real user data)

## Blocker Resolution Checklist

Minimum steps to unblock:

```bash
# 1. Create Railway account (https://railway.app) — requires web browser
# 2. Install CLI and authenticate
npm install -g @railway/cli
railway login
# 3. Set token for non-interactive use
export RAILWAY_TOKEN="<generated-token>"
# 4. Deploy per instructions in staging_provider_decision.md
```

## Next Allowed Action

**The next allowed action is: `external_staging_deployment`**

Once an external provider account is available (Railway, Render, or Fly.io), the deployment configs in this repository are ready to use:

| File | Purpose |
|------|---------|
| [`railway.json`](../../railway.json) | Railway project definition |
| [`backend/nixpacks.toml`](../../backend/nixpacks.toml) | Backend build hints |
| [`frontend/nixpacks.toml`](../../frontend/nixpacks.toml) | Frontend build hints |
| [`docs/deployment/staging_provider_decision.md`](staging_provider_decision.md) | Provider evaluation and deployment steps |
| [`docs/deployment/staging_env_vars.md`](staging_env_vars.md) | Environment variable reference |

## What Cannot Happen Until External Staging Exists

1. **Production deployment** — `production_accepted` and `release_allowed` both remain `false`
2. **Real OpenAI enablement** — `FF_AI_EVALUATION_REAL_PROVIDER_ENABLED` must stay `false`
3. **Production data** — No real user data may be used
4. **Production secrets** — No production secrets may be committed or configured

## Documented By

This decision is recorded as part of TRAINER-PLATFORM-MVP-003-EXTERNAL-STAGING-DEPLOYMENT-OR-STAGING-DECISION.

Proof: [`docs/proofs/proof_trainer_platform_mvp_003_external_staging.json`](../proofs/proof_trainer_platform_mvp_003_external_staging.json)

## Related Documents

- [staging_provider_decision.md](staging_provider_decision.md) — Provider evaluation and deployment prep
- [staging_deployment_plan.md](staging_deployment_plan.md) — Original staging plan with local profile
- [staging_env_vars.md](staging_env_vars.md) — Environment variable reference
