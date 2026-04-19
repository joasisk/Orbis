# Phase 8 Public SDK Baseline

This document tracks the first delivered increment of Phase 8 (`docs/IMPLEMENTATION_PLAN.md`): a public, API-key-based SDK for external automations.

## Scope (this increment)
- Python client package under `sdk/python/orbis_sdk`
- Thin wrapper around existing stable REST endpoints
- API key auth header support (`X-API-Key`)
- Error normalization to a single SDK exception type
- Unit tests using HTTP transport mocks

## Out of scope (future Phase 8 increments)
- GraphQL support
- Mobile client SDKs
- Plugin framework
- Analytics-specific query client

## Why this is safe
- Reuses existing API-key flow introduced in Phase 7.
- Does not alter planner approval gates or schedule mutation behavior.
- Keeps API as source of truth and avoids duplicating domain logic in clients.
