# Railway Root Directory Fix Report - MVP-005B

## Layer
TRAINER-PLATFORM-MVP-005B-FIX-RAILWAY-ROOT-DIRECTORY-AND-REDEPLOY

## Date
2026-06-05

## Objective
Fix Railway service build configuration so backend and frontend are built from correct root directories, redeploy both services, and verify progress on Railway external staging.

## Root Cause Analysis

### Build Failure Observation
Railway build logs previously showed:
- "Nixpacks was unable to generate a build plan for this app."
- Build attempted from repository root, listing `railway.json`, `docker-compose.staging.yml`, `README.md`, `Makefile`, `backend/`, `frontend/`, etc.

The global `build.builder` field in `railway.json` was set to `NIXPACKS`:

```json
{
  "build": {
    "builder": "NIXPACKS",
    "nixpacksConfigPath": ""
  }
}
```

When `railway up` was run from the repo root, Railway applied the global Nixpacks builder against the entire repository, which has no root-level build configuration. The per-service `build.builder` (`DOCKERFILE`) was not activated.

### railway.json Configuration
The `railway.json` already had correct service-level root directories:

```json
{
  "services": [
    {
      "name": "backend",
      "root": "backend",
      "build": { "builder": "DOCKERFILE", "dockerfilePath": "Dockerfile" }
    },
    {
      "name": "frontend",
      "root": "frontend",
      "build": { "builder": "DOCKERFILE", "dockerfilePath": "Dockerfile" }
    }
  ]
}
```

However, the service-level `root` field is only effective when deploying via `railway up` with the `--path-as-root` flag, or when the service has a connected GitHub source. For upload-based deployments, the working directory at invocation time plus the `--path-as-root` flag determines the build context.

### Fix Applied
Both services were deployed using:

```bash
# From backend/ directory:
railway up . --path-as-root --service backend --environment staging --detach --json

# From frontend/ directory:
railway up . --path-as-root --service frontend --environment staging --detach --json
```

This ensures the build archive contains only the service directory's contents, with the correct root for Dockerfile resolution.

## Deployment Results

| Service | Deployment ID | Status | Method |
|---------|--------------|--------|--------|
| Backend | `a48cd8e6-b7db-424d-80fe-691f57f5612b` | SUCCESS | `railway up` from `backend/` |
| Frontend | `39c27d96-45e1-4db9-841b-dc2ef72cdaab` | SUCCESS | `railway up` from `frontend/` |

## External Health Checks

| Check | URL | Result |
|-------|-----|--------|
| Backend Health | `https://backend-staging-0487.up.railway.app/health` | `{"status":"ok","app":"TrainerPlatform","version":"0.1.0"}` |
| Backend Ready | `https://backend-staging-0487.up.railway.app/ready` | `{"status":"ok","database":"ok"}` |
| OpenAPI | `https://backend-staging-0487.up.railway.app/openapi.json` | HTTP 200, 24 paths |
| Frontend | `https://frontend-staging-4146.up.railway.app` | HTTP 200 |

## Summary

The Railway build root directory issue was addressed by deploying from the correct service directories with the `--path-as-root` flag. The `railway.json` configuration was reviewed and confirmed to have correct service-level root directory settings. Both services redeployed successfully on Railway staging.

## Verdict

```json
{
  "railway_build_root_fixed": true,
  "backend_root_directory": "backend",
  "frontend_root_directory": "frontend",
  "backend_redeployed": true,
  "frontend_redeployed": true,
  "backend_deployment_success": true,
  "frontend_deployment_success": true,
  "next_allowed_action": "real_openai_staging_gate"
}
```
