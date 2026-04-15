# Phase 2 Work Plan — Project and Task Domain

## Source scope
This work plan is derived from **Phase 2** in `docs/IMPLEMENTATION_PLAN.md`.

Phase 2 goal:
- core data model and CRUD workflows

Phase 2 required deliverables:
- Areas of Life
- Projects
- Tasks
- recurring commitments
- task dependencies
- privacy flags
- user priority inputs
- spouse influence inputs
- history/versioning model

Phase 2 definition of done:
- API CRUD for all core entities
- task/project list and detail pages in web app
- version entries created on meaningful changes

---

## 1) Backend domain model and migrations

### Objectives
- Introduce all Phase 2 entities in the data model.
- Define relationship integrity and constraints up front.
- Keep migration history clean and reversible.

### Tasks
- Add models for:
  - `AreaOfLife`
  - `Project`
  - `Task`
  - `RecurringCommitment`
  - `TaskDependency`
  - `EntityVersion` (or equivalent history table)
- Add key fields:
  - privacy fields (`is_private`, `visibility_scope`)
  - user priority inputs for both Project and Task:
    - `priority`
    - `urgency`
    - `deadline`
    - `deadline_type` (`soft` / `hard`)
  - spouse priority inputs for both Project and Task:
    - `spouse_priority`
    - `spouse_urgency`
    - `spouse_deadline`
    - `spouse_deadline_type` (`soft` / `hard`)
- Add relationship constraints:
  - project belongs to area of life
  - task optionally belongs to project
  - dependency edges are unique
  - no self-referential task dependency
- Create Alembic migrations for all new tables, indexes, and constraints.

### Exit criteria
- Migrations apply/rollback cleanly in local and CI environments.

---

## 2) API schema contracts and validation

### Objectives
- Provide stable request/response contracts.
- Reject invalid data before persistence.

### Tasks
- Add create/update/read schemas for each core Phase 2 entity.
- Add validation rules for:
  - invalid dependency loops/self-reference
  - invalid privacy scope combinations
  - recurrence field format correctness
- Standardize API error shape for validation and authorization failures.

### Exit criteria
- Invalid payloads are consistently rejected with actionable errors.

---

## 3) Service layer and business logic

### Objectives
- Keep route handlers thin and testable.
- Centralize meaningful-change and versioning behavior.

### Tasks
- Implement service modules for each Phase 2 entity CRUD workflow.
- Add dependency integrity checks and domain-level guards.
- Implement recurring commitment baseline behavior (create/update/list semantics).
- Add a shared change detector to decide when history/version entries are written.

### Exit criteria
- Route handlers delegate domain logic to services.

---

## 4) API endpoints (Phase 2 CRUD)

### Objectives
- Meet the Phase 2 API CRUD requirement for all core entities.

### Tasks
- Add API routers/endpoints for:
  - `/areas`
  - `/projects`
  - `/tasks`
  - `/recurring-commitments`
  - `/task-dependencies`
- Implement baseline list filtering/sorting:
  - by project/area
  - by status/priority
  - by privacy
- Add history endpoints for entity version retrieval.

### Exit criteria
- Full CRUD coverage with authentication/authorization applied.

---

## 5) Web app list/detail workflows

### Objectives
- Satisfy Phase 2 UI definition of done.

### Tasks
- Add project list/detail pages.
- Add task list/detail pages.
- Add create/edit/delete forms for projects and tasks.
- Include UX inputs for:
  - privacy flags
  - user priority inputs (`priority`, `urgency`, `deadline`, `deadline_type`)
  - spouse priority inputs (`spouse_priority`, `spouse_urgency`, `spouse_deadline`, `spouse_deadline_type`)
  - task dependencies
- Add basic history/version panel on detail views.

### Exit criteria
- User can create, edit, inspect, and delete core entities in the web app.

---

## 6) Versioning strategy

### Objectives
- Guarantee meaningful changes are traceable.

### Tasks
- Define meaningful-change matrix for each entity type.
- Record version entries with:
  - entity type/id
  - actor/user id
  - timestamp
  - changed fields (diff or snapshots)
- Ensure create/update/delete events are versioned according to matrix policy.

### Exit criteria
- Version entries are generated reliably for all meaningful changes.

---

## 7) Testing and quality gates

### Objectives
- Prevent regressions and ensure Phase 2 completeness.

### Tasks
- Add backend unit tests for:
  - model constraints
  - service-level validation
  - versioning trigger behavior
- Add API integration tests for CRUD routes and auth boundaries.
- Add web-level smoke tests for project/task list and detail flows.
- Add migration upgrade/downgrade test in CI.

### Exit criteria
- All required tests pass in CI, including migrations.

---

## 8) Delivery sequence

### Recommended order
1. Models + migrations
2. Schemas + validation
3. Services + CRUD APIs
4. Dependency and recurrence hardening
5. Versioning model + endpoints
6. Web list/detail UI + forms
7. Test hardening + docs updates

---

## Proposed implementation slices

### Slice A (Backend foundation)
- models, migrations, schemas

### Slice B (CRUD enablement)
- service methods and API routes for Areas/Projects/Tasks

### Slice C (Advanced domain)
- dependencies, recurring commitments, privacy/influence rule handling

### Slice D (History)
- meaningful-change detector and version entry endpoints

### Slice E (Web completion)
- project/task list and detail pages + CRUD forms

### Slice F (Quality)
- test expansion and CI stability fixes

---

## Open decisions to unblock implementation

- privacy visibility matrix (owner/spouse/shared behavior)
- recurrence expression format (simple cadence vs full RRULE)
- dependency policy for blocked tasks (strict vs advisory enforcement)
