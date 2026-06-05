# Trainer Platform — Staging Environment Variables

## Layer
TRAINER-PLATFORM-MVP-002-STAGING-DEPLOY-PREPARATION

## Date
2026-06-05

## Overview

This document lists all environment variables required for the staging
deployment of Trainer Platform MVP.

For local Docker Compose staging, variables are set in the
`docker-compose.staging.yml` file under each service's `environment` block.

For external staging (future), variables should be set via the platform's
secret manager (Render env vars, Railway secrets, GitHub Actions secrets, etc.).

## Required Variables

### Application

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `APP_ENV` | `staging` | Runtime environment |
| `APP_NAME` | `TrainerPlatform` | Application name |
| `APP_VERSION` | `0.1.0` | Semantic version |
| `DEBUG` | `false` | Must be false in staging |
| `SECRET_KEY` | `staging-<random-secret>` | Generate a random secret; never commit |
| `REQUEST_ID_HEADER` | `X-Request-ID` | Request tracing header |

### Database

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/db` | Async connection string |
| `DATABASE_SYNC_URL` | `postgresql://user:pass@host:5432/db` | Sync connection string for scripts |

Local staging uses:
- User: `trainer`
- Password: `trainer_staging_pass`
- Host: `postgres` (Docker service name)
- Port: `5432`
- Database: `trainer_platform_staging`

### Auth

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | 24 hours |
| `ALGORITHM` | `HS256` | JWT signing algorithm |

### AI Gateway (Mock Provider)

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `AI_GATEWAY_PROVIDER` | `mock` | Mock provider for staging |
| `AI_GATEWAY_API_KEY` | `` (empty) | Not needed for mock |
| `AI_GATEWAY_MODEL` | `gpt-4o-mini` | Model identifier |
| `AI_GATEWAY_TIMEOUT_SECONDS` | `30` | Request timeout |
| `AI_GATEWAY_MAX_RETRIES` | `1` | Max retry attempts |
| `AI_GATEWAY_FALLBACK_PLACEHOLDER_ENABLED` | `true` | Fallback on failure |

### OpenAI (Real Provider)

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `OPENAI_API_KEY` | `` (empty) | **Must remain empty in this layer** |

Real OpenAI provider is **disabled** in this layer. Set only when explicitly
authorized in a future layer.

### Analytics

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `ANALYTICS_ENABLED` | `true` | Analytics recording enabled |

### Feature Flags

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `FF_TRAINER_QA_INTERVIEW_VISIBLE` | `true` | QA trainer visible |
| `FF_TRAINER_QA_INTERVIEW_ENROLLMENT_ENABLED` | `true` | Enrollment enabled |
| `FF_SCENARIO_RUNTIME_ENABLED` | `true` | Scenario runtime enabled |
| `FF_AI_EVALUATION_ENABLED` | `true` | AI evaluation enabled |
| `FF_AI_EVALUATION_REAL_PROVIDER_ENABLED` | `false` | Real provider disabled |
| `FF_ANALYTICS_ENABLED` | `true` | Analytics enabled |
| `FF_LOCALE_EN_US_ENABLED` | `true` | English locale enabled |
| `FF_BETA_ACCESS_ENABLED` | `false` | Beta access disabled |

### Localization

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `DEFAULT_LOCALE` | `ru-RU` | Default UI locale |
| `FALLBACK_LOCALE` | `en-US` | Fallback locale |

### Logging

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `LOG_LEVEL` | `info` | Log level |
| `LOG_FORMAT` | `json` | Structured JSON logging |

### Rate Limiting

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `RATE_LIMIT_ENABLED` | `true` | **Enabled** in staging |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `120` | 120 requests/minute/IP |

### CORS / Frontend

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `FRONTEND_URL` | `http://localhost:3000` | Frontend origin for CORS |
| `CORS_ALLOWED_ORIGINS` | `` (empty) | Additional comma-separated origins |

### Admin

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `ADMIN_API_KEY` | `staging-<random-key>` | Admin API key; never commit |

## Frontend Env Variables

| Variable | Staging Value | Notes |
|----------|---------------|-------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL (client-side) |

## Security Rules

1. **Never commit real secrets** to the repository
2. **Never use production secrets** in staging
3. **Never enable real OpenAI provider** without authorization
4. Use synthetic test data only
5. Rotate secrets before promoting to production
6. Use platform secret manager for external staging

## Docker Compose Reference

For local Docker staging, all variables are declared in:
[`docker-compose.staging.yml`](../../docker-compose.staging.yml)

See also: [staging_deployment_plan.md](staging_deployment_plan.md)
