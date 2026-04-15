from fastapi import APIRouter, FastAPI

app = FastAPI(title="Orbis API", version="0.1.0")

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "api"}


@app.get("/health", tags=["health"])
def root_health_check() -> dict[str, str]:
    return {"status": "ok", "service": "api"}


app.include_router(api_router)
