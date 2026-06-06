# Frontend Staging API Build Contract Fix Report

## Layer

TRAINER-PLATFORM-MVP-007B-FIX-FRONTEND-STAGING-API-BUILD-CONTRACT

## Date

2026-06-06

## Root Cause

The deployed Railway frontend bundle contained `http://localhost:8000` as the
API base URL because:

1. **Missing Docker build ARGs**: The `frontend/Dockerfile` did not accept
   `NEXT_PUBLIC_API_URL` (or the new canonical `NEXT_PUBLIC_API_BASE_URL`) as a
   Docker build argument. Next.js inlines `NEXT_PUBLIC_*` env vars at build time,
   but the Docker build had no way to receive them.

2. **Duplicated env resolver in `next.config.js`**: The file contained an
   independent `getApiBaseUrl()` function that fell back to `http://localhost:8000`
   when no env var was set. This function was also used in an `env` block that
   **hardcoded the resolved value into every bundle at build time**.

3. **Stale `railway.json` buildArgs**: The `railway.json` build args referenced
   `NEXT_PUBLIC_API_URL: https://backend.up.railway.app` which was both the wrong
   URL (generic, not staging-specific) and ineffective because the Dockerfile
   never consumed build args.

## Changes Made

### 1. Canonical API Base URL Variable

**File**: `frontend/src/lib/api/client.ts`

- Migrated canonical env var from `NEXT_PUBLIC_API_URL` → `NEXT_PUBLIC_API_BASE_URL`
- Backward-compatible fallback to `NEXT_PUBLIC_API_URL` if `NEXT_PUBLIC_API_BASE_URL` is unset
- Development mode (`APP_ENV=development` or unset) → localhost fallback allowed
- Staging/production with missing URL → returns empty string (fails loudly)

### 2. Removed Duplicated Env Logic from next.config.js

**File**: `frontend/next.config.js`

- Removed entire `getApiBaseUrl()` function (duplicated from client.ts)
- Removed `async rewrites()` that used the duplicated resolver
- Removed `env: { NEXT_PUBLIC_API_URL: getApiBaseUrl() }` block that hardcoded localhost
- Config is now clean: only `output: 'standalone'` and `images` configuration

### 3. Docker Build ARGs

**File**: `frontend/Dockerfile`

Added before `npm run build`:

```dockerfile
ARG NEXT_PUBLIC_API_BASE_URL
ARG NEXT_PUBLIC_APP_ENV
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_APP_ENV=$NEXT_PUBLIC_APP_ENV
```

### 4. Railway Build Config

**File**: `railway.json`

Updated buildArgs:

```json
"buildArgs": {
  "NEXT_PUBLIC_API_BASE_URL": "https://backend-staging-0487.up.railway.app",
  "NEXT_PUBLIC_APP_ENV": "staging"
}
```

### 5. Tests

**File**: `frontend/src/tests/api-client.test.ts`

- Renamed all `NEXT_PUBLIC_API_URL` → `NEXT_PUBLIC_API_BASE_URL`
- Added backward-compat tests for `NEXT_PUBLIC_API_URL`
- Added staging/production never-localhost guarantees
- Added register/login endpoint resolution tests
- Total: 17 API client tests, all passing

## Verification

| Check | Result |
|-------|--------|
| Local build (`npm run build`) | ✅ Passed |
| Tests (`vitest run`) | ✅ 17/17 passed |
| Bundle scan for `localhost:8000` | ✅ 0 references |
| Bundle contains staging backend URL | ✅ Verified |
| Railway redeploy | ✅ Completed |
| Registration from browser | ✅ POST to `backend-staging-0487.up.railway.app` → 201 |
| Login from browser | ✅ POST to `backend-staging-0487.up.railway.app` → 200 |
| Domain catalog | ✅ Loads from external backend |
| Trainer page | ✅ Loads from external backend |
| Localhost requests observed | ✅ None |

## Security

| Check | Result |
|-------|--------|
| Provider secrets in frontend | ✅ None |
| DeepSeek key exposed | ✅ No |
| OpenAI enabled | ✅ No |
| Production accepted | ✅ false |
| Release allowed | ✅ false |

## Git

| Check | Result |
|-------|--------|
| Branch | `master` |
| Commit | `7e5d2da` |
| Pushed | ✅ Yes |
| Clean | ✅ Yes |
