# Known Issues — 009

## Runtime

1. **Frontend double `/api` routing**: The initial build used
   `NEXT_PUBLIC_API_BASE_URL=https://.../api` while all API paths already
   include the `/api/v1/` prefix. Fixed by rebuilding with
   `NEXT_PUBLIC_API_BASE_URL=https://...` (no suffix).

2. **Internal network DNS**: The Docker `internal` network with
   `internal: true` blocks external DNS resolution. The backend was added
   to the `public` network to reach DeepSeek API.

3. **`handle_path` prefix stripping**: Caddy's `handle` directive with `/*`
   suffix behaves like `handle_path` and strips the matched prefix. Fixed by
   using named route matcher `@api` instead.

4. **Health check command quoting**: Python one-liner health check commands
   need careful quoting in YAML. Fixed by using CMD (exec) format in Docker
   health checks.

## Non-Blocking

5. **BA phase2 scenarios use slug-based IDs** (e.g. `ba_phase2_*`) while QA
   scenarios use UUID-like scenario IDs. Both work correctly.

6. **The `trainer_count` localization** shows "сценарии" (scenarios) instead
   of "тренажёры" (trainers) for multiple trainers — a minor translation
   choice, not a functional issue.

## Resolved

7. **GitHub Actions SSH host empty** (Layer 009A). The `appleboy/ssh-action`
   referenced `${{ secrets.VPS_HOST }}` etc. when these are public env vars.
   Fixed by using `${{ env.VPS_HOST }}` for host, user, and port; only
   `VPS_SSH_KEY` remains as a secret. Preflight validation added.
   - Root cause: `SECRET_NAME_MISMATCH`
   - Fix: commit `222d5ba` + repository secret `VPS_SSH_KEY`

8. **`/tmp` ephemeral commit records** (Layer 009B). Previous/current deploy
   commit SHAs were stored at `/tmp/current_deployed_commit` and
   `/tmp/previous_deployed_commit`, which are ephemeral and lost on reboot.
   Fixed by migrating to persistent files at
   `/opt/trainer-platform/deploy/{current,previous,pending}_commit` with
   atomic writes and health-gated rotation.
   - Root cause: ephemeral storage
   - Fix: commit `d2c7ea3`
