# Railway Staging Environment Variables

## Backend Service

| Variable                        | Value                                                 | Source         |
|---------------------------------|-------------------------------------------------------|----------------|
| `APP_ENV`                       | `staging`                                             | Manual         |
| `AI_PROVIDER`                   | `mock`                                                | Manual         |
| `AI_MODEL_EVALUATOR`            | `mock-evaluator`                                      | Manual         |
| `AI_REAL_PROVIDER_ENABLED`      | `false`                                               | Manual         |
| `AI_MAX_COST_PER_REQUEST_USD`   | `0.05`                                                | Manual         |
| `AI_TIMEOUT_SECONDS`            | `30`                                                  | Manual         |
| `ANALYTICS_ENABLED`             | `true`                                                | Manual         |
| `RATE_LIMIT_ENABLED`            | `true`                                                | Manual         |
| `RATE_LIMIT_REQUESTS_PER_MINUTE`| `60`                                                  | Manual         |
| `LOG_LEVEL`                     | `info`                                                | Manual         |
| `DATABASE_URL`                  | `postgresql+asyncpg://...@postgres.railway.internal`  | Railway        |
| `JWT_SECRET`                    | *(managed secret)*                                    | Manual         |
| `FRONTEND_URL`                  | `https://frontend-staging-4146.up.railway.app`        | Manual         |
| `CORS_ALLOWED_ORIGINS`          | `https://frontend-staging-4146.up.railway.app`        | Manual         |
| `PORT`                          | `8000`                                                | Manual         |

## Frontend Service

| Variable                      | Value                                             | Source     |
|-------------------------------|---------------------------------------------------|------------|
| `NEXT_PUBLIC_API_URL`         | `https://backend-staging-0487.up.railway.app`     | Manual     |
| `NEXT_PUBLIC_APP_ENV`         | `staging`                                         | Manual     |

## Database Service (PostgreSQL)

Automatically provisioned by Railway:

| Variable            | Value                                       |
|---------------------|---------------------------------------------|
| `DATABASE_URL`      | `postgresql://postgres:...@postgres.railway.internal:5432/railway` |
| `DATABASE_PUBLIC_URL` | `postgresql://postgres:...@shortline.proxy.rlwy.net:18291/railway` |
| `PGHOST`            | `postgres.railway.internal`                  |
| `PGPORT`            | `5432`                                       |
| `PGUSER`            | `postgres`                                   |
| `PGDATABASE`        | `railway`                                    |

## Security Notes

- All env vars with secrets (`DATABASE_URL`, `JWT_SECRET`) are managed via Railway's variable system
- No `.env` files are committed to git
- `.env.railway.local` exists for local tooling but is gitignored
- Real OpenAI provider is DISABLED (`AI_REAL_PROVIDER_ENABLED=false`)
- Production acceptance is `false` — this is staging only
