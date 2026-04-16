# Current Status and Progress Draft (Documentation-Aligned)

Assessment date: **2026-04-16**.

This draft evaluates implementation status against the canonical documentation order:
1. `docs/REQUIREMENTS.md`
2. `docs/MVP_PLAN.md`
3. `docs/IMPLEMENTATION_PLAN.md`
4. `docs/ARCHITECTURE.md`

---

## Executive summary

The repository appears to be **through Phase 4 backend baseline** with **Phase 3+4 web integration partially complete**.

- **Backend:** Strong progress through Phases 1–4 with passing lint/tests and coverage for auth, phase-2 CRUD/history, phase-3 daily plan/focus flows, and phase-4 weekly proposal + note extraction workflows.
- **Frontend:** Phase 2 CRUD pages exist and a Phase 3 UI component exists, but the default homepage is currently a static design shell and does not mount that Phase 3 workflow by default.
- **MVP risk:** Core MVP workflows are mostly implemented at API level; biggest remaining delivery risk is cohesive day-to-day UX wiring (especially making “do-now -> focus actions -> blocker/energy capture” a first-class user path).

---

## Evidence snapshot (checks run)

### API checks
- `cd apps/api && ruff check app tests` -> pass.
- `cd apps/api && PYTHONPATH=. pytest -q` -> pass (`13 passed`).

### Web checks
- `cd apps/web && npm run lint` -> pass.
- `cd apps/web && npm run typecheck` -> pass.

---

## Progress against implementation phases

## Phase 0 — Foundations
**Status:** ✅ Complete

- Monorepo structure, docs set, and ADRs are present.
- Tooling and quality gates are functional (ruff, next lint, typecheck).
- Architecture doc still aligns with API-first boundaries.

## Phase 1 — Core backend and auth
**Status:** ✅ Complete

- Auth flow coverage exists in tests (`test_phase1_auth_flow.py`).
- Owner/spouse role model and protected flows are implemented and validated by tests.

## Phase 2 — Project/task domain
**Status:** ✅ Complete for baseline MVP scope

- API surfaces areas/projects/tasks/recurring commitments/dependencies/history.
- Prior known gaps (e.g., recurring commitment detail endpoint, dependency cycle validation) now appear implemented.
- CRUD/history integration tests exist and pass.
- Web includes project and task list/detail routes.

## Phase 3 — Scheduling and focus workflows
**Status:** ⚠️ Backend complete; web exposure partially wired

- Daily plan API exists and is tested.
- Focus lifecycle endpoints (`start/stop/sidetrack/unable`) exist and are tested.
- Blocker taxonomy and overload fields are present in phase-3 models/schemas/tests.
- A `Phase3Home` web component exists and calls these endpoints.
- **Gap:** root homepage currently renders a static shell and does not mount `Phase3Home`, so the primary route does not expose this behavior by default.

## Phase 4 — AI planning engine
**Status:** ✅ Baseline implemented

- Weekly proposal generate/get/approve endpoints are present.
- Note extraction preview/decision endpoints are present.
- API tests validate weekly proposal and note extraction accept flow.
- Approval gate behavior is represented in API surface (proposal then approve).

## Phase 5 — Calendar and reminders
**Status:** ❌ Not yet delivered (or not evidenced in current checks)

- No verified end-to-end implementation evidence collected in this assessment for calendar read/write adapter and reminder worker behavior.

## Phase 6 — Wife visibility and influence UX
**Status:** ⚠️ Data model support present; dedicated spouse UX maturity unclear

- Spouse influence fields exist in phase-2 data model.
- A dedicated spouse-facing dashboard/experience is not yet confirmed in this assessment.

## Phase 7 — Hardening and TrueNAS packaging
**Status:** ⚠️ Partial

- Core local stack and architecture are in place.
- Production hardening criteria (backup/restore validation, rate limiting/API keys, TrueNAS-ready deployment proof) were not re-verified in this pass.

---

## Progress against MVP capabilities (from `docs/MVP_PLAN.md`)

- **Project/task tracking:** ✅ Implemented (API + web baseline pages).
- **AI weekly planning:** ✅ Implemented at baseline workflow level (proposal + approval endpoints + tests).
- **Reminders:** ❌ Not yet verified as implemented.
- **Focus mode:** ⚠️ Implemented in backend and component-level web UI, but not surfaced as default homepage experience.
- **Wife visibility:** ⚠️ Partial evidence via data model/permissions; full UX still needs explicit verification.

---

## Architecture alignment check (`docs/ARCHITECTURE.md`)

- API-first split remains intact: domain logic is centered in `apps/api`, with web mostly consuming APIs.
- No evidence in this assessment of boundary violations that move core orchestration into web handlers.
- Current gap is not architecture mismatch; it is UX integration completeness.

---

## Updated next-step plan (with intermediate catch-up phase)

1. **Phase 4.5 (new) — Web catch-up + settings interface**
   - Make `/` API-backed and remove static dead-end behavior.
   - Fetch and render core domain data in default user flows:
     - Areas of Life
     - Projects
     - Tasks
   - Fetch and render scheduling context:
     - daily plan (“what to do now”)
     - weekly schedule/proposal context
   - Make focus/task execution actions easy to access from the default route.
   - Implement a settings interface for MVP operations:
     - profile/session basics
     - reminder preferences
     - calendar and notes integration connection/config status
     - AI planning controls that keep approval gates intact

2. **Phase 5 — Calendar + reminder delivery completion**
   - Finish/verify first calendar adapter read/write path.
   - Implement reminder worker delivery + response logging loop.
   - Validate that accepted plan items can become soft calendar blocks.

3. **Phase 6 — Spouse visibility UX completion**
   - Add/verify spouse-facing dashboard flows for relevant schedule context.
   - Validate private-item suppression in all spouse-visible views.
   - Validate influence UX and weighting behavior without overriding owner data.

4. **Phase 7 — Hardening and deployment proof**
   - Add repeatable backup/restore verification.
   - Add baseline operational/security checks (rate limiting, API key flow where applicable).
   - Produce deployment runbook validation for TrueNAS target.

5. **Tracking update**
   - Add a concise MVP status matrix in docs with links to implemented endpoints/pages and explicit pending items.

---

## Delivery confidence

- **High confidence:** phases 1–4 backend baseline capabilities exist and pass automated checks.
- **Medium confidence:** end-user day-to-day workflow polish in web (especially focus-first entry experience).
- **Lower confidence:** phase 5+ operational features, pending explicit implementation/verification evidence.
