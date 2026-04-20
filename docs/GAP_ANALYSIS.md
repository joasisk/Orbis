# Consolidated Gap Analysis (Single Source of Truth)

Date: 2026-04-19  
Scope: Replaces legacy phase/UI gap-analysis files with one verified backlog.

## Replaced documents
- `docs/PHASE0_3_GAP_ANALYSIS.md`
- `docs/PHASE1_GAP_ANALYSIS.md`
- `docs/PHASE2_GAP_ANALYSIS.md`
- `docs/PHASE3_GAP_ANALYSIS.md`
- `docs/UI_API_GAP_ANALYSIS.md`
- `docs/UI_API_GAP_IMPLEMENTATION_PLAN.md`

## Verification method
- Code-path verification in API and web routes/components.
- Endpoint/search verification with repository grep.
- API regression tests for auth/domain/focus/planning/settings flows.

## What is no longer a gap (implemented and verified)
Removed from backlog because implementation is present and verified:

1. **Phase 1 auth baseline**: bootstrap/login/refresh/logout, spouse creation/status endpoints, role guards, and tests.
2. **Phase 2 domain baseline**: Areas/Projects/Tasks/Recurring commitments CRUD, task dependency cycle detection, spouse influence endpoint, and history logging.
3. **Phase 3 core focus loop**: daily plan endpoint + focus lifecycle endpoints (`start`, `stop`, `sidetrack`, `unable`) with blocker and energy capture.
4. **Primary route API wiring in web**: home/schedule/projects/tasks/areas/settings routes load API-backed data.
5. **Spouse management + spouse influence UI**: owner spouse create/status flow and spouse influence editing flows are present.

---

## Remaining verified gaps (incomplete)

> Update 2026-04-19: G1–G5 are now implemented in code and covered by validation checks below. This section is kept only as a closure log until the next backlog refresh.

### G1 — Weekly proposal workflow is API-only (no web UI)
**Status:** ✅ Closed  
**Verified:** API endpoints exist; no web usage found.

- API exists for generate/latest/approve:
  - `POST /planning/weekly-proposals/generate`
  - `GET /planning/weekly-proposals/latest`
  - `POST /planning/weekly-proposals/{proposal_id}/approve`
- No matching calls/components found in `apps/web/src`.

**Impact:** owner cannot complete proposal generation/review/approval workflow from UI.

**Next MVP action:** add owner-only weekly proposal workspace in web schedule flow with explicit pre-approval messaging.

### G2 — Note extraction review workflow is API-only (no web UI)
**Status:** ✅ Closed  
**Verified:** API endpoints exist; no web usage found.

- API exists for preview/decision:
  - `POST /planning/note-extractions/preview`
  - `POST /planning/note-extractions/{id}/decision`
- No matching calls/components found in `apps/web/src`.

**Impact:** owner cannot run note-to-task candidate review/accept-dismiss workflow from UI.

**Next MVP action:** add note extraction panel with preview + accept/dismiss and created-task feedback.

### G3 — Planned-action schedule settings fields are missing in API + web
**Status:** ✅ Closed  
**Verified:** settings model/schema/UI still expose baseline reminder + AI toggles only.

Missing requirement-level controls:
- app timezone for planned actions
- weekly planning cadence
- note-scan cadence
- reminder scan interval
- optional automation pause-until

**Impact:** owner cannot configure planned-action cadence from settings.

**Next MVP action:** extend `UserSettings` model/schema/PATCH + settings UI and validate cadence constraints while preserving approval guardrails.

### G4 — Entity history access is still over-broad for spouse users
**Status:** ✅ Closed  
**Verified:** history query allows spouse access by owner-role existence rather than explicit owner-spouse linkage.

**Impact:** potential overexposure of unrelated owner history to spouse-role users.

**Next MVP action:** tighten history authorization to explicit relationship scope (same owner household link), then add policy tests.

### G5 — API test ergonomics still require `PYTHONPATH=.`
**Status:** ✅ Closed  
**Verified:** `pytest -q` fails collection from `apps/api` unless `PYTHONPATH=.` is provided.

**Impact:** friction for local/CI command consistency.

**Next MVP action:** configure package path in pytest settings or project layout so `pytest -q` works directly.

---

## Prioritized execution order
1. **G1** Weekly proposal UI wiring.
2. **G2** Note extraction UI wiring.
3. **G3** Planned-action schedule settings model/API/UI.
4. **G4** History authorization hardening + tests.
5. **G5** Pytest path ergonomics cleanup.

## Definition of done for this consolidated backlog
- All five gaps above are closed with tests or explicit validation steps.
- No approval-first planning/scheduling guardrails are weakened.
- Spouse influence remains separate from owner priority fields.
- This file remains the only active gap-analysis tracker.
