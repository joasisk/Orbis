# Phase 2 Gap Analysis (Documentation vs Implementation)

## Scope
Compared **Phase 2 — Project and task domain** commitments in `docs/IMPLEMENTATION_PLAN.md` and `docs/PHASE2_WORK_PLAN.md` against the current implementation across API, data model, web UI, and tests.

---

## Deliverables Status

### 1) Areas of Life
**Status:** ⚠️ Partially implemented  
**What exists:**
- `AreaOfLife` model and migration table are present.
- API supports create/list/update/delete for areas.

**Gap:**
- Spouse visibility for owner areas is effectively blocked because non-owner area listing is filtered to `owner_user_id == actor.id`, so spouse users cannot discover owner areas they should potentially collaborate on.

### 2) Projects
**Status:** ✅ Implemented (baseline CRUD)  
**What exists:**
- Project model includes privacy + owner/spouse priority/deadline fields.
- API supports create/list/get/update/delete.
- Web includes project list and detail pages with create flow.

**Gap:**
- Authorization is overly permissive on updates/deletes: `get_project` grants access via `_can_view`, and `update_project`/`delete_project` reuse that read permission without checking write permissions.
- No explicit ownership check when creating a project in an area; if a caller knows an `area_id`, the service assigns owner from that area without access validation.

### 3) Tasks
**Status:** ✅ Implemented (baseline CRUD)  
**What exists:**
- Task model includes optional project linkage, privacy flags, and owner/spouse influence inputs.
- API supports create/list/get/update/delete.
- Web includes task list and detail pages with create flow.

**Gap:**
- Same write-authorization issue as projects (`update_task`/`delete_task` depend on read-level `_can_view`).
- Task creation inherits owner from project without validating caller’s permission to write in that project.

### 4) Recurring commitments
**Status:** ⚠️ Mostly implemented  
**What exists:**
- Model, migration, schemas, and create/list/update/delete endpoints exist.

**Gap:**
- API does not provide detail endpoint (`GET /recurring-commitments/{id}`), so full CRUD/read parity is incomplete if “read” is interpreted as both list and detail.

### 5) Task dependencies
**Status:** ⚠️ Partially implemented  
**What exists:**
- Model/migration constraints include uniqueness and no self-reference.
- API supports create/list/delete.

**Gap:**
- No update endpoint.
- No cycle detection beyond self-reference (documentation calls for dependency loop validation).
- `list_task_dependencies` has no ownership/visibility filtering and can expose all dependency rows.

### 6) Privacy flags + user/spouse priority inputs
**Status:** ✅ Implemented in backend, ⚠️ partial in frontend  
**What exists:**
- Project/task backend supports `is_private`, `visibility_scope`, and owner/spouse priority/urgency/deadline fields.
- Schema-level rule enforces `is_private=true` ⇒ `visibility_scope='owner'`.

**Gap:**
- Frontend create forms do not include `deadline_type` and `spouse_deadline_type` inputs.

### 7) History/versioning model
**Status:** ✅ Implemented (baseline), ⚠️ policy hardening needed  
**What exists:**
- `EntityVersion` table, version writes on create/update/delete, and history endpoint exist.

**Gap:**
- No documented meaningful-change matrix; current behavior logs every changed field but does not encode per-entity policy.
- History authorization is too broad: any spouse role can read any entity history because filtering allows all spouse users regardless of ownership.

---

## Definition of Done Status

### DoD: API CRUD for all core entities
**Status:** ⚠️ Mostly implemented  
**Reasoning:**
- Areas/projects/tasks/recurring commitments/task dependencies are all exposed via API routes.
- However, recurring commitments and task dependencies do not have full detail/update parity, and dependency validation does not yet enforce loop constraints.

### DoD: task/project list and detail pages in web app
**Status:** ✅ Implemented (baseline)  
**Reasoning:**
- Project/task list pages and detail pages exist and are wired to API calls.

### DoD: version entries created on meaningful changes
**Status:** ⚠️ Partially implemented  
**Reasoning:**
- Version entries are created on create/update/delete.
- “Meaningful changes” criteria are not formalized and therefore not demonstrably enforced per documentation.

---

## Critical Gaps (Priority Order)

1. **Authorization hardening for write operations**
   - Split read visibility from write permission.
   - Enforce owner (or explicit allowed actor) for update/delete across project/task/recurring/dependency flows.
   - Validate ownership access on create when referencing foreign keys (`area_id`, `project_id`).

2. **Dependency integrity beyond self-reference**
   - Add cycle detection in service layer before creating dependency edges.
   - Add tests for multi-node cycle rejection.

3. **History access control correctness**
   - Restrict spouse history reads to records owned by the associated owner relationship.
   - Avoid global spouse-role visibility across unrelated owners.

4. **API completeness for Phase 2 entities**
   - Add `GET /recurring-commitments/{id}`.
   - Decide/update whether task dependencies need PATCH support or declare immutable edges explicitly in docs.

5. **Web DoD completion**
   - Add edit/delete flows in project/task UI (currently create/list/detail refresh).
   - Add missing inputs: `deadline_type`, `spouse_deadline_type`, and dependency assignment UX.

6. **Test coverage expansion**
   - Add service/API tests for auth boundaries, privacy visibility matrix, dependency cycles, and history access rules.
   - Add migration upgrade/downgrade checks and web smoke tests requested by the work plan.

---

## Suggested Next Sprint Slice

1. **Security first:** write authorization + history scoping fixes.
2. **Validation second:** dependency cycle checks + explicit error responses.
3. **UI completion:** edit/delete + missing fields and dependency UX.
4. **Confidence:** broaden integration tests for Phase 2 DoD and regressions.
