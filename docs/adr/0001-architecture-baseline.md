# ADR 0001: Monorepo Baseline Architecture

- Status: Accepted
- Date: 2026-04-15

## Context
Orbis combines a web interface, API, worker process, and supporting infrastructure (PostgreSQL, Redis, reverse proxy). The implementation plan requires clear architecture guardrails early so subsequent phases can evolve consistently.

## Decision
We standardize on a monorepo containing:

- `apps/web`: Next.js application for user-facing workflows.
- `apps/api`: FastAPI application for business logic and persistence APIs.
- `apps/api/app/workers`: background worker entrypoint for async jobs.
- `infra/`: reverse proxy and deployment support files.
- `docs/`: requirements, architecture, and planning artifacts.

Runtime orchestration uses Docker Compose with proxy, web, api, db, redis, and worker services.

## Consequences

### Positive
- Shared versioning for web/api/docs with one source of truth.
- Lower setup overhead for local development.
- Architecture and operational docs live next to implementation.

### Trade-offs
- CI must explicitly handle multi-language tooling.
- Cross-app changes can increase CI runtime.
