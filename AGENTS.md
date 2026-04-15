# AGENTS.md

## Agent profile
This repository supports **Agenti AI / coding agents** working on Orbis.

## Project at a glance
- Product: self-hosted, AI-assisted time and project management for ADHD users.
- Primary stack:
  - Web: Next.js (`apps/web`)
  - API: FastAPI (`apps/api`)
  - Data: PostgreSQL
  - Queue/cache: Redis
  - Reverse proxy: Caddy
- Architecture is API-first: keep business logic in API/services, keep the web layer thin.

## Source-of-truth order (follow strictly)
1. `docs/REQUIREMENTS.md`
2. `docs/MVP_PLAN.md`
3. `docs/IMPLEMENTATION_PLAN.md`
4. `docs/ARCHITECTURE.md`
5. Relevant ADRs under `docs/adr/`
6. Existing tests and code comments

When instructions conflict, prefer the highest item in this list unless an explicit user/developer/system instruction says otherwise.

## Non-negotiable guardrails
- Do **not** introduce behavior outside MVP scope unless clearly labeled as future work.
- Do **not** remove approval gates around AI planning/scheduling changes.
- Do **not** expose private items to spouse-facing views.
- Do **not** merge owner priority values with spouse influence values into one field.
- Do **not** add gamification/noisy engagement mechanics by default.
- Preserve low-friction, low-overwhelm UX decisions.

## Architecture and design constraints
- Keep core domain orchestration in `apps/api` service/domain layers.
- Keep `apps/web` focused on presentation and API consumption.
- Prefer REST contract consistency for MVP endpoints.
- Treat PostgreSQL as source of truth; use JSONB only for flexible metadata.
- Background/async operations belong in worker-oriented paths/jobs, not ad-hoc web handlers.

## Implementation workflow for agents
1. Read the source-of-truth docs relevant to the task.
2. Map task to a specific requirement (and MVP phase if possible).
3. Propose/implement the **smallest** viable change.
4. Update tests and/or provide executable validation steps.
5. If behavior/contract changes, update docs and ADRs as needed.

## Quality bar
Before finishing, run the most relevant checks:

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

## Directory intent
- `apps/api`: domain logic, authz, planning orchestration, integrations, worker entrypoints.
- `apps/web`: UI shell and interaction flows.
- `docs`: requirements, architecture, plans, and ADRs.
- `infra`: deployment and reverse proxy configuration.

## Change safety checklist
A contribution is safe when:
- It is traceable to documented requirements.
- It does not silently expand product scope.
- It preserves security/privacy boundaries.
- It keeps API/web separation intact.
- It includes tests or concrete verification steps.
