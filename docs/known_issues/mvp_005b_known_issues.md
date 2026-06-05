# Known Issues — MVP-005B Railway Redeploy and Progress Resmoke

## 1. Progress Update Not Active on Railway

**Status**: OPEN

**Component**: Railway deployment

**Description**: The progress-update-after-evaluation fix (committed in `d27b537`) is verified in code and backend tests pass, but Railway external staging still runs pre-fix code. Progress shows `total_attempts=0` after evaluation completes successfully.

**Root cause**: Railway deployment is stale — needs manual redeploy from latest `master`.

**Workaround**: None. Requires Railway CLI operator to run `railway up --service backend -e staging --detach` after authentication.

**Verification method**: Run `scripts/railway_smoke_test_mvp005.sh` after redeploy. Step 15 (Progress) should show `total_attempts >= 1` and `average_score > 0`.

**Impact**: Blocks MVP-005 final acceptance. Progress feature gap persists on external staging despite being code-verified.

---

## 2. Railway CLI Authentication Unavailable

**Status**: OPEN

**Component**: Infrastructure

**Description**: The `RAILWAY_TOKEN` in `.env.railway.local` is a project-scoped deployment token, not a user API token. `railway login` requires an interactive terminal. The Railway GraphQL API cannot be used to trigger deployments without a user token.

**Impact**: Cannot trigger Railway redeploy from non-interactive environment.

**Workaround**: Operator runs `railway login` interactively, then `railway up --service backend -e staging --detach`.

---

## 3. Railway GitHub Auto-Deploy Not Verified

**Status**: UNKNOWN

**Component**: Infrastructure

**Description**: An empty commit (`463d1ee`) was pushed to `origin master` to trigger Railway auto-deploy (if configured). The endpoint did not update within 10+ minutes, suggesting auto-deploy is either not configured or set to a different branch.

**Impact**: Deployments must be triggered manually via Railway CLI.

---

## 4. Frontend Build ID Unstable

**Status**: INFO

**Component**: Frontend

**Description**: The frontend build ID (`VONIBrkNEIsWlkphJtVFn`) changes on every build. This is normal Next.js behavior but means the deployed build version can't be tracked across deployments without external monitoring.

**Impact**: None. Normal behavior.

---

## 5. Admin Endpoints Return 500

**Status**: OPEN

**Component**: Backend

**Description**: Admin endpoints (`/api/v1/admin/system-health`, `/api/v1/admin/seed-status`) return HTTP 500 on Railway staging.

**Impact**: Admin monitoring unavailable on external staging. These endpoints require admin authentication that may not be configured properly for the staging environment.

**Workaround**: Use health/ready endpoints for monitoring. Admin endpoints tested locally.

---

## Mitigation Status Summary

| Issue | Severity | Status | Mitigation |
|-------|----------|--------|------------|
| Progress not on Railway | HIGH | Open | Needs operator Railway redeploy |
| Railway CLI unavailable | MEDIUM | Open | Needs interactive login |
| Auto-deploy not verified | MEDIUM | Unknown | Check Railway project settings |
| Admin endpoints 500 | LOW | Open | Use /health and /ready instead |
