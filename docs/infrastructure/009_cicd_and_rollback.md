# CI/CD and Rollback — 009

## CI Pipeline

File: `.github/workflows/ci.yml`

Triggers: `push` to `master`/`main`/`release/**`

Jobs:
- Backend Tests (Python 3.12, PostgreSQL)
- Trainer Package Validation
- Migration Check (including rollback test)
- Frontend Build (TypeScript, Next.js)
- Frontend Tests (Vitest)
- OpenAPI Export

## Deployment Workflow

File: `.github/workflows/deploy-staging.yml`

### Trigger

- Automatically after CI passes on `master`
- Manual dispatch with optional commit SHA

### Process

1. Checkout exact commit
2. SSH to VPS
3. `git fetch` + checkout exact commit
4. Build Docker images (backend + frontend)
5. Run Alembic migrations
6. Restart services with `docker compose up -d`
7. Health check (retry up to 5 times)

### Required Configuration

| Setting          | Source     | Value                     |
|------------------|------------|---------------------------|
| VPS_HOST         | env var    | 152.53.227.37             |
| VPS_USER         | env var    | trainer                   |
| VPS_PORT         | env var    | 22                        |
| VPS_SSH_KEY      | Secret     | SSH private key for deployment |
| VPS_DEPLOY_PATH  | env var    | /opt/trainer-platform     |

### Preflight Validation

The workflow includes a `Validate deployment secrets` step that fails fast
before SSH connection if any required configuration is missing.

## Rollback

### Script

Location: `/opt/trainer-platform/scripts/rollback.sh`

Usage:
```bash
# Rollback to previous deployment
sudo -u trainer /opt/trainer-platform/scripts/rollback.sh

# Rollback to specific commit
sudo -u trainer /opt/trainer-platform/scripts/rollback.sh <commit-sha>
```

### Manual Rollback

```bash
cd /opt/trainer-platform/repo
git checkout <previous-commit>
cd /opt/trainer-platform/deploy
docker compose build backend frontend
docker compose up -d backend frontend caddy
```

### Rollback Safety

- Previous commit SHA is recorded at `/tmp/previous_deployed_commit`
- Rollback rebuilds images from that commit
- No data rollback needed (migrations are backward-compatible)
- Railway staging remains as fallback
