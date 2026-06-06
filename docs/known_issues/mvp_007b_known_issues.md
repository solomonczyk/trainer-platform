# MVP-007B Known Issues

## Fixed

### Frontend bundle contained localhost API URL

**Status**: ✅ FIXED

The deployed Railway frontend had `http://localhost:8000` as the API base URL
because Docker build args for `NEXT_PUBLIC_API_BASE_URL` were not configured.

**Fix**: Added `ARG`/`ENV` to Dockerfile, updated `railway.json` buildArgs,
removed duplicated env resolver from `next.config.js`, and migrated to
canonical `NEXT_PUBLIC_API_BASE_URL`.

## Open / Pending

### Railway staging credentials are ephemeral

**Severity**: Low

The Railway token in `.env.railway.local` has an expiration. Future redeploys
from non-interactive environments may require token refresh.

### Railway auto-deploy not confirmed

**Severity**: Low

It is unclear whether Railway GitHub auto-deploy is configured for this project.
Manual `railway up` was used for the MVP-007B redeploy.

## Resolved Constraints

- `production_accepted`: `false` (unchanged — correct)
- `release_allowed`: `false` (unchanged — correct)
- No provider secrets in frontend bundle (confirmed)
- No OpenAI or DeepSeek configuration changes (confirmed)
