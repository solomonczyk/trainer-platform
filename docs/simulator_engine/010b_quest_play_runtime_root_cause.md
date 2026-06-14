# 010B — Quest Play Browser Runtime Root Cause Analysis

## Summary

The Quest Play page crashed with `Cannot read properties of undefined (reading 'message')` when the backend returned error responses in a format the frontend API client did not expect.

## Root Cause

### File
`frontend/src/lib/api/client.ts`

### Expression
Line 69 (pre-fix): `super(err.message)` inside `ApiClientError` constructor
Reached from Line 121: `throw new ApiClientError(errorData.error)`

### Chain of Events

1. **Backend returns FastAPI/Starlette default error format**
   When the backend raises `HTTPException` (or any subclass like `AppError`), Starlette's default exception handler intercepts it (because our custom `global_error_handler` was registered only for `Exception`, not `HTTPException` specifically) and returns:
   ```json
   {"detail": "Error message text"}
   ```

2. **Frontend expects canonical format**
   The `request()` function in `client.ts` expected the backend to always return:
   ```json
   {"error": {"code": "...", "message": "...", "details": {}, "request_id": "..."}}
   ```

3. **Undefined access**
   When the response was `{"detail": "Quest not found"}`, `errorData.error` evaluated to `undefined`. Then:
   ```
   new ApiClientError(undefined)
     → constructor(err: ApiError["error"]) { super(err.message); ... }
     → super(undefined.message)
     → TypeError: Cannot read properties of undefined (reading 'message')
   ```

4. **Error propagation**
   TanStack Query's `useMutation`/`useQuery` caught the TypeError and passed it to `onError` handlers, which displayed `err.message` (the confusing TypeError string) in the error UI.

### Actual Values

| Variable | Expected Type | Actual Value |
|----------|--------------|--------------|
| `errorData` | `{ error: { code, message, ... } }` | `{ detail: "Quest not found" }` |
| `errorData.error` | `{ code, message, ... }` | `undefined` |
| `err` (ApiClientError constructor) | `ApiError["error"]` | `undefined` |
| `err.message` | `string` | TypeError thrown |

### Contract Owner

**BOTH** — the defect spans the frontend-to-backend error contract:
- **Backend**: The `global_error_handler` was registered only for `Exception`, not `HTTPException`. Starlette's default handler for `HTTPException` returned `{"detail": ...}` format instead of the canonical `{"error": {...}}` format.
- **Frontend**: The `request()` function assumed a single error response format with no normalization or fallback. The `ApiClientError` constructor had no guard against `undefined`/`null` input.

### Why Previous Tests Missed It

- The API-level tests (`focused_backend_passed: 84`) tested backend-internal contracts and did not verify the error response format reaching the browser.
- The frontend tests did not include error normalization or error-state rendering tests.
- The frontend used `error instanceof Error ? err.message : fallback` patterns that were individually safe but did not prevent the confusing TypeError message from reaching the user.
- There was no browser-level regression test for the Quest Play page error states.

## Fix

1. **Canonical Error Model**: Added `normalizeApiError()` function supporting all backend error shapes.
2. **Safe ApiClientError**: Constructor now uses `normalizeApiError()` instead of direct `.message` access.
3. **Backend handler registration**: Added `app.exception_handler(HTTPException)(global_error_handler)` for consistent error format.
4. **25 unit tests + 16 rendering tests**: Cover all error contract variants.
5. **6 browser tests**: Cover QA/BA quest catalog loading, quest opening, legacy URL verification.
