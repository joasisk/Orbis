# Phase-by-Phase Implementation Plan

## Phase 0 — Foundations
Goal: establish repo, local development, and architecture guardrails.

Deliverables:
- repository structure in place
- Docker Compose local stack running
- environment strategy and secret handling
- coding standards, linting, formatting
- initial documentation set
- architecture decision records started

Definition of done:
- `docker compose up` starts proxy, web, api, db, redis, worker
- health endpoints exist for api and web

## Phase 1 — Core backend and auth
Goal: secure backend foundation and basic user model.

Deliverables:
- FastAPI app bootstrapped
- PostgreSQL connection and migrations
- auth model:
  - owner role
  - spouse role
- secure password auth
- refresh token flow
- API auth middleware
- audit log model starter

Key entities:
- User
- Session / RefreshToken
- AuditEvent

Definition of done:
- login/logout works
- protected endpoint works
- roles enforce access

## Phase 2 — Project and task domain
Goal: core data model and CRUD workflows.

Deliverables:
- Areas of Life
- Projects
- Tasks
- recurring commitments
- task dependencies
- privacy flags
- user priority inputs
- spouse influence inputs
- history/versioning model

Definition of done:
- API CRUD for all core entities
- task/project list and detail pages in web app
- version entries created on meaningful changes

## Phase 3 — Scheduling and focus workflows
Goal: make the system usable day to day.

Deliverables:
- daily plan concept
- focus mode endpoint and UI
- task execution actions:
  - start
  - stop
  - sidetrack
  - unable to finish
- blocker reason tracking
- energy input before and after task
- overload detection v1

Definition of done:
- user can ask system what to do now
- user can track a task session
- user can record blockers quickly

## Phase 4 — AI planning engine
Goal: introduce AI where it creates clear value.

Deliverables:
- provider abstraction layer
- weekly plan generation job
- approval workflow for proposed schedule
- note-to-task extraction workflow
- prompt templates and evaluation logging
- AI guardrails:
  - no silent schedule changes
  - approval required

Definition of done:
- Sunday planning job creates a proposal
- proposal can be accepted or edited
- imported note can generate candidate tasks

## Phase 4.1 — Schedule and performance model extension
Goal: introduce explicit schedule entities and execution telemetry without reopening completed Phase 3/4 scope.

Deliverables:
- schedule data model additions (`weekly_schedules`, `daily_schedules`, `daily_schedule_items`)
- schedule lifecycle and execution endpoints aligned to approval-first behavior
- telemetry capture for outcomes, time spent, distractions, and mood/energy inputs
- planner input wiring that consumes new telemetry while preserving approval gates

Definition of done:
- weekly/day schedule lifecycle works with owner-only accept/reject controls
- execution telemetry is persisted and available to planner feature assembly
- web/API contracts for schedule surfaces are stabilized before subsequent UX catch-up work

## Phase 4.5 — Web catch-up and settings UX
Goal: close MVP usability gaps by wiring existing API capabilities into the day-to-day web experience.

Deliverables:
- replace static homepage dead-end with API-backed dashboard flows
- fetch and render Areas of Life, Projects, and Tasks in primary app routes
- fetch and render `weekly_schedules`/`daily_schedules` (including `proposed` vs `accepted` state) in web UI
- render `daily_schedule_items` execution telemetry inputs (outcome, actual minutes, distractions) from stabilized Phase 4.1 contracts
- promote "do now" and focus actions to first-class default navigation path
- settings interface (owner-focused MVP):
  - profile/session basics
  - reminder preferences (within existing MVP reminder scope)
  - calendar and notes integration connection status/config surface
  - AI planning controls tied to approval-first guardrails and schedule lifecycle semantics from Phase 4.1

Definition of done:
- primary web entry route shows live API data (not placeholder/static-only)
- user can navigate between tasks, daily plan, and weekly schedule context without hidden routes
- settings page exists and persists configuration through API endpoints
- no approval gates are bypassed in scheduling/planning interactions

## Phase 5 — Calendar and reminder integration
Goal: connect planning to real time and commitments.

Deliverables:
- one calendar adapter first
- read external events
- write accepted `daily_schedule_items` as soft calendar blocks (never auto-publish from proposed schedules)
- reminder scheduling worker
- adaptive reminder response tracking tied to schedule/day-item identifiers for planner feedback reuse

Definition of done:
- external commitments appear in planning context
- accepted schedule items can create calendar blocks
- reminders can be delivered and logged

## Phase 6 — Wife visibility and influence experience
Goal: support household transparency without losing owner control.

Deliverables:
- spouse dashboard view
- private-item handling
- visible schedule compression/minimization for low-importance items from accepted schedules only
- influence input UX
- weighting rules for critical family/household items

Definition of done:
- spouse sees relevant accepted schedule view
- private items are hidden properly
- influence values affect AI planning but do not overwrite owner data

## Phase 7 — Hardening and TrueNAS packaging
Goal: make it deployable and reliable in homelab conditions.

Deliverables:
- production Dockerfiles
- backups/export scripts
- restore workflow
- observability baseline (including schedule lifecycle and day-item telemetry paths introduced in Phase 4.1)
- rate limiting
- API key flow for external frontends
- TrueNAS deployment notes

Definition of done:
- app can be deployed cleanly on TrueNAS
- backup/export tested
- basic security review complete

## Phase 8 — Post-MVP expansion
Goal: expand integrations and platform reach beyond MVP without changing MVP guardrails.

Deliverables (incremental):
- public SDK baseline (API-key based) for external tooling automation
- evaluate GraphQL facade feasibility against existing REST contracts
- mobile app with Expo
- iOS widgets and notifications
- richer analytics
- plugin system evolution

Definition of done (for first increment):
- documented public SDK usage aligned to existing API key flow
- SDK includes task/project read operations and core action helpers (daily plan/focus start)
- automated tests validate request auth header behavior and error handling

## Detailed schedule/performance extension plan
- See `docs/SCHEDULE_AND_PERFORMANCE_MODEL_PLAN.md` for DB, API, and web implementation details for explicit weekly/daily schedules and adaptive performance telemetry.
- **When this work happens in the implementation plan:** this extension is tracked as **Phase 4.1**.
  - Phase 3 and Phase 4 are treated as complete/closed.
  - Phase 4.1 owns schedule model + telemetry rollout end-to-end.
  - Before Phase 4.5, Phase 4.1 completes API contract stabilization so web catch-up/settings can consume finalized schedule endpoints.
