"""Error handling and custom exceptions."""

from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.core.config import settings


class AppError(HTTPException):
    """Base application error with structured response."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict | None = None,
    ):
        self.code = code
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)

    def to_dict(self, request_id: str = "") -> dict:
        return {
            "error": {
                "code": self.code,
                "message": self.detail,
                "details": self.details,
                "request_id": request_id,
            }
        }


class NotFoundError(AppError):
    def __init__(self, entity: str = "Resource", entity_id: str = ""):
        # Avoid double "not found" when entity already ends with it
        suffix = " not found"
        if entity.lower().rstrip(".").endswith(suffix):
            msg = entity + (f": {entity_id}" if entity_id else "")
            code_entity = entity[: -len(suffix)] or "Resource"
        else:
            msg = f"{entity}{suffix}" + (f": {entity_id}" if entity_id else "")
            code_entity = entity
        super().__init__(
            code=f"{code_entity.upper().replace(' ', '_')}_NOT_FOUND",
            message=msg,
            status_code=404,
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "Access denied"):
        super().__init__(code="FORBIDDEN", message=message, status_code=403)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(code="CONFLICT", message=message, status_code=409)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed", details: dict | None = None):
        super().__init__(code="VALIDATION_ERROR", message=message, status_code=422, details=details or {})


async def global_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler that formats all errors consistently."""
    request_id = getattr(request.state, "request_id", "")
    if isinstance(exc, AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(request_id=request_id),
        )
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail,
                    "details": {},
                    "request_id": request_id,
                }
            },
        )
    if settings.debug:
        raise exc
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "details": {},
                "request_id": request_id,
            }
        },
    )
