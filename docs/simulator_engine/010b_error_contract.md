# 010B — Canonical Frontend Error Contract

## Interface

```typescript
interface AppError {
  code: string;
  message: string;
  status?: number;
  details?: Record<string, unknown>;
  correlationId?: string;
  retryable: boolean;
  fieldErrors?: Record<string, string[]>;
}
```

## Normalization Function

`normalizeApiError(error: unknown): AppError`

## Supported Backend Response Shapes

| Pattern | Example | Source |
|---------|---------|--------|
| Canonical | `{"error": {"code":"...", "message":"...", "details":{}, "request_id":"..."}}` | Backend `AppError` via `global_error_handler` |
| Detail string | `{"detail": "Error message"}` | FastAPI/Starlette default `HTTPException` handler |
| Detail object | `{"detail": {"message":"...", "code":"..."}}` | Nested error details |
| Errors array | `{"errors": [{"message":"...", "field":"..."}]}` | Validation error responses |
| Network error | `TypeError('Failed to fetch')` | Browser network failures |
| Non-JSON | Status text string | Non-JSON 500, proxy errors |
| Plain Error | `Error('message')` | Application-level errors |
| Undefined/Null | Any falsy input | Catch-all safe fallback |

## Supported Behaviors

| Requirement | Status |
|-------------|--------|
| Unknown error supported | ✅ |
| Network error supported | ✅ |
| Backend detail string supported | ✅ |
| Backend detail object supported | ✅ |
| Non-JSON response supported | ✅ |
| Correlation ID preserved where present | ✅ |
| Undefined `.message` access removed | ✅ |
| Retryable flag set from HTTP status | ✅ |
| Field errors extracted from validation errors | ✅ |

## ApiClientError

```typescript
class ApiClientError extends Error {
  code: string;
  details: Record<string, unknown>;
  requestId: string;
  status: number | undefined;
}
```

Safe construction: `new ApiClientError(undefined)` never throws. The constructor normalizes all input through `normalizeApiError()`.
