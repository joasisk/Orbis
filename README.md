# Orbis

Orbis is a self-hosted, AI-assisted time and project management system designed for ADHD users.

## Mission and MVP focus
Orbis prioritizes low-friction planning, realistic scheduling, and reduced overwhelm while keeping privacy and approval controls explicit.

Before implementing features, use this project source-of-truth order:
1. [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md)
2. [`docs/MVP_PLAN.md`](docs/MVP_PLAN.md)
3. [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md)
4. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
5. ADRs in [`docs/adr/`](docs/adr/)

## Tech stack
- **Web:** Next.js (`apps/web`)
- **API:** FastAPI (`apps/api`)
- **Data:** PostgreSQL
- **Queue/cache:** Redis
- **Reverse proxy:** Caddy
- **Deployment:** Docker Compose, with TrueNAS-friendly layout

## Repository map
- [`apps/api/`](apps/api/) — API-first domain orchestration, authz, planning, workers
- [`apps/web/`](apps/web/) — presentation/UI flows and API consumption
- [`docs/`](docs/) — requirements, architecture, plans, ADRs, and operational guides
- [`infra/`](infra/) — deployment scripts and Caddy config
- [`sdk/python/`](sdk/python/) — Python SDK for external integrations
- [`docker-compose.yml`](docker-compose.yml) — local orchestration entrypoint

For a full directory guide, see [`docs/REPO_STRUCTURE.md`](docs/REPO_STRUCTURE.md).

## Quick start (local)
1. Copy environment file:
   ```bash
   cp .env.example .env
   ```
2. Start services:
   ```bash
   docker compose up --build
   ```
3. Verify health endpoints:
   - API: `http://localhost/api/v1/health`
   - Web: `http://localhost/api/health`
4. Open API docs:
   - Swagger UI: `http://localhost/docs`

For API docs workflow details, see [`docs/API_SWAGGER.md`](docs/API_SWAGGER.md).

## Key documentation
### Product and planning
- Requirements: [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md)
- MVP phases: [`docs/MVP_PLAN.md`](docs/MVP_PLAN.md)
- Implementation sequencing: [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md)
- Current status draft: [`docs/CURRENT_STATUS_PROGRESS_DRAFT.md`](docs/CURRENT_STATUS_PROGRESS_DRAFT.md)

### Architecture and data
- Architecture baseline: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Data models: [`docs/DATA_MODELS.md`](docs/DATA_MODELS.md)
- API strategy: [`docs/API_STRATEGY.md`](docs/API_STRATEGY.md)
- ADR index: [`docs/adr/`](docs/adr/)

### Delivery and operations
- Local/prod hardening + TrueNAS: [`docs/PHASE7_HARDENING_AND_TRUENAS.md`](docs/PHASE7_HARDENING_AND_TRUENAS.md)
- Roadmap/issues planning: [`docs/GITHUB_ISSUES_ROADMAP.md`](docs/GITHUB_ISSUES_ROADMAP.md)
- AI contributor workflow: [`docs/AI_AGENT_GUIDE.md`](docs/AI_AGENT_GUIDE.md)

### SDK
- Python SDK docs: [`sdk/python/README.md`](sdk/python/README.md)
- Phase 8 SDK plan: [`docs/PHASE8_PUBLIC_SDK.md`](docs/PHASE8_PUBLIC_SDK.md)

## Development quality checks
### API
```bash
cd apps/api
pip install -r requirements.txt
ruff check app tests
ruff format --check app tests
```

### Web
```bash
cd apps/web
npm ci
npm run lint
npm run typecheck
```

## Troubleshooting
- **`502 Bad Gateway` on `/api/*` in local dev**
  ```bash
  docker compose ps
  docker compose logs api --tail=200
  ```
  If local credentials/volumes are stale, reset and recreate:
  ```bash
  docker compose down -v
  docker compose up --build
  ```

- **Postgres auth error (`password authentication failed for user "orbis"`)**
  Existing Postgres volumes retain original credentials. Keep `.env` aligned with initialized values, or reset local data:
  ```bash
  docker compose down -v
  docker compose up --build
  ```

## Phase 7 hardening baseline
- Sensitive auth endpoint rate limiting via `API_RATE_LIMIT_REQUESTS` and `API_RATE_LIMIT_WINDOW_SECONDS`
- Owner-managed API keys at `/api/v1/api-keys` (`X-API-Key` header)
- Backup/restore scripts:
  - [`infra/scripts/backup.sh`](infra/scripts/backup.sh)
  - [`infra/scripts/restore.sh`](infra/scripts/restore.sh)
