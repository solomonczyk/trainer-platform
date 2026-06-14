"""FastAPI application entry point."""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.errors import global_error_handler
from app.core.rate_limiter import RateLimitMiddleware
from app.db.session import engine
from app.db.base import Base

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup/shutdown."""
    configure_logging()
    logger.info("Starting Trainer Platform API", version=settings.app_version)
    # Create tables if not exist (for dev/test convenience)
    if settings.app_env == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    logger.info("Trainer Platform API stopped")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS — support comma-separated origins from env (e.g. "http://localhost:3000,http://localhost:8080")
_cors_origins = [o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip()]
if settings.frontend_url not in _cors_origins:
    _cors_origins.append(settings.frontend_url)
# Always include localhost for dev/staging
for local_dev in ("http://localhost:3000", "http://localhost:8000"):
    if local_dev not in _cors_origins:
        _cors_origins.append(local_dev)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (disabled by default in development)
app.add_middleware(RateLimitMiddleware)

# Global error handler — covers Exception and HTTPException
app.exception_handler(Exception)(global_error_handler)
app.exception_handler(HTTPException)(global_error_handler)


# Middleware: request_id
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get(settings.request_id_header, str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers[settings.request_id_header] = request_id
    return response


# ---------------------------------------------------------------------------
# Health / Ready
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


@app.get("/ready")
async def ready():
    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"
    return {"status": "ok" if db_status == "ok" else "degraded", "database": db_status}


# ---------------------------------------------------------------------------
# Register Routers
# ---------------------------------------------------------------------------

from app.modules.auth import router as auth_router
from app.modules.users import router as users_router
from app.modules.domains import router as domains_router
from app.modules.trainers import router as trainers_router
from app.modules.scenarios import router as scenarios_router
from app.modules.runtime import router as runtime_router
from app.modules.evaluations import router as evaluations_router
from app.modules.progress import router as progress_router
from app.modules.analytics import router as analytics_router
from app.modules.activities import router as activities_router
from app.modules.admin import router as admin_router
from app.modules.quests.router import router as quests_router

# Certification-grade core routers
from app.certification_core.routers import (
    competency_router,
    blueprint_router,
    knowledge_source_router,
    item_family_router,
    item_router,
    rubric_router,
    domain_pack_router,
    audit_router,
    transition_router,
)

# Dynamic Item Bank Runtime routers
from app.certification_core.routers.item_bank_runtime_router import router as item_bank_runtime_router

# Controlled Generation router
from app.certification_core.routers.generation_router import router as generation_router

# Human Review router
from app.certification_core.routers.human_review_router import router as human_review_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
app.include_router(domains_router, prefix="/api/v1", tags=["Domains"])
app.include_router(trainers_router, prefix="/api/v1", tags=["Trainers"])
app.include_router(scenarios_router, prefix="/api/v1", tags=["Scenarios"])
app.include_router(runtime_router, prefix="/api/v1", tags=["Runtime"])
app.include_router(evaluations_router, prefix="/api/v1", tags=["Evaluations"])
app.include_router(progress_router, prefix="/api/v1", tags=["Progress"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(activities_router, prefix="/api/v1", tags=["Activities"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(quests_router, prefix="/api/v1", tags=["Quests"])

# Certification-grade core routes
app.include_router(competency_router, prefix="/api/v1", tags=["Certification-Core"])
app.include_router(blueprint_router, prefix="/api/v1", tags=["Certification-Core"])
app.include_router(knowledge_source_router, prefix="/api/v1", tags=["Certification-Core"])
app.include_router(item_family_router, prefix="/api/v1", tags=["Certification-Core"])
app.include_router(item_router, prefix="/api/v1", tags=["Certification-Core"])
app.include_router(rubric_router, prefix="/api/v1", tags=["Certification-Core"])
app.include_router(domain_pack_router, prefix="/api/v1", tags=["Certification-Core"])
app.include_router(audit_router, prefix="/api/v1", tags=["Certification-Core"])
app.include_router(transition_router, prefix="/api/v1", tags=["Certification-Core"])

# Dynamic Item Bank Runtime routes
app.include_router(
    item_bank_runtime_router,
    prefix="/api/v1",
    tags=["Certification-Core-Item-Bank"],
)

# Controlled Generation routes
app.include_router(
    generation_router,
    tags=["Certification-Generation"],
)

# Human Review routes
app.include_router(
    human_review_router,
    tags=["Certification-Human-Review"],
)


# ---------------------------------------------------------------------------
# OpenAPI export at runtime
# ---------------------------------------------------------------------------

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    return app.openapi()
