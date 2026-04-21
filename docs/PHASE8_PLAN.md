# Phase 8 Execution Plan (Post-MVP Expansion)

## Purpose
This plan breaks Phase 8 (`docs/IMPLEMENTATION_PLAN.md`) into small, safe increments that expand the platform without changing MVP guardrails.

## Guardrails carried forward from MVP
- Keep planner approval-first behavior intact (no silent schedule mutations).
- Keep spouse visibility/privacy boundaries intact.
- Keep owner priority and spouse influence as separate values.
- Keep API/service layers as domain source of truth; clients stay thin.

## Delivery strategy
Phase 8 is delivered as sequential increments so each slice can ship independently and preserve deployability for self-hosted users.

---

## Increment 8.1 — Public SDK baseline (in progress)
**Objective:** ship a stable public SDK for automation against existing API-key-protected endpoints.

### Scope
- Python SDK package and versioning policy
- Auth (`X-API-Key`) and typed error normalization
- Core reads/actions:
  - tasks/projects reads
  - daily plan fetch helper
  - focus start helper
- Usage docs and examples
- Unit tests with transport mocks

### Exit criteria
- SDK examples run end-to-end against local API
- Auth/error handling tests pass
- Semver/versioned changelog policy documented

### Notes
- Detailed baseline tracked in `docs/PHASE8_PUBLIC_SDK.md`.

---

## Increment 8.2 — Obsidian multi-vault expansion
**Objective:** support multiple vault connections while preserving existing extraction and approval flow.

### Scope
- Data model updates for multiple vault records per owner
- Routing rules from vault/folder/tag to Area/Project defaults
- Web/API settings UX for vault management and routing previews
- Worker updates for per-vault ingestion scheduling

### Exit criteria
- Multiple vaults can be connected and independently enabled/disabled
- Imported notes become proposed tasks only (no direct schedule writes)
- Routing rules are deterministic and test-covered

### Dependencies
- Stable SDK auth patterns from 8.1 can be reused for integration tests

---

## Increment 8.3 — GraphQL facade feasibility
**Objective:** evaluate whether a read-focused GraphQL facade improves client ergonomics without replacing REST.

### Scope
- ADR documenting tradeoffs, maintenance cost, and security implications
- Prototype for read-only endpoints (tasks/projects/schedule summaries)
- Benchmarks: latency, payload size, and resolver complexity

### Exit criteria
- Decision recorded as:
  - proceed with limited read facade, or
  - defer and keep REST-only for post-MVP horizon
- No mutation path is added in this increment

---

## Increment 8.4 — Mobile app foundation (Expo)
**Objective:** establish a reliable mobile shell for daily plan and focus interactions.

### Scope
- Expo app scaffold and auth/session handling via API keys/tokens
- Daily plan view and task focus start/stop flows
- Accessibility baseline (font scaling, reduced-motion aware interactions)
- Offline-read cache for last fetched daily plan (no offline writes in this increment)

### Exit criteria
- Owner can authenticate and complete focus start/stop from mobile
- Critical flows covered by integration/e2e smoke tests
- No divergence in domain behavior from API contracts

### Dependencies
- SDK (8.1) can be reused to reduce duplicated client logic

---

## Increment 8.5 — iOS widgets and notifications
**Objective:** provide low-friction reminders and glanceable context.

### Scope
- Widget surfaces: current focus item, next planned block
- Notification pipeline refinement for focus/daily schedule reminders
- Quiet-by-default settings and per-channel controls

### Exit criteria
- Widgets never reveal private items in spouse/shared contexts
- Notification delivery and acknowledgement are logged for planner feedback
- User-configurable quiet windows are respected

---

## Increment 8.6 — Analytics expansion
**Objective:** provide actionable insights without creating noisy engagement loops.

### Scope
- Read models for execution trends (completion, drift, blockers, energy patterns)
- Weekly summary endpoints and web/mobile dashboards
- Export-friendly endpoints for self-hosted analysis

### Exit criteria
- Analytics highlight planning/actionable adjustments (not streak gamification)
- Aggregates are computed from existing telemetry sources only
- Privacy constraints preserved for spouse-visible analytics surfaces

---

## Increment 8.7 — Plugin system evolution
**Objective:** enable constrained extension points for integrations and automations.

### Scope
- Plugin manifest spec, capability model, and sandbox policy
- Event hooks (read-only first; controlled write hooks later)
- Admin UI for plugin install/enable/disable and audit visibility

### Exit criteria
- Plugin permission boundaries are enforced and test-covered
- Install/upgrade/disable lifecycle documented for self-hosted operators
- Security review checklist completed before broad enablement

---

## Cross-cutting workstreams
These run across all increments:

1. **Security & privacy**
   - Threat model updates per increment
   - Regression checks for private-item exposure and auth boundaries

2. **Documentation lifecycle**
   - Keep `docs/IMPLEMENTATION_PLAN.md` current with increment status
   - Add ADRs when architecture or contract direction changes

3. **Observability**
   - Structured logs/metrics/traces for new integration paths
   - Alerting for ingestion/job failures and auth anomalies

4. **Backward compatibility**
   - Version API/SDK changes explicitly
   - Publish migration notes for self-hosted operators

## Suggested sequence and checkpoints
1. 8.1 Public SDK baseline
2. 8.2 Obsidian multi-vault expansion
3. 8.3 GraphQL feasibility decision
4. 8.4 Mobile foundation
5. 8.5 iOS widgets + notifications
6. 8.6 Analytics expansion
7. 8.7 Plugin system evolution

At each checkpoint:
- confirm MVP guardrails still hold,
- run targeted regression suites in API/web,
- update implementation docs to reflect actual state.
