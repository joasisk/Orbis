# Task Creation Rework — Gap Analysis

Date: 2026-04-30  
Scope: `docs/task_creation/*` plan set versus the current implementation in `apps/api`, `apps/web`, and tests.

## Method
- Reviewed planned behavior in:
  - `docs/task_creation/01_implementation_plan.md`
  - `docs/task_creation/02_file_by_file_execution_plan.md`
  - `docs/task_creation/03_commit_by_commit_patch_plan.md`
  - `docs/task_creation/04_first_implementation_pass.md`
- Checked implementation evidence in:
  - API schemas/models/routes/services
  - Web task/spouse UI components
  - Current API tests

---

## Status summary

| Area | Status | Notes |
|---|---|---|
| Task priority/urgency enums | ✅ Implemented | API literals, DB constraints, migration, and task UI usage exist. |
| Task status lifecycle + transition endpoint | ✅ Implemented | Direct status updates blocked; explicit transition endpoint exists. |
| Owner/spouse write-boundaries (task attributes) | ✅ Implemented | API service enforces actor-specific attribute updates. |
| Scrubbed-task scheduling exclusion | ✅ Implemented (API) | Planning/focus exclude terminal statuses including `scrubbed`. |
| Unified orbit/project selector | ⚠️ Partially implemented | Assignment control exists, but plan-specific searchable `<orbit>: <project>` behavior is not fully evident/documented. |
| Markdown-backed WYSIWYG task description | ✅ Implemented | Task modal now includes markdown authoring helpers and rendered preview while preserving markdown `notes` storage. |
| Role-aware create/edit attribute visibility in task modal | ⚠️ Partially implemented | Editability controls exist; additional visibility/UX details from plan need validation/final polish. |
| Status transition actions in task modal (no free-form edit) | ✅ Implemented | Status selection moved to explicit transition actions. |
| i18n coverage for new user text | ✅ Implemented (task modal surface) | Task-creation modal labels/actions moved to i18n keys and added to all supported locales. |
| Planning docs synchronization after implementation | ⚠️ Incomplete | Task-creation plan docs exist, but no consolidated “actual state” document was present before this file. |

---

## Detailed gaps

### G1 — Markdown WYSIWYG description editor
**Status:** Closed (implemented 2026-04-30)  
**Evidence:** Task modal now provides markdown formatting helpers (bold/italic/heading), edit/preview toggling, and rendered markdown preview while persisting to `notes` markdown text.

---

### G2 — Unified orbit/project searchable selector behavior is under-specified in implementation
**Priority:** P1  
**Planned:** One searchable dropdown showing `<orbit>: <project>` with debounced filtering over both names.  
**Current evidence:** Current task modal uses existing assignment controls, but the task-creation docs do not map to explicit implemented debounce/search UX semantics.

**Impact:**
- Potential mismatch between expected and actual assignment UX.
- Hard to verify requirement closure from docs/tests alone.

**Recommended closure:**
1. Either implement the exact planned searchable unified selector UX, or
2. Update docs to record the finalized UX choice and rationale (if intentionally simplified).
3. Add/expand web tests for search, filtering, and assignment semantics.

---

### G3 — i18n completeness for task-creation rework text
**Status:** Closed for task modal surface (implemented 2026-04-30)  
**Evidence:** Task modal task-creation labels/actions migrated to i18n keys present for all supported locales (`en`, `sk`, `de`, `it`, `es`, `pl`).

---

### G4 — Task-creation documentation package needed an explicit “actual-state” checkpoint
**Priority:** P2  
**Planned:** Keep implementation/gap docs current and non-obsolete.  
**Current evidence:** Execution plans existed, but no task-creation-specific post-pass gap snapshot.

**Impact:**
- Harder to see what is closed vs open without traversing code.

**Recommended closure:**
- Keep this file updated as implementation closes remaining items.
- When a gap closes, mark it and reference the implementing PR/commit.

---

## Proposed close order
1. **G1** (WYSIWYG markdown editor).
2. **G3** (i18n completion for all new task UI text).
3. **G2** (unified selector UX finalize + tests/documentation).
4. **G4** (ongoing docs hygiene as items close).

This ordering keeps user-facing quality and guardrail compliance ahead of lower-risk documentation polish.
