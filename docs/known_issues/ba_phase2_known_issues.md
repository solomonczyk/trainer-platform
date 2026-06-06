# BA Phase 2 Known Issues

## Active Issues

### 1. Railway Deployment Infrastructure Limitation
**Status**: OPEN
**Impact**: Medium

The Railway deployment infrastructure prevents automatic deployment of the latest backend code. The Phase 2 backend changes (seed script, retry policy, analytics events) require a manual reseed via the admin API after deployment or local backend against Railway DB.

**Workaround**: 
- Backend: Run `POST /api/v1/admin/seed/ba-trainer-phase2` after deployment
- Use local backend against Railway PostgreSQL DB for testing

### 2. Real DeepSeek Evaluation Requires API Key
**Status**: OPEN
**Impact**: Medium

Real DeepSeek evaluation requires `DEEPSEEK_API_KEY` to be configured. Without it, evaluation falls back to mock provider. This is the same limitation as Phase 1.

**Workaround**: Set `AI_GATEWAY_PROVIDER=deepseek` and `DEEPSEEK_API_KEY=<key>` in Railway environment variables.

### 3. Phase 2 Scenarios Need Re-seed on Fresh DB
**Status**: OPEN
**Impact**: Low

Phase 2 scenarios are seeded via admin API (`POST /api/v1/admin/seed/ba-trainer-phase2`) and are not part of Alembic migrations. A fresh database requires explicit seeding.

**Workaround**: Run the seed endpoint after any DB reset.

### 4. Frontend Routes Require Rebuild
**Status**: OPEN
**Impact**: Low

The new Phase 2 frontend routes (`/trainers/[slug]/phase2` and `/trainers/[slug]/phase2/[scenarioId]`) are part of the Next.js build. A rebuild is required after updating the frontend code.

## Resolved Issues

### 5. Raw i18n Keys Visible in Scenario Pages (Phase 1 Carryover)
**Status**: RESOLVED
**Resolution**: All `scenario.title_key` references now properly go through `t()` translation function with fallback to the key itself.

## Non-Issues

- **Phase 2 and Phase 1 co-existence**: Fully compatible. Phase 1 uses Activity model, Phase 2 uses Scenario model. No conflicts.
- **Cross-user isolation**: Phase 2 scenarios use existing Scenario runtime which has per-user session/attempt isolation.
- **Progress tracking**: Phase 2 uses existing ProgressService which handles scenario-based evaluations.
