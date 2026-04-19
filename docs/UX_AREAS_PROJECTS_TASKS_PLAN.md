# UX Plan: Combined Areas + Projects Workspace and Task Management

## Status
Draft for review and iteration.

## Why this change
This plan improves the MVP capture-and-organize flow by:
- Merging **Areas of Life** and **Projects** into one workspace screen.
- Adding complete **Task management** with practical filtering.
- Introducing modal-based create/edit interactions to reduce navigation/context switching.
- Adding a global **Add Task** entry point in left navigation.

This remains within MVP scope (Areas → Projects → Tasks, low-friction UX, no extra gamification).

---

## Source traceability
- `docs/REQUIREMENTS.md`
  - “Support Areas of Life -> Projects -> Tasks”
  - Task fields and status/deadline/priority/urgency support.
- `docs/MVP_PLAN.md`
  - Core data/workflow includes Areas, Projects, Tasks.
  - MVP success requires user can capture and organize active work.
- `docs/DATA_MODELS.md`
  - Implemented editable entities/fields for `areas_of_life`, `projects`, `tasks`.

---

## Scope requested (what we will deliver)

## 1) Merge Areas + Projects into one screen
Create a unified page (suggested route: `/projects`, label: **Long Term Plan**) with:

### Layout
- **Left column:** life areas list + “Add life area” button.
- **Right column:** projects list + “Add project” button.
- Both add actions open **modals**.

### Selection and filtering behavior
- Default state: **no area selected** ⇒ show **all projects**.
- Left-click on life area item ⇒ set as selected area and filter right column to only projects with that `area_id`.
- Provide clear selected style and an optional “Clear filter” action.

### Editing behavior
- Each life area row includes right-aligned **Edit** button.
- Clicking edit opens life area modal pre-filled with current values.
- Each project row includes right-aligned **Edit** button.
- Clicking edit opens project modal pre-filled with current values.

### Editable fields (respect model)
- **Life area modal** (create/edit):
  - `name`
  - `description`
- **Project modal** (create/edit):
  - `area_id` (dropdown of all life areas)
  - `name`
  - `description`
  - `status`
  - `is_private`
  - `visibility_scope`
  - `priority`
  - `urgency`
  - `deadline`
  - `deadline_type`
  - `spouse_priority`
  - `spouse_urgency`
  - `spouse_deadline`
  - `spouse_deadline_type`

> Note: spouse influence fields remain separate from owner fields (no merging).

---

## 2) Add task management screen
Ensure there is a dedicated task management page (suggested route: `/tasks`) featuring:

### Task list and filters
List tasks with filter controls for:
- life area
- project
- priority
- urgency
- deadline (e.g., overdue / due soon / has deadline / no deadline)
- optional additional practical filters:
  - status
  - visibility_scope
  - privacy (`is_private`)

### Add task modal
- “Add task” button opens modal.
- Input sequence:
  1. Title/name (`title`)
  2. Life area dropdown
  3. Project dropdown (filtered by selected life area)
  4. Remaining editable task fields

### Task edit modal
Each task row includes an Edit action to open the same modal in edit mode with full editable fields.

### Editable task fields
- `project_id` (nullable, selected via life area/project flow)
- `title`
- `notes`
- `status`
- `is_private`
- `visibility_scope`
- `priority`
- `urgency`
- `deadline`
- `deadline_type`
- `spouse_priority`
- `spouse_urgency`
- `spouse_deadline`
- `spouse_deadline_type`

---

## 3) Global quick action in left navigation
Add **“Add Task”** button in persistent left nav so user can create tasks from any screen.

### Behavior
- Opens the exact same Add Task modal used on `/tasks`.
- Preserves any preselected context when available (optional enhancement):
  - If launched from filtered views, prefill matching area/project where valid.

---

## UX and interaction details

### Modal patterns (all create/edit modals)
- Open/close with keyboard and pointer.
- Escape closes modal (with dirty-state confirmation if changed).
- Background scroll lock while open.
- Primary CTA: Save/Create.
- Secondary CTA: Cancel.
- Inline field validation + API error region.

### Dropdown behavior
- Life area dropdown always sourced from latest areas list.
- Project dropdown behavior:
  - Disabled until life area chosen (for task create flow).
  - Shows only projects with selected `area_id`.
  - If editing existing task with no project, allow empty selection.

### Empty states
- No areas: prompt to create first life area.
- No projects for selected area: show empty state + “Add project”.
- No tasks matching filters: show “No tasks found” + clear filters action.

---

## Data/API impact
No data-model expansion required. Use existing CRUD endpoints and query/filter capabilities where available.

If current task/project list endpoints do not support needed server-side filtering, implement temporary client-side filtering first, then optimize with API query params in a follow-up.

---

## Proposed implementation phases

### Phase A — Structure and navigation
1. Merge Areas + Projects UI into one workspace page.
2. Add left-nav “Add Task” entry and shared task modal host.

### Phase B — Modal CRUD for Areas/Projects
1. Add area create/edit modals.
2. Add project create/edit modals with area dropdown.

### Phase C — Task management page
1. Build task list with filter bar.
2. Add task create/edit modal with area→project dependent dropdown logic.
3. Connect global Add Task action to same modal.

### Phase D — Polish and safeguards
1. Validation, accessibility, keyboard flows, loading states.
2. Consistent error handling and toasts/messages.
3. Regression testing for privacy/visibility/spouse influence separation.

---

## Acceptance criteria

### Combined Areas + Projects
- User sees 2-column layout: areas left, projects right.
- No area selected ⇒ all projects visible.
- Clicking area filters projects to that area.
- Area and project rows each have Edit button opening prefilled modal.
- Create/edit project uses life area dropdown (not free-text ID).

### Tasks management
- Dedicated tasks screen lists tasks.
- User can filter by life area, project, priority, urgency, deadline.
- Add Task opens modal and enforces area-first then project-from-area selection.
- Task edit modal exposes all editable task fields.

### Global action
- Left nav includes Add Task button.
- Button opens same Add Task modal from any page.

---

## Risks / open questions for review
1. **Filter scale**: if task volume is large, server-side filter params should be prioritized.
2. **Spouse roles in UI**: confirm whether spouse can edit spouse_* fields from these modals or only from dedicated influence flow.
3. **Project requirement for tasks**: current model allows `project_id = null`; confirm if UX should still allow project-less tasks after selecting life area.
4. **Route strategy**: keep `/areas` route as redirect/alias to merged workspace, or remove from nav and keep backward-compatible route.

---

## Out of scope (for now)
- Kanban/board views.
- Bulk editing.
- AI-assisted autofill in create/edit modals.
- Gamification or engagement mechanics.

