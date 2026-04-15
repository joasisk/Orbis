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
- `docs/` project requirements, architecture, implementation plan, AI agent guidance
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

## Initial development order
1. Bring up local infra
2. Implement authentication and core task/project models
3. Build web shell and login
4. Add weekly planning, reminders, and focus mode

See `docs/IMPLEMENTATION_PLAN.md` and `docs/REQUIREMENTS.md`.


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
