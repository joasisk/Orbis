import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.db import check_db_connection

logger = logging.getLogger(__name__)


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


app = FastAPI(title="Orbis API", version="0.1.0", lifespan=lifespan)


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
