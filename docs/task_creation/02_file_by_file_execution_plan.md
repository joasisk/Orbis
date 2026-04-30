# Task Creation Rework — File-by-File Execution Plan

## API Contract and Schemas
- `apps/api/app/schemas/domain.py`
  - Add task priority/urgency enum literals.
  - Replace numeric task attribute fields with enum-based fields.
  - Remove direct `status` from generic task update schema.
  - Add status transition request schema.

## DB Models and Constraints
- `apps/api/app/models/domain.py`
  - Convert task priority/urgency fields to string-enum storage.
  - Add task constraints for status and enum value checks.
  - Align task status default to `staged`.

## Migration
- `apps/api/alembic/versions/<new_migration>.py`
  - Numeric-to-enum data backfill.
  - Constraint rollout.
  - Deterministic downgrade mapping.

## API Routes
- `apps/api/app/api/v1/domain.py`
  - Update task filter query types for enum-based priority/urgency.
  - Add task status transition endpoint.
  - Keep/create compatibility strategy for spouse influence endpoint.

## Domain Services
- `apps/api/app/services/domain.py`
  - Add transition service method and transition legality checks.
  - Preserve status non-direct-edit policy in generic update.
  - Enforce owner/spouse write boundaries on attribute fields.
  - Handle scrubbed unscheduling side effects.

## Planning/Focus Compatibility
- `apps/api/app/services/focus.py`
- `apps/api/app/services/planning.py`
  - Replace numeric assumptions with enum-to-score mapping.
  - Exclude scrubbed tasks from planning/scheduling candidates.

## Web Task UI
- `apps/web/src/components/entity-management.tsx`
  - Reorder form sections.
  - Implement markdown-backed WYSIWYG experience.
  - Improve unified orbit/project selector with debounced search.
  - Enforce role-aware field visibility/editability.
  - Replace direct status edit with transition actions.

## i18n
- `apps/web/src/lib/i18n.ts`
  - Add labels/status/action keys across all available languages.

## Tests
- `apps/api/tests/test_domain_crud_flow.py`
- `apps/api/tests/test_focus_daily_plan.py`
- `apps/api/tests/test_planning_flow.py`
- `apps/api/tests/test_task_status_transitions.py` (new)
  - Update existing numeric assumptions and add transition/permission coverage.

## Documentation
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/GAP_ANALYSIS.md`
- `docs/API_SWAGGER.md` and/or `docs/API_STRATEGY.md`
  - Reflect contract and lifecycle updates.
