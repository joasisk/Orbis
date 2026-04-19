# Orbis Development Guide

This document is for contributors working on code, tests, and architecture.

## Source-of-truth order
Before implementing changes, follow this order:
1. [`docs/REQUIREMENTS.md`](REQUIREMENTS.md)
2. [`docs/MVP_PLAN.md`](MVP_PLAN.md)
3. [`docs/IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md)
4. [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)
5. ADRs in [`docs/adr/`](adr/)

## Local development quick start
1. Copy env file:
   ```bash
   cp .env.example .env
   ```
2. Start services:
   ```bash
   docker compose up --build
   ```
3. Verify:
   - API: `http://localhost/api/v1/health`
   - Web: `http://localhost/api/health`

## Project structure
- API domain orchestration: `apps/api`
- Web presentation and API consumption: `apps/web`
- Infra and proxy config: `infra`

See full layout in [`docs/REPO_STRUCTURE.md`](REPO_STRUCTURE.md).

## Quality checks
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

## Related contributor docs
- Architecture baseline: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)
- API strategy: [`docs/API_STRATEGY.md`](API_STRATEGY.md)
- Data models: [`docs/DATA_MODELS.md`](DATA_MODELS.md)
- AI contributor notes: [`docs/AI_AGENT_GUIDE.md`](AI_AGENT_GUIDE.md)
- SDK contributor context: [`docs/PHASE8_PUBLIC_SDK.md`](PHASE8_PUBLIC_SDK.md)
