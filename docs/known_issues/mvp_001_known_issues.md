# MVP-001 Known Issues

## Critical
None open.

## High
1. **Frontend tests not yet configured** — Vitest setup needs to be completed for proper frontend test runs.
2. **Real OpenAI provider not configured** — AI evaluation uses mock provider; real provider needs API key setup.
3. **CI pipeline not defined** — No GitHub Actions or similar CI configuration yet.

## Medium
4. **Rate limiting not implemented** — No rate limiting on API endpoints; needed for production.
5. **SQLite used for tests** — Test database uses SQLite instead of PostgreSQL; some Postgres-specific features not tested.
6. **No password strength requirements** — Password validation is minimal (min 8 chars).
7. **Admin API key not enforced** — Admin API key defined but not used; admin routes rely on JWT role only.
8. **Email verification not implemented** — Users can register without email verification.

## Low
9. **Mobile responsiveness needs review** — Basic responsive design implemented but not fully tested on all devices.
10. **Accessibility audit not performed** — Basic accessibility patterns used but no formal audit.
11. **No error tracking integration** — Errors are logged but no external error tracking (Sentry, etc.) configured.
12. **No backup/restore scripts** — Database backup procedures not automated.
13. **No monitoring/alerting** — No production monitoring configured.

## Accepted for MVP
- Mock AI provider instead of real LLM
- SQLite for tests instead of PostgreSQL
- No email verification
- No password reset flow
- Minimal admin dashboard
- Basic analytics without visualization
