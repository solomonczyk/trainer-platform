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
2. Record target commit to `DEPLOYED_COMMIT` env
3. Validate deployment secrets (fail-fast)
4. SSH to VPS
5. Write target to `pending_commit` (atomic `mktemp` + `mv`)
6. `git fetch` + checkout exact commit (with SHA mismatch guard)
7. Build Docker images (backend + frontend)
8. Run Alembic migrations
9. Restart services with `docker compose up -d`
10. Wait for container health checks
11. HTTPS health check (retry up to 5 times)
12. **On success**: rotate `current_commit→previous_commit`, `pending_commit→current_commit`, remove `pending_commit`
13. **On failure**: preserve `current_commit` and `previous_commit`, do not mark failed target

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
# Dry-run (validate without executing)
/opt/trainer-platform/scripts/rollback.sh --dry-run

# Rollback to previous deployment
/opt/trainer-platform/scripts/rollback.sh

# Rollback to specific commit
/opt/trainer-platform/scripts/rollback.sh --target <commit-sha>
```

### Modes

| Flag | Description |
|------|-------------|
| `--dry-run` | Validate rollback plan without executing |
| `--target <sha>` | Roll back to specific commit (default: `previous_commit`) |
| (no flags) | Execute real rollback to `previous_commit` |

### Dry-Run Output

```
current_commit=<sha>
rollback_target=<sha>
target_resolvable=true
target_distinct=true
would_checkout_exact_sha=true
would_rebuild_or_restart=true
would_preserve_database_volume=true
would_run_container_health_checks=true
would_run_https_health_check=true
real_rollback_executed=false
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

- Previous commit SHA is recorded at `/opt/trainer-platform/deploy/previous_commit`
- Current commit SHA at `/opt/trainer-platform/deploy/current_commit`
- Pending commit (during active deployment) at `/opt/trainer-platform/deploy/pending_commit`
- All files use atomic writes (`mktemp` + `mv`)
- Rollback rebuilds images from that commit
- No data rollback needed (migrations are backward-compatible)
- Database volume is preserved (no destructive prune)
- Post-rollback container health checks and HTTPS health checks are automated
- Rollback dry-run validates target resolution, distinctness, and all infrastructure preconditions
- Railway staging remains as fallback
