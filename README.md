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
- `apps/api/` backend skeleton
- `apps/web/` frontend skeleton
- `infra/` local deployment and reverse proxy config
- `docker-compose.yml` local orchestration starter

## Initial development order
1. Bring up local infra
2. Implement authentication and core task/project models
3. Build web shell and login
4. Add weekly planning, reminders, and focus mode

See `docs/IMPLEMENTATION_PLAN.md` and `docs/REQUIREMENTS.md`.
