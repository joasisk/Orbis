import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.db import check_db_connection
from app.core.rate_limit import SENSITIVE_POST_PATHS, InMemoryRateLimiter, is_rate_limited_endpoint

logger = logging.getLogger(__name__)
rate_limiter = InMemoryRateLimiter()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        check_db_connection()
    except RuntimeError as exc:
        logger.warning(
            "Database connectivity check failed during startup. "
            "API process will stay online to avoid proxy 502s while dependencies recover: %s",
            exc,
        )
    yield


app = FastAPI(
    title="Orbis API",
    summary="API-first backend for Orbis time and project management",
    description=(
        "Orbis provides AI-assisted project, task, and schedule orchestration for ADHD-friendly "
        "planning workflows.\n\n"
        "This OpenAPI document covers the MVP REST surface consumed by first-party and "
        "third-party clients."
    ),
    version="0.1.0",
    contact={"name": "Orbis API Team"},
    openapi_tags=[
        {
            "name": "health",
            "description": "Liveness and dependency health checks for API and orchestration layers.",
        }
    ],
    lifespan=lifespan,
)


@app.middleware("http")
async def enforce_sensitive_rate_limits(request: Request, call_next):
    if is_rate_limited_endpoint(request.url.path, request.method, SENSITIVE_POST_PATHS):
        forwarded_for = request.headers.get("x-forwarded-for", "")
        if forwarded_for:
            client_identity = forwarded_for.split(",")[0].strip()
        else:
            client_identity = request.client.host if request.client is not None else "unknown"

        allowed = rate_limiter.allow(
            key=client_identity,
            bucket=request.url.path,
            limit=settings.api_rate_limit_requests,
            window_seconds=settings.api_rate_limit_window_seconds,
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests to sensitive endpoint. Please retry later.",
                },
            )

    return await call_next(request)


@app.exception_handler(OperationalError)
async def database_operational_error_handler(_: object, exc: OperationalError) -> JSONResponse:
    logger.exception("Database operational error while processing request", exc_info=exc)
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database temporarily unavailable. Verify database connectivity and try again.",
        },
    )


@app.exception_handler(ProgrammingError)
async def database_programming_error_handler(_: object, exc: ProgrammingError) -> JSONResponse:
    logger.exception("Database programming error while processing request", exc_info=exc)
    detail = "Database query failed. Verify schema migrations are applied and try again."
    if "UndefinedTable" in str(getattr(exc, "orig", "")) or 'relation "users" does not exist' in str(exc):
        detail = "Database schema is not initialized. Run migrations (e.g., `alembic upgrade head`) and try again."
    return JSONResponse(status_code=503, content={"detail": detail})


@app.get("/health", tags=["health"])
def root_health_check() -> dict[str, str]:
    return {"status": "ok", "service": "api", "app": settings.app_name}


@app.get("/api/v1/health", tags=["health"])
def api_health_check() -> dict[str, str]:
    return {"status": "ok", "service": "api", "app": settings.app_name}


app.include_router(api_v1_router, prefix="/api/v1")
