# Auth Identity Fix — 2026-06-15

## Problem
AUTH_SESSION_IDENTITY_MISMATCH: Header showed different user than verify-email session bar.
Multiple operators registered, tokens consumed before human could click.

## Root Causes Identified

### 1. No canonical auth source (critical)
- Header and verify-email each independently fetched `/api/v1/me` into local useState
- After `setToken()` replaced JWT, Header was never notified → stale identity
- 6 components each managed their own UserResponse state independently

### 2. Gmail/network bot consumes tokens
- Something on user's network (IP 77.243.31.189) POSTs to `/api/v1/auth/verify-email` within seconds of email delivery
- Token consumed before human operator can click the link

## Changes Made

### Frontend: Canonical AuthContext (`frontend/src/lib/auth/AuthContext.tsx`)
- Single React Context as source of truth for user identity
- `useAuth()` hook → `{ user, loading, refresh, clearSession }`
- Listens for `auth-changed` custom event, auto-refreshes
- Header now reads from `useAuth()` instead of local state
- verify-email session bar reads from same `useAuth()`

### Frontend: `setToken()` / `clearToken()` dispatch `auth-changed`
- Any JWT change auto-notifies all components
- Guarantees Header user === SessionBar user

### Frontend: Manual verification (anti-bot)
- `/verify-email?token=...` no longer auto-verifies on page load
- Shows "ready" state with "Verify Email" button
- User must click button to trigger POST
- Blocks Gmail link preview bots from consuming tokens

### Backend: verify-email requires authentication
- `POST /api/v1/auth/verify-email` now requires JWT
- Validates token belongs to authenticated user (`user.id == owner_user_id`)
- Returns 403 ForbiddenError if token belongs to different account
- Bots without JWT cannot consume tokens

### Staging-only debug bar
- SessionBar on verify-email page only visible when `NEXT_PUBLIC_APP_ENV !== "production"`
- Shows current user email + verified status
- "Clear" button to wipe stale session

## Files Changed
- `frontend/src/lib/auth/AuthContext.tsx` — NEW: canonical auth context
- `frontend/src/app/layout.tsx` — wrap with AuthProvider
- `frontend/src/components/layout/Header.tsx` — use useAuth()
- `frontend/src/app/verify-email/page.tsx` — useAuth() + manual verify + SessionBar
- `frontend/src/lib/api/client.ts` — setToken/clearToken dispatch auth-changed; verifyEmail no skipAuth
- `backend/app/modules/auth/router.py` — verify-email requires auth
- `backend/app/modules/auth/service.py` — verify_email validates token ownership
- `backend/app/modules/auth/schemas.py` — VerifyEmailResponse includes email

## Remaining
- [ ] Update tests in `test_email_verification.py` to pass auth headers on verify-email calls
- [ ] Push to GitHub
- [ ] Deploy backend to VPS
- [ ] Run final clean browser proof with operator registering via browser
- [ ] Verify: header === session bar, /me email_verified=true, /domains=200, /quests=200
- [ ] Update proof JSON
