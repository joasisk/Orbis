# Schedule and Performance Model Implementation Plan

## Purpose
Define an MVP-scoped plan to add explicit weekly/daily schedules and richer execution telemetry so the system can adapt workload using AI while preserving approval gates.

## Requirements traceability
- `docs/REQUIREMENTS.md` §2: AI weekly planning with approval gate.
- `docs/REQUIREMENTS.md` §3: focus workflow and approximate time spent.
- `docs/REQUIREMENTS.md` §4: failure/blocker signals used for rescheduling.
- `docs/IMPLEMENTATION_PLAN.md` Phase 3: daily plan concept and focus tracking.
- `docs/IMPLEMENTATION_PLAN.md` Phase 4: approval workflow for proposed schedule.

## Scope and non-goals
### In scope
- Add explicit schedule entities:
  - weekly schedule container
  - 7 daily schedules per week
  - daily schedule items referencing tasks
- Add explicit schedule lifecycle states (`proposed`, `accepted`) at weekly and daily levels.
- Add telemetry needed for adaptive planning:
  - postponed/failed outcomes
  - self-evaluation
  - task time spent
  - distractions
  - mood/energy snapshots

### Out of scope (for this change set)
- Calendar provider synchronization logic.
- Advanced analytics dashboards (beyond API payloads for later AI/analytics).
- New gamification/engagement mechanics.

---

## Data model plan (DB)

## 1) New tables
### `weekly_schedules`
- `id` (uuid, pk)
- `owner_user_id` (fk -> users.id, on delete cascade)
- `week_start_date` (date, indexed)
- `status` (enum/check: `proposed|accepted|rejected`)
- `source_proposal_id` (nullable fk -> weekly_plan_proposals.id, on delete set null)
- `created_at`, `accepted_at` (nullable)

Constraints/indexes:
- unique (`owner_user_id`, `week_start_date`) for active record strategy (or include status if preserving multiple revisions).
- index on (`owner_user_id`, `week_start_date`, `status`).

### `daily_schedules`
- `id` (uuid, pk)
- `weekly_schedule_id` (fk -> weekly_schedules.id, on delete cascade)
- `owner_user_id` (fk -> users.id, on delete cascade)
- `schedule_date` (date, indexed)
- `status` (enum/check: `proposed|accepted|adjusted`)
- `mood_score` (smallint nullable, check range 1..5)
- `morning_energy` (float nullable, range check 0..1)
- `evening_energy` (float nullable, range check 0..1)
- `self_evaluation` (text nullable)
- `created_at`, `updated_at`

Constraints/indexes:
- unique (`weekly_schedule_id`, `schedule_date`)
- unique (`owner_user_id`, `schedule_date`) when status in (`accepted`, `adjusted`) to prevent duplicate active day plans.

### `daily_schedule_items`
- `id` (uuid, pk)
- `daily_schedule_id` (fk -> daily_schedules.id, on delete cascade)
- `owner_user_id` (fk -> users.id, on delete cascade)
- `task_id` (fk -> tasks.id, on delete cascade)
- `planned_minutes` (int not null, check > 0)
- `actual_minutes` (int nullable, check >= 0)
- `outcome_status` (enum/check: `planned|done|postponed|failed|partial|skipped`)
- `order_index` (int not null)
- `distraction_count` (int not null default 0)
- `distraction_notes` (text nullable)
- `postponed_to_date` (date nullable)
- `failure_reason` (text nullable)
- `created_at`, `updated_at`

Constraints/indexes:
- unique (`daily_schedule_id`, `order_index`)
- index (`owner_user_id`, `task_id`, `outcome_status`)
- check `postponed_to_date` is null unless `outcome_status='postponed'`.

## 2) Reuse/adjust existing tables
- Keep `weekly_plan_proposals` and `weekly_plan_items` as AI proposal artifacts.
- Add optional linkage from accepted `weekly_schedules.source_proposal_id` for traceability.
- Keep `focus_sessions`/`blocker_events` for high-resolution execution telemetry.

## 3) Migration sequence
1. Add new schedule tables and constraints.
2. Backfill path (optional): convert current accepted `weekly_plan_proposals` into `weekly_schedules` + `daily_schedules` + `daily_schedule_items`.
3. Add compatibility views/helpers if needed by existing endpoints.
4. Drop deprecated behavior only after API/FE migration complete.

---

## Backend/API plan

## 1) Domain services
Create service layer modules:
- `schedule_generation_service`
  - materialize `weekly_schedules` + 7 `daily_schedules` from proposal items.
- `schedule_acceptance_service`
  - enforce owner-only acceptance.
  - acceptance of weekly schedule auto-accepts included daily schedules (or requires per-day accept; feature flag).
- `daily_execution_service`
  - update `daily_schedule_items` outcomes.
  - store time spent and distraction counters.
  - create/update focus session links where present.

## 2) API endpoints (REST)
### Weekly schedule
- `POST /v1/schedules/weeks/generate` -> creates proposed weekly schedule (from AI proposal job output).
- `GET /v1/schedules/weeks/{week_start_date}` -> fetch week + 7 days + items.
- `POST /v1/schedules/weeks/{id}/accept` -> accept weekly schedule (approval gate).
- `POST /v1/schedules/weeks/{id}/reject` -> reject weekly schedule.

### Daily schedule
- `GET /v1/schedules/days/{date}` -> fetch day plan and status.
- `POST /v1/schedules/days/{id}/accept` -> accept daily schedule.
- `PATCH /v1/schedules/days/{id}` -> adjust mood/energy/self-evaluation.

### Daily schedule item execution
- `PATCH /v1/schedules/day-items/{id}`
  - update `outcome_status`, `actual_minutes`, `distraction_count`, `distraction_notes`, `postponed_to_date`, `failure_reason`.
- `POST /v1/schedules/day-items/{id}/start-focus`
- `POST /v1/schedules/day-items/{id}/end-focus`

## 3) Validation and rules
- Only owner can accept/reject schedules.
- Weekly schedule should include exactly 7 distinct dates from `week_start_date` to `+6` days.
- Accepted day items cannot reference private task in spouse-facing contexts.
- Preserve approval gates: no automatic mutation of accepted schedules by AI.

## 4) AI planning integration
- Planner reads historical features from:
  - item outcomes (`failed`, `postponed`, `partial`)
  - actual vs planned minutes
  - distraction rate
  - mood/energy snapshots
  - blocker reasons from existing tables
- Planner writes proposals; acceptance endpoint materializes final schedules.

---

## Frontend (Web) plan

## 1) New views/components
- Weekly Schedule page:
  - week header, proposal status, accept/reject actions.
  - seven-day board/list with per-day status chips.
- Daily Schedule page:
  - ordered task blocks with planned minutes.
  - quick outcomes: done/postponed/failed/partial/skipped.
  - time spent edit and distraction capture.
  - mood + energy + self-evaluation card.

## 2) UX and state flow
- Proposed state is visually distinct from accepted.
- On week acceptance:
  - confirm modal explaining no automatic overwrite without approval.
- On day adjustments:
  - capture reason when workload is reduced.
- Low-friction inputs:
  - one-tap outcome actions.
  - optional text fields collapsed by default.

## 3) Spouse visibility behavior
- Spouse sees only allowed schedule items from existing visibility rules.
- Private tasks remain hidden.
- Spouse cannot accept/reject owner schedules.

---

## Delivery plan (phased)

## Updated implementation schedule (as of 2026-04-16)
This schedule is aligned to the current roadmap ordering where scheduling/focus work is Milestone 2, after auth/core-domain hardening.

### Target window
- **Start:** 2026-05-04 (first Monday after a 2-week M1 stabilization buffer)
- **MVP complete for this scope:** 2026-06-12
- **Total duration:** 6 weeks

### Week-by-week schedule
- **Week 1 (2026-05-04 -> 2026-05-08): Milestone A foundation**
  - finalize schema decisions and status state machine
  - implement migrations and SQLAlchemy models for weekly/daily schedule tables
  - add DB-level checks/indexes and migration tests
- **Week 2 (2026-05-11 -> 2026-05-15): Milestone B APIs, part 1**
  - implement week/day read endpoints and generation/accept/reject service skeletons
  - implement authorization guards and validation rules
  - add endpoint contract tests for week/day lifecycle
- **Week 3 (2026-05-18 -> 2026-05-22): Milestone B APIs, part 2**
  - implement day-item execution endpoints (`outcome_status`, `actual_minutes`, distractions)
  - integrate focus-session linkage and blocker signal joins
  - complete service-level state transition tests
- **Week 4 (2026-05-25 -> 2026-05-29): Milestone C web app**
  - build weekly schedule view and accept/reject UX
  - build daily schedule view and low-friction outcome capture
  - complete component/integration tests for week/day flows
- **Week 5 (2026-06-01 -> 2026-06-05): Milestone D AI feedback loop**
  - map telemetry extraction into planner input features
  - update prompt/eval logging to include new schedule telemetry signals
  - add regression tests for planner input assembly
- **Week 6 (2026-06-08 -> 2026-06-12): hardening and rollout**
  - run end-to-end QA across DB/API/FE flows
  - execute backfill (if needed) and production migration rehearsal
  - ship docs/runbooks and complete DoD checklist

### Go/no-go gates
- **Gate 1 (end of Week 1):** migration and model design accepted.
- **Gate 2 (end of Week 3):** API lifecycle and authz fully test-covered.
- **Gate 3 (end of Week 5):** planner successfully consumes new telemetry without bypassing approval gates.
- **Release gate (Week 6):** no critical defects in schedule acceptance/execution flows.

## Milestone A — Database foundation
- Add schema + migrations + indexes + checks.
- Add SQLAlchemy models and repository queries.
- Add migration tests (upgrade/downgrade smoke).

## Milestone B — Backend APIs
- Add Pydantic schemas and services.
- Implement week/day/item endpoints.
- Add authorization and validation guards.
- Add unit/integration tests.

## Milestone C — Frontend MVP
- Build weekly/day pages and API hooks.
- Add acceptance and item outcome workflows.
- Add basic empty/loading/error states.

## Milestone D — AI feedback loop
- Extend planner feature extraction from new telemetry.
- Update prompt templates and evaluation logs.
- Add regression tests for proposal generation inputs.

---

## Test strategy

## DB
- Migration applies cleanly from latest head.
- Constraints verified:
  - weekly/day uniqueness
  - 7-day completeness rule (service-level + test assertions)
  - valid status transitions

## BE/API
- Endpoint contract tests for each route.
- Authz tests (owner/spouse).
- State-transition tests:
  - proposed -> accepted/rejected
  - day item planned -> done/postponed/failed/partial/skipped
- Analytics payload correctness tests for planner inputs.

## FE
- Component tests for status rendering and action handling.
- Integration tests for accept/reject and day-item updates.
- Accessibility checks on key actions and forms.

---

## Risks and mitigations
- Risk: duplicate truth between proposal tables and schedule tables.
  - Mitigation: define proposal tables as pre-accept artifacts only; schedule tables as execution truth.
- Risk: over-capturing telemetry increases friction.
  - Mitigation: optional fields + progressive disclosure in UI.
- Risk: performance of analytics queries.
  - Mitigation: indexes on owner/date/status/task and aggregate/materialized views later.

## Definition of done
- Weekly schedule is first-class with proposed/accepted lifecycle.
- Exactly seven daily schedules per generated week.
- Daily schedules link to tasks through day items.
- Execution data captures outcomes, time spent, distractions, mood/energy, and self-evaluation.
- AI planner can read these signals without bypassing approval gates.
