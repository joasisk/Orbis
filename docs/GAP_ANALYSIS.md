# MVP Gap Analysis (Current)

Date: 2026-04-20  
Scope: Gap analysis against `docs/REQUIREMENTS.md` + `docs/MVP_PLAN.md` with implementation evidence from API/web code and current automated checks.

## Verification method
- Reviewed MVP source-of-truth docs and implementation plan alignment.
- Verified implemented surfaces in:
  - `apps/api/app` + `apps/api/tests`
  - `apps/web/src/app` + `apps/web/src/components`
- Re-ran baseline checks:
  - API: `pytest -q` (`29 passed`)
  - Web: `npm run lint`, `npm run typecheck`

---

## MVP capability status matrix

### 1) Project/task tracking
**Status:** ✅ Implemented (MVP-ready baseline)

- Areas/Projects/Tasks/Recurring commitments + history and influence fields are implemented in API and surfaced in web CRUD workflows.
- Regression tests cover core domain flow and history scope behavior.

### 2) AI weekly planning with approval gate
**Status:** ✅ Implemented (MVP-ready baseline)

- Proposal generation/review/approval endpoints exist.
- Weekly proposal controls are wired in web schedule dashboard.
- Manual approval gate is preserved (no silent schedule commit path).

### 3) Focus mode + daily execution actions
**Status:** ✅ Implemented (MVP-ready baseline)

- Daily plan endpoint and focus actions (`start`, `stop`, `sidetrack`, `unable`) are implemented and tested.
- Home dashboard exposes “do now” + focus actions and day-item telemetry updates.

### 4) Reminder model
**Status:** ✅ Implemented (backend baseline)

- Reminder/event models and services are implemented with response logging.
- Reminder behavior is covered in planning/reminder tests.

### 5) Calendar integration (read + scheduled write)
**Status:** ✅ Implemented (MVP baseline)

- Calendar adapter path exists.
- Accepted schedule items can be exported as soft calendar blocks.

### 6) Notes ingestion path
**Status:** ✅ Implemented (MVP baseline)

- Note extraction preview + decision APIs exist.
- Web schedule dashboard includes review/accept/dismiss workflow.

### 7) Spouse visibility + influence
**Status:** ⚠️ Mostly implemented; one UX gap remains

- Spouse dashboard exists with accepted-schedule visibility and private-item filtering semantics.
- Spouse influence editing exists in spouse dashboard, but quick-edit currently exposes only `spouse_priority` and `spouse_urgency` there.
- Requirement-level spouse deadline influence is supported in domain payloads but not fully represented in spouse dashboard quick-edit UX.

### 8) Self-host/deploy baseline (TrueNAS-oriented)
**Status:** ⚠️ Functionally prepared; live deploy proof still environment-dependent

- Hardening docs/scripts and tests exist (backup/restore, rate limiting, API keys).
- Live TrueNAS deployment verification remains a final environment execution step.

---

## Remaining prioritized gaps (near-MVP)

### G1 — Spouse dashboard quick-edit does not include spouse deadline fields
**Priority:** P0 (MVP requirement-fit)

**Current evidence:**
- Spouse dashboard quick edit handles only `spouse_priority` and `spouse_urgency` updates.
- Spouse deadline fields are present in domain models/forms elsewhere, but not in this primary spouse-facing flow.

**Impact:**
- The “wife importance + deadline inputs” requirement is only partially satisfied in the default spouse dashboard experience.

**Recommended closure:**
- Add spouse dashboard controls for `spouse_deadline` + `spouse_deadline_type` (with validation and clear save/error states).
- Add/extend API integration tests for spouse-role deadline influence updates through the same flow.

### G2 — App settings UX is behind API capabilities for planned-action cadence
**Priority:** P1 (MVP usability/completion)

**Current evidence:**
- API/settings schemas and tests include cadence/timezone fields (`app_timezone`, weekly planning cadence/time, note scan cadence, reminder scan interval, automation pause).
- Settings web screen currently emphasizes integration toggles/audit/spouse management and does not expose full cadence controls.

**Impact:**
- Owner cannot fully tune planning/reminder/scan behavior from UI despite backend support.

**Recommended closure:**
- Extend settings UI to include existing API-backed cadence fields and validation messages.
- Keep approval-first guardrail messaging visible when automation is toggled.

### G3 — Production validation step for TrueNAS packaging remains open
**Priority:** P2 (release-readiness)

**Current evidence:**
- Scripts/tests/docs cover hardening baseline.
- Final live TrueNAS runbook execution is not yet documented as completed.

**Impact:**
- Residual deployment risk at MVP handoff.

**Recommended closure:**
- Run/record one full TrueNAS deployment verification pass (install, health, backup/restore smoke, auth rate-limit smoke).

---

## Suggested MVP-close sequence
1. **Close G1** (spouse deadline quick-edit parity in spouse dashboard).
2. **Close G2** (settings cadence controls UI).
3. **Close G3** (live TrueNAS proof and evidence capture).

With these three items completed, MVP scope should be considered materially closed for release-candidate quality.
