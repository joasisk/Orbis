# GitHub Roadmap and Issue Backlog

This roadmap translates the existing planning docs into an actionable GitHub issue backlog.

Sources used:
- `docs/REQUIREMENTS.md`
- `docs/MVP_PLAN.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `README.md`

## Milestones (suggested)

1. **M1 — Auth + Core Domain**
2. **M2 — Scheduling + Focus**
3. **M3 — AI Planning + Notes**
4. **M4 — Calendar + Reminders**
5. **M5 — Wife Visibility + Influence**
6. **M6 — Hardening + TrueNAS Packaging**

---

## Priority roadmap (now -> later)

### Now (next 2–4 weeks)
- Finalize auth/session hardening and audit trail completeness.
- Implement Area/Project/Task data model + CRUD.
- Ship first web app shell for task/project list + detail.

### Next
- Build daily planning and focus session workflow.
- Add blocker and energy feedback loops.
- Introduce weekly AI proposal engine + approval flow.

### Later
- Calendar adapter and reminder worker.
- Wife-facing dashboard and influence weighting.
- Deployment hardening, backup/restore, and TrueNAS packaging.

---

## GitHub issues (ready to create)

> Format below is designed to be pasted directly into GitHub issues.

## Epic 1: Auth and security baseline

### Issue 1 — Harden refresh-token rotation and session revocation
- **Type:** Feature
- **Labels:** `backend`, `auth`, `security`, `priority:P0`
- **Milestone:** `M1 — Auth + Core Domain`
- **Depends on:** existing auth bootstrap

**Description**
Complete refresh-token rotation guarantees and add explicit session revocation controls (single session + all sessions).

**Acceptance Criteria**
- Refresh tokens are one-time use and rotated on refresh.
- Reuse of an old refresh token is detected and invalidated.
- User can revoke one session and all sessions.
- Audit events are written for refresh + revoke actions.

---

### Issue 2 — Add role-based access guardrails for owner/spouse flows
- **Type:** Feature
- **Labels:** `backend`, `auth`, `access-control`, `priority:P0`
- **Milestone:** `M1 — Auth + Core Domain`
- **Depends on:** Issue 1

**Description**
Enforce role constraints in API routes to support owner and spouse access patterns.

**Acceptance Criteria**
- Role checks are centralized and reusable.
- Protected endpoints deny unauthorized role access.
- Integration tests cover owner-only, spouse-visible, and forbidden cases.

---

### Issue 3 — Expand audit logging model and event coverage
- **Type:** Feature
- **Labels:** `backend`, `security`, `audit`, `priority:P1`
- **Milestone:** `M1 — Auth + Core Domain`
- **Depends on:** Issue 2

**Description**
Ensure meaningful user and AI-triggered actions are audit logged for traceability.

**Acceptance Criteria**
- Audit event schema captures actor, action, entity, before/after summary, timestamp.
- Auth + task mutation endpoints emit audit events.
- API includes an owner-only audit query endpoint with pagination.

---

## Epic 2: Project/task domain MVP

### Issue 4 — Implement Areas of Life data model and CRUD API
- **Type:** Feature
- **Labels:** `backend`, `domain`, `priority:P0`
- **Milestone:** `M1 — Auth + Core Domain`
- **Depends on:** Issue 2

**Description**
Create Areas as top-level planning buckets with CRUD endpoints.

**Acceptance Criteria**
- DB model + migration created.
- REST endpoints for create/list/get/update/archive.
- Validation rules documented and tested.

---

### Issue 5 — Implement Projects data model and CRUD API
- **Type:** Feature
- **Labels:** `backend`, `domain`, `priority:P0`
- **Milestone:** `M1 — Auth + Core Domain`
- **Depends on:** Issue 4

**Description**
Create Projects under Areas with status, priority, deadline metadata.

**Acceptance Criteria**
- DB model + migration created.
- CRUD endpoints support owner scope and privacy metadata.
- Project list supports filtering by area/status/priority.

---

### Issue 6 — Implement Tasks data model and CRUD API
- **Type:** Feature
- **Labels:** `backend`, `domain`, `priority:P0`
- **Milestone:** `M1 — Auth + Core Domain`
- **Depends on:** Issue 5

**Description**
Create task model with effort, energy, dependencies, deadlines, and recurrence links.

**Acceptance Criteria**
- DB model + migration created.
- CRUD endpoints include status transitions.
- Dependency and recurrence references validated.
- Soft vs hard deadline fields supported.

---

### Issue 7 — Add task/project version history tracking
- **Type:** Feature
- **Labels:** `backend`, `domain`, `history`, `priority:P1`
- **Milestone:** `M1 — Auth + Core Domain`
- **Depends on:** Issue 6

**Description**
Track meaningful changes to projects/tasks for explainability and rollback context.

**Acceptance Criteria**
- Version/event table for task/project mutations exists.
- Changes persist diff summary for key fields.
- API endpoints expose history timeline.

---

### Issue 8 — Build web UI: Areas/Projects/Tasks list + detail shell
- **Type:** Feature
- **Labels:** `frontend`, `ux`, `priority:P0`
- **Milestone:** `M1 — Auth + Core Domain`
- **Depends on:** Issues 4–6

**Description**
Deliver initial authenticated web shell for browsing and editing core entities.

**Acceptance Criteria**
- Navigation includes Areas, Projects, Tasks.
- List and detail pages can read/write data via API.
- Basic empty/loading/error states implemented.

---

## Epic 3: Scheduling and focus workflows

### Issue 9 — Implement daily plan generation endpoint (rules-based v1)
- **Type:** Feature
- **Labels:** `backend`, `planning`, `priority:P1`
- **Milestone:** `M2 — Scheduling + Focus`
- **Depends on:** Issue 6

**Description**
Create deterministic daily plan endpoint as precursor to AI-assisted planning.

**Acceptance Criteria**
- Endpoint returns ranked "next best tasks" using deadlines/priority/energy.
- Hard commitments are never overridden.
- Response explains ranking factors.

---

### Issue 10 — Build focus mode actions (start/stop/sidetrack/unable)
- **Type:** Feature
- **Labels:** `backend`, `frontend`, `focus-mode`, `priority:P0`
- **Milestone:** `M2 — Scheduling + Focus`
- **Depends on:** Issues 8–9

**Description**
Implement session-based focus actions and UX for rapid execution tracking.

**Acceptance Criteria**
- API endpoints for start/stop/sidetrack/unable are implemented.
- UI supports one-click action flow.
- Session duration and reason metadata are stored.

---

### Issue 11 — Add blocker taxonomy + energy check-in capture
- **Type:** Feature
- **Labels:** `backend`, `frontend`, `planning-signals`, `priority:P1`
- **Milestone:** `M2 — Scheduling + Focus`
- **Depends on:** Issue 10

**Description**
Capture blocker reasons and pre/post energy to improve scheduling decisions.

**Acceptance Criteria**
- Blocker reason enum includes documented failure causes.
- Energy inputs are required where specified.
- Data is queryable for planning jobs.

---

## Epic 4: AI planning and notes ingestion

### Issue 12 — Implement AI provider abstraction layer
- **Type:** Feature
- **Labels:** `backend`, `ai`, `architecture`, `priority:P0`
- **Milestone:** `M3 — AI Planning + Notes`
- **Depends on:** Issue 11

**Description**
Create provider-agnostic interface for LLM-based planning workflows.

**Acceptance Criteria**
- Unified interface supports at least 2 providers.
- Provider config is environment-driven.
- Requests/responses are logged with safe redaction.

---

### Issue 13 — Add weekly planning job + approval workflow
- **Type:** Feature
- **Labels:** `backend`, `ai`, `worker`, `priority:P0`
- **Milestone:** `M3 — AI Planning + Notes`
- **Depends on:** Issue 12

**Description**
Generate Sunday proposal and require explicit approval before applying schedule changes.

**Acceptance Criteria**
- Scheduled worker creates weekly proposal at configured time.
- Proposal can be accepted/edited/rejected.
- No schedule mutation occurs without explicit approval.

---

### Issue 14 — Implement note import and candidate task extraction pipeline
- **Type:** Feature
- **Labels:** `backend`, `ai`, `integrations`, `priority:P1`
- **Milestone:** `M3 — AI Planning + Notes`
- **Depends on:** Issue 12

**Description**
Ingest selected notes and extract candidate projects/tasks linked to source context.

**Acceptance Criteria**
- Manual note import endpoint available.
- Extraction creates suggestions (not auto-committed items).
- User can accept/edit/dismiss suggestions.
- Source-note reference is preserved.

---

## Epic 5: Calendar and reminders

### Issue 15 — Ship first calendar adapter (read + soft-block write)
- **Type:** Feature
- **Labels:** `backend`, `integrations`, `calendar`, `priority:P1`
- **Milestone:** `M4 — Calendar + Reminders`
- **Depends on:** Issue 13

**Description**
Integrate one calendar provider for commitment import and planned task block export.

**Acceptance Criteria**
- External events are read into planning context.
- Accepted plan items can be written as soft blocks.
- Existing hard commitments are protected.

---

### Issue 16 — Implement adaptive reminder scheduler + delivery logging
- **Type:** Feature
- **Labels:** `backend`, `worker`, `reminders`, `priority:P1`
- **Milestone:** `M4 — Calendar + Reminders`
- **Depends on:** Issue 10

**Description**
Create reminder engine that adapts based on user interaction patterns.

**Acceptance Criteria**
- Reminder schedule model supports throttle windows.
- Delivery + response events are logged.
- User settings allow reminder tone and frequency controls.

---

## Epic 6: Wife visibility and influence

### Issue 17 — Build spouse dashboard with private-item filtering
- **Type:** Feature
- **Labels:** `frontend`, `backend`, `privacy`, `priority:P1`
- **Milestone:** `M5 — Wife Visibility + Influence`
- **Depends on:** Issues 2, 8

**Description**
Create spouse-facing view of visible schedule items with strict privacy filtering.

**Acceptance Criteria**
- Spouse sees only visibility-allowed items.
- Private items are fully hidden/redacted from spouse view.
- API and UI tests validate privacy boundaries.

---

### Issue 18 — Add spouse influence inputs + weighted planning rules
- **Type:** Feature
- **Labels:** `backend`, `planning`, `family-workflow`, `priority:P1`
- **Milestone:** `M5 — Wife Visibility + Influence`
- **Depends on:** Issues 13, 17

**Description**
Allow spouse to submit importance/deadline influence signals that affect planning weights.

**Acceptance Criteria**
- Influence inputs stored separately from owner priority fields.
- Weighting applies more strongly to critical household/family items.
- Owner can review influence impact in plan rationale.

---

## Epic 7: Hardening and deployment

### Issue 19 — Add backup/export + restore verification scripts
- **Type:** Feature
- **Labels:** `devops`, `data`, `reliability`, `priority:P1`
- **Milestone:** `M6 — Hardening + TrueNAS Packaging`
- **Depends on:** Issue 6

**Description**
Provide repeatable data export/import workflow for homelab reliability.

**Acceptance Criteria**
- Backup scripts cover DB and critical config.
- Restore procedure is documented and tested in clean environment.
- Verification checklist confirms data integrity.

---

### Issue 20 — Production hardening: rate limits, API keys, observability baseline
- **Type:** Feature
- **Labels:** `backend`, `security`, `observability`, `priority:P1`
- **Milestone:** `M6 — Hardening + TrueNAS Packaging`
- **Depends on:** Issues 3, 19

**Description**
Prepare production baseline for secure, stable self-hosted operation.

**Acceptance Criteria**
- API rate limiting in place for sensitive endpoints.
- API key flow exists for external first-party/third-party clients.
- Minimal metrics/logging dashboards and alerts documented.

---

## Suggested issue creation order (first sprint)
1. #1 Refresh/session hardening
2. #2 Role guardrails
3. #4 Areas CRUD
4. #5 Projects CRUD
5. #6 Tasks CRUD
6. #8 Web list/detail shell

This sequence gives a usable vertical slice quickly while preserving security and future planning workflows.
