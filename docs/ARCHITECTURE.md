# Architecture Overview

## Guiding principle
API-first architecture so web, mobile, and third-party frontends all consume the same domain services.

## Core services

### Web app
- Next.js frontend
- handles user-facing UI and browser session experience
- should keep business logic thin

### API
- FastAPI application
- owns domain logic, permissions, orchestration, and integrations
- exposes REST first

### Worker
- background jobs:
  - weekly planning
  - reminder scheduling
  - note ingestion
  - calendar sync tasks
  - cleanup jobs

### PostgreSQL
- source of truth for structured data
- use JSONB only for flexible metadata where appropriate

### Redis
- queues, rate limiting, cache, short-lived state

## Domain boundaries
- auth
- projects/tasks
- planning
- reminders
- integrations
- AI orchestration
- audit/versioning

## Security principles
- role-based access
- privacy flags on entities
- audit log for AI-related actions
- approval gates for automated planning changes
- browser cookies for web auth, token path for external clients

## API strategy
- REST for MVP
- GraphQL after schema stabilizes
- webhooks/events after core entity lifecycle is stable

## Data model reference
- See `docs/DATA_MODELS.md` for current implemented entities/relationships and planned schedule-model extensions.
