# Task Creation Rework — Implementation Plan

## Phase 0: Align requirements + current behavior
1. Audit current task model, forms, and API contracts.
2. Map requested changes to MVP/source-of-truth docs.

## Phase 1: Domain model and API contract updates

### 1) Replace numeric priority/urgency with language enums
- `priority`: `core | major | minor | ambient`
- `urgency`: `immediate | near | planned | flexible`
- Update create/update/read schemas and validation.
- Plan deterministic migration for existing numeric data.

### 2) Enforce status as enum and non-direct-edit
- Status set:
  - `staged`
  - `primed`
  - `in_flight`
  - `holding`
  - `mission_complete`
  - `scrubbed`
- Default on create: `staged`.
- Remove generic direct status editing.
- Add explicit transition endpoint/action flow.
- Ensure `scrubbed` tasks are unschedulable and removed from active/future schedules.

### 3) Owner/spouse attribute authorization in API
Attribute fields in scope:
- `priority`
- `urgency`
- `deadline_type`
- `deadline`

Rules:
- Caller can modify only their own attribute set.
- Opposite-side fields are either rejected or ignored consistently.
- Edit responses can still include both sets for visibility.

## Phase 2: Data layer + migration
1. Schema changes for enum-based priority/urgency and constrained status.
2. Backfill numeric values to enums with deterministic mappings.
3. Add DB constraints/indexes to enforce integrity.

## Phase 3: Web UI/UX rework

### 1) Form layout restructure
Order:
1. Task name + description
2. Classification (project/orbit assignment)
3. Attributes:
   - Row 1: priority + urgency
   - Row 2: deadline type + deadline date/time
   - Row 3: assignment + private checkbox

### 2) Description editor
- Store markdown.
- Present as WYSIWYG editor with safe round-tripping.

### 3) Unified orbit/project selector
- One searchable dropdown field.
- Option format: `<orbit>: <project>`
- Selection sets both orbit and project identifiers.
- Debounced filtering across both orbit + project names.

### 4) Role-aware UI visibility/editability
- Create: show/edit only caller-owned attribute inputs.
- Edit: show both sides; only caller side editable.

### 5) Status UI behavior
- No free-form status editing.
- Use explicit status transition actions/buttons.

## Phase 4: Scheduler integration and safeguards
- Exclude `scrubbed` from scheduling candidates.
- Remove scrubbed tasks from future schedule placements.
- Validate transition consistency.

## Phase 5: Testing strategy

### API
- Enum validation tests.
- Role authorization tests for owner/spouse attribute writes.
- Status transition matrix tests.
- Scheduler exclusion/removal tests for scrubbed tasks.
- Migration tests.

### Web
- Form section ordering tests.
- WYSIWYG markdown round-trip tests.
- Unified selector debounce/filter/assignment tests.
- Role-based field enable/disable tests.
- Status action behavior tests.

## Phase 6: Documentation updates
- Update API docs for enum contracts and status transitions.
- Update implementation/gap-analysis docs to reflect completed work.
