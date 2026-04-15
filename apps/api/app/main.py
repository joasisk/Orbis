import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

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


@app.get("/health", tags=["health"])
def root_health_check() -> dict[str, str]:
    return {"status": "ok", "service": "api", "app": settings.app_name}


@app.get("/api/v1/health", tags=["health"])
def api_health_check() -> dict[str, str]:
    return {"status": "ok", "service": "api", "app": settings.app_name}


app.include_router(api_v1_router, prefix="/api/v1")
