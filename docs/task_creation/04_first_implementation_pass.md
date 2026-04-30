# Task Creation Rework — First Implementation Pass (Execution Checklist)

## Step 1: API Schemas (`apps/api/app/schemas/domain.py`)
- Add `TaskPriority` + `TaskUrgency` literals.
- Replace numeric task attribute schema fields with enum types.
- Remove direct `status` field from generic task update schema.
- Add status transition payload schema (action-based recommended).

## Step 2: DB Model + Migration
### `apps/api/app/models/domain.py`
- Update task priority/urgency owner+spouse fields to string.
- Add constraints for status and enum sets.
- Set task status default to `staged`.

### `apps/api/alembic/versions/<new>.py`
- Add temporary string columns.
- Backfill using deterministic mapping.
- Swap/drop old columns and apply constraints.

## Step 3: Domain Service (`apps/api/app/services/domain.py`)
- Keep create forcing `staged`.
- Keep generic update blocking direct status writes.
- Introduce `transition_task_status` with legal transition map.
- Enforce role-specific attribute write permissions.
- Ensure scrubbed tasks are unscheduled from current/future schedules.

## Step 4: API Route Wiring (`apps/api/app/api/v1/domain.py`)
- Add `POST /tasks/{id}/status-transition`.
- Update list task query typing for enum filters.
- Keep or deprecate spouse-influence route with explicit compatibility note.

## Step 5: Planning/Focus Adaptation
- `apps/api/app/services/focus.py`
- `apps/api/app/services/planning.py`

Tasks:
- Implement enum-to-score mapping helpers.
- Replace numeric comparisons with mapped scoring.
- Exclude scrubbed tasks from candidate selection.

## Step 6: Web Task Modal (`apps/web/src/components/entity-management.tsx`)
- Reorder to: Basics → Classification → Attributes.
- Introduce markdown-backed WYSIWYG editor.
- Implement debounced unified orbit/project search/filter/select.
- Ensure role-aware field visibility/editability.
- Replace direct status editing with explicit transition actions.

## Step 7: i18n
- `apps/web/src/lib/i18n.ts`

Tasks:
- Add all new labels/action/status keys.
- Ensure all available languages are updated.

## Step 8: Tests
### API
- Update/create tests in:
  - `apps/api/tests/test_domain_crud_flow.py`
  - `apps/api/tests/test_focus_daily_plan.py`
  - `apps/api/tests/test_planning_flow.py`
  - `apps/api/tests/test_task_status_transitions.py`

Coverage targets:
- Enum validation and filtering.
- Status transition matrix.
- Role-based permission enforcement.
- Scrubbed scheduling exclusion/removal.

### Web
- Add behavior tests for section order, debounce/filtering, role field gating, and status actions.

## Step 9: Validation Commands
- `cd apps/api && ruff check app tests`
- `cd apps/api && ruff format --check app tests`
- `cd apps/api && pytest`
- `cd apps/web && npm run lint`
- `cd apps/web && npm run typecheck`

## Step 10: Documentation Sync
- Update planning/API docs after implementation.
- Mark completed plan items to prevent stale planning artifacts.
