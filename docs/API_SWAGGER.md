# API Swagger Documentation

Orbis API exposes an OpenAPI schema and an interactive Swagger UI directly from the FastAPI app.

## Endpoints

- Swagger UI: `/docs`
- ReDoc UI: `/redoc`
- OpenAPI schema JSON: `/openapi.json`

## View Swagger in local Docker environment

1. Start the stack:
   ```bash
   docker compose up --build
   ```
2. Open Swagger UI in your browser:
   - Through the reverse proxy: `http://localhost/docs`
3. Optional direct API container access (if you expose API port directly):
   - `http://localhost:8000/docs`

## View Swagger when running API directly

1. Run API from `apps/api` (example):
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
2. Open:
   - `http://localhost:8000/docs`

## Notes

- Swagger UI reflects current request/response models and validation rules defined in FastAPI routes and Pydantic schemas.
- Use the **Authorize** button in Swagger UI for secured endpoints when authentication is enabled for those routes.
