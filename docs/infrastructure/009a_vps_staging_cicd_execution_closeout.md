# VPS Staging CI/CD Execution Closeout — 009A

## Summary

Closeout of the GitHub Actions deployment workflow execution gate. The workflow
existed but its first execution failed before connecting to the VPS because the
`appleboy/ssh-action` referenced `${{ secrets.VPS_HOST }}`, `${{ secrets.VPS_USER }}`,
and `${{ secrets.VPS_PORT || 22 }}`, while only the SSH key requires secret storage.

## Root Cause

**Code**: `SECRET_NAME_MISMATCH` / `MISSING_REPOSITORY_SECRET`

The workflow's `env` block contained correct hardcoded values for host
(`152.53.227.37`), user (`trainer`), and port (`22`), but the `appleboy/ssh-action`
step referenced them as GitHub Actions secrets (`secrets.VPS_HOST`, `secrets.VPS_USER`,
`secrets.VPS_PORT || 22`) which were never configured.

## Fix Applied

Three changes to `.github/workflows/deploy-staging.yml`:

1. **Changed** `host: ${{ secrets.VPS_HOST }}` → `${{ env.VPS_HOST }}`
2. **Changed** `username: ${{ secrets.VPS_USER }}` → `${{ env.VPS_USER }}`
3. **Changed** `port: ${{ secrets.VPS_PORT || 22 }}` → `${{ env.VPS_PORT }}`
4. **Kept** `key: ${{ secrets.VPS_SSH_KEY }}` (the only truly secret value)
5. **Added** `Validate deployment secrets` preflight step before SSH
6. **Fixed** commit recording to capture SHA from repo directory (not deploy dir)

## Secrets Required

| Secret        | Source        | Notes                                    |
|---------------|---------------|------------------------------------------|
| VPS_SSH_KEY   | Repository    | SSH private key for `trainer@152.53.227.37` |

## Verification

- ✅ SSH key authentication: PASSED
- ✅ Host key verified: YES (ed25519)
- ✅ GitHub Actions run: GREEN (run #27195360143)
- ✅ Deploy via SSH: PASSED
- ✅ Health check: PASSED
- ✅ Exact commit deployed: 2b625b11ef970aecf5da266a0907d87480521625
- ✅ Docker Compose: HEALTHY (all 4 services: frontend, backend, caddy, postgres)
- ✅ Rollback readiness: VERIFIED
- ✅ Runtime code unchanged (workflow-only changes)

## Final Run Details

- Run #6: id `27195360143`, commit `2b625b1`
- All steps green: checkout → record commit → validate secrets → SSH deploy → health check → notify
- URL: <https://github.com/solomonczyk/trainer-platform/actions/runs/27195360143>

## Proof

- Proof JSON: `docs/proofs/proof_trainer_platform_vps_staging_cicd_execution_closeout_009a.json`
- Layer 009 proof: `docs/proofs/proof_trainer_platform_vps_staging_deployment_009.json`
