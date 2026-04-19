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

## Getting started
- Usage guide: [`docs/USAGE.md`](docs/USAGE.md)
- Development setup: [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)
- API docs workflow details: [`docs/API_SWAGGER.md`](docs/API_SWAGGER.md)

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

### Usage and operations
- Usage guide: [`docs/USAGE.md`](docs/USAGE.md)
- TrueNAS setup guide: [`docs/TRUENAS_SETUP.md`](docs/TRUENAS_SETUP.md)
- Local/prod hardening runbook: [`docs/PHASE7_HARDENING_AND_TRUENAS.md`](docs/PHASE7_HARDENING_AND_TRUENAS.md)

### Development
- Development setup and checks: [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)
- Roadmap/issues planning: [`docs/GITHUB_ISSUES_ROADMAP.md`](docs/GITHUB_ISSUES_ROADMAP.md)
- AI contributor workflow: [`docs/AI_AGENT_GUIDE.md`](docs/AI_AGENT_GUIDE.md)

### SDK
- Python SDK docs: [`sdk/python/README.md`](sdk/python/README.md)
- Phase 8 SDK plan: [`docs/PHASE8_PUBLIC_SDK.md`](docs/PHASE8_PUBLIC_SDK.md)

## Development quality checks
See [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).

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
