# Persistent Rollback, Git Clean, and HEAD Reconciliation Closeout — 009B

## Summary

Closeout of remaining audit blockers after the successful VPS CI/CD deployment (009A):

1. **Persistent commit tracking** — replaced `/tmp` ephemeral records with persistent files at `/opt/trainer-platform/deploy/{current,previous,pending}_commit`
2. **Health-gated commit rotation** — pending commit written before deploy; current/previous only rotated after health checks pass
3. **Rollback dry-run** — `--dry-run` and `--target <sha>` modes; validates target resolution, distinctness, checkout, rebuild, database volume preservation, container + HTTPS health checks
4. **`git clean`** — `.claude/` classified as local agent state and gitignored
5. **HEAD reconciliation** — diff between deployed commit (`2b625b1`) and repository HEAD (`d2c7ea3`) confirmed docs/proofs and workflow changes only; no runtime code changed

## Changes Applied

| Change | File | Description |
|--------|------|-------------|
| Persistent commit tracking | `.github/workflows/deploy-staging.yml` | Replace `/tmp` with `/opt/trainer-platform/deploy/`; write pending_commit before deploy; rotate only after health pass |
| Atomic file updates | `.github/workflows/deploy-staging.yml` | Use `mktemp` + `mv` for all commit file writes |
| Checkout verification | `.github/workflows/deploy-staging.yml` | SHA mismatch guard after `git checkout` |
| Rollback script | `/opt/trainer-platform/scripts/rollback.sh` | Added `--dry-run`, `--target <sha>`; reads from persistent `previous_commit`; validates 10 preconditions; container + HTTPS health checks |
| Git clean | `.gitignore` | Added `.claude/` (local agent harness state) |
| Persistent records | `/opt/trainer-platform/deploy/{current,previous}_commit` | Initialized from verified deployment history (`2b625b1`, `222d5ba`) |

## Persistent Commit Tracking

### Files

| Path | Purpose | Semantics |
|------|---------|-----------|
| `/opt/trainer-platform/deploy/current_commit` | Last successfully deployed and health-checked commit | Updated only after health pass |
| `/opt/trainer-platform/deploy/previous_commit` | Successful commit immediately before current | Rotated atomically with current update |
| `/opt/trainer-platform/deploy/pending_commit` | Target being deployed but not yet health-accepted | Written before deploy; removed after rotation |

### Ownership and Permissions

```
directory: trainer:trainer, 0755
files:     trainer:trainer, 0644
```

### Health-Gated Rotation Sequence

1. Read persistent current_commit
2. Validate target commit
3. Write target to pending_commit (atomic)
4. Checkout exact target commit (with SHA mismatch guard)
5. Build Docker images
6. Run Alembic migrations
7. Restart services with `docker compose up -d`
8. Wait for container health checks
9. Run HTTPS health check (up to 5 retries)
10. **On success**: rotate current→previous, pending→current, remove pending
11. **On failure**: preserve current, preserve previous, do not mark failed target as current

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

### Dry-Run Checks

- current_commit exists and is readable
- Rollback target exists (default: previous_commit)
- Target is a valid git commit
- Target differs from current
- Docker Compose file exists
- Required env files exist (backend.env, frontend.env)
- Database volume is preserved (no destructive prune)

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

## Git Hygiene

`.claude/` inspected and classified as `LOCAL_AGENT_STATE` (contains only `scheduled_tasks.lock`, a 1K lock file). No secrets found. Resolved by adding to `.gitignore`.

## HEAD Reconciliation

| Aspect | Value |
|--------|-------|
| Deployed runtime commit | `d2c7ea3aa3f316fa6cde618a4e45e0a57acc8678` |
| Repository HEAD (master) | `d2c7ea3aa3f316fa6cde618a4e45e0a57acc8678` |
| HEAD matches origin/master | Yes |
| Changed files after `2b625b1` | 5 (3 docs/proofs, 2 workflow/gitignore) |
| Frontend runtime changed | No |
| Backend runtime changed | No |
| Database schema changed | No |
| Workflow changed | Yes (persistent tracking, health-gated rotation) |
| Docker Compose/prod config changed | No |
| Final HEAD deployed | Yes (deployed and verified green) |

## Runtime Health

- Frontend: ✅ HTTP 200
- Backend health: ✅ HTTP 200
- All 4 Docker containers: healthy (frontend, backend, caddy, postgres)
- No restart loops
- No unexpected 5xx errors

## Verification

- ✅ Persistent commit tracking: ACTIVE
- ✅ current_commit: `d2c7ea3` (deployed and health-checked)
- ✅ previous_commit: `2b625b1` (distinct from current)
- ✅ pending_commit: absent (clean after successful deploy)
- ✅ Atomic file writes: confirmed (`mktemp` + `mv`)
- ✅ Current updated only after health pass
- ✅ Failed deploy preserves current/previous
- ✅ Rollback dry-run: PASSED (target: `2b625b1`)
- ✅ Rollback target resolvable, distinct, with health checks planned
- ✅ Git clean: empty `git status --porcelain`
- ✅ HEAD reconciled: docs/proof-only after deployed commit
- ✅ Final HEAD deployed and verified green

## Fast Path

- Focused checks only: git, SSH, Docker, HTTP, rollback dry-run
- Full local backend runs: 0
- Full local frontend runs: 0
- Browser E2E runs: 0
- Provider calls: 0
- Redundant runs: 0

## Proof

- Proof JSON: `docs/proofs/proof_trainer_platform_vps_staging_closeout_009b.json`
- Layer 009 proof: `docs/proofs/proof_trainer_platform_vps_staging_deployment_009.json`
- Layer 009A proof: `docs/proofs/proof_trainer_platform_vps_staging_cicd_execution_closeout_009a.json`
