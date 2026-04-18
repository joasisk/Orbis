# Orbis

Self-hosted, AI-assisted time and project management system optimized for ADHD users.

## Stack
- Frontend: Next.js
- Backend API: FastAPI
- Database: PostgreSQL
- Queue/Cache: Redis
- Reverse proxy: Caddy
- Deployment: Docker Compose / TrueNAS Custom App compatible layout

## What's in this repo
- `docs/` project requirements, architecture, data models, implementation plan, AI agent guidance
- `apps/api/` FastAPI bootstrap with health endpoints and worker entrypoint
- `apps/web/` Next.js bootstrap with home page and health route
- `infra/` local deployment and reverse proxy config
- `docker-compose.yml` local orchestration starter

## Quick start
1. Copy environment file:
   ```bash
   cp .env.example .env
   ```
2. Start local services:
   ```bash
   docker compose up --build
   ```
3. Verify health checks:
   - API: `http://localhost/api/v1/health`
   - Web: `http://localhost/api/health`
4. Open API docs (Swagger UI):
   - `http://localhost/docs`

For full Swagger/OpenAPI usage instructions, see `docs/API_SWAGGER.md`.

## Initial development order
1. Bring up local infra
2. Implement authentication and core task/project models
3. Build web shell and login
4. Add weekly planning, reminders, and focus mode

See `docs/IMPLEMENTATION_PLAN.md`, `docs/REQUIREMENTS.md`, and `docs/DATA_MODELS.md`.


## Quality checks
### API (Python)
```bash
cd apps/api
pip install -r requirements.txt
ruff check app tests
ruff format --check app tests
```

### Web (Next.js)
```bash
cd apps/web
npm ci
npm run lint
npm run typecheck
```

## Architecture decisions
ADR records are stored under `docs/adr/`.

## Troubleshooting
- **Proxy returns `502 Bad Gateway` for `/api/*` in local dev**
  - Verify the API container is running and healthy:
    ```bash
    docker compose ps
    docker compose logs api --tail=200
    ```
  - Compose now provides safe defaults for required API/DB env vars, but a stale DB volume with mismatched credentials can still prevent startup.
  - If credentials changed, reset local data:
    ```bash
    docker compose down -v
    docker compose up --build
    ```

- **API fails at startup with `password authentication failed for user "orbis"`**
  - If Postgres data already exists, changing `POSTGRES_PASSWORD` in `.env` does not update the existing DB user password.
  - Ensure `.env` credentials match the values used when the `postgres_data` volume was first initialized, or reset local data and recreate containers:
    ```bash
    docker compose down -v
    docker compose up --build
    ```
