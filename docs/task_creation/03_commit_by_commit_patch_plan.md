# Task Creation Rework — Commit-by-Commit Patch Plan

## Commit 1: Schema + DB Migration
**Goal:** Enum-based priority/urgency foundation and status constraints.

Files:
- `apps/api/app/schemas/domain.py`
- `apps/api/app/models/domain.py`
- `apps/api/alembic/versions/<new_migration>.py`

Suggested message:
- `feat(api): migrate task priority/urgency to enums and enforce task status constraints`

## Commit 2: Service + Route Behavior
**Goal:** Status transitions and role-safe attribute writes.

Files:
- `apps/api/app/services/domain.py`
- `apps/api/app/api/v1/domain.py`

Suggested message:
- `feat(api): add task status transition endpoint and enforce owner/spouse attribute boundaries`

## Commit 3: Planning/Focus Adaptation
**Goal:** Preserve ranking/scheduling behavior under enum attributes.

Files:
- `apps/api/app/services/focus.py`
- `apps/api/app/services/planning.py`
- `apps/api/app/schemas/planning.py` (if needed)

Suggested message:
- `refactor(api): adapt planning and focus scoring to enum task attributes`

## Commit 4: API Tests
**Goal:** Lock contract and role/transition behavior.

Files:
- `apps/api/tests/test_domain_crud_flow.py`
- `apps/api/tests/test_focus_daily_plan.py`
- `apps/api/tests/test_planning_flow.py`
- `apps/api/tests/test_task_status_transitions.py` (new)

Suggested message:
- `test(api): cover enum attributes, transitions, and role-based task edits`

## Commit 5: Web Task Modal Rework
**Goal:** UX layout + WYSIWYG + unified assignment selector.

Files:
- `apps/web/src/components/entity-management.tsx`
- optional extracted editor component file

Suggested message:
- `feat(web): redesign task modal with WYSIWYG description and unified orbit/project selector`

## Commit 6: Web i18n + UI Tests
**Goal:** Translation completeness and behavior confidence.

Files:
- `apps/web/src/lib/i18n.ts`
- locale dictionaries/tests as applicable

Suggested message:
- `chore(web): add i18n keys and tests for task creation/editing rework`

## Commit 7: Docs Sync
**Goal:** Keep planning and API docs current.

Files:
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/GAP_ANALYSIS.md`
- `docs/API_SWAGGER.md` and/or `docs/API_STRATEGY.md`

Suggested message:
- `docs: update task lifecycle and task-attribute contract documentation`
