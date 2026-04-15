# Phase 0–3 Gap Analysis (Post-FE Redesign Verification)

## Scope
This review re-checks **Phase 0 through Phase 3** from `docs/IMPLEMENTATION_PLAN.md` against the current implementation after the recent web design update.

Assessment date: **2026-04-15**.

---

## Executive Summary

| Phase | Status | Readout |
|---|---|---|
| Phase 0 — Foundations | ✅ Implemented with minor operational caveat | Compose and health routes exist, lint/typecheck scripts are wired, CI exists, and ADRs are present. |
| Phase 1 — Core backend and auth | ✅ Implemented | Auth bootstrap/login/refresh/logout, owner/spouse role controls, and tests pass. |
| Phase 2 — Project and task domain | ✅ Backend complete, ⚠️ thin FE ergonomics | CRUD + dependencies + history are implemented and tested; web routes exist but are still utility CRUD shells, not polished product UX. |
| Phase 3 — Scheduling and focus workflows | ✅ Backend complete, ❌ FE workflow gap | Daily plan and focus lifecycle APIs are implemented/tested, but redesigned home UI is currently static and not wired to phase-3 actions. |

---

## Verification Commands Run

### API quality + tests
- `cd apps/api && pip install -r requirements.txt`
- `cd apps/api && ruff check app tests`
- `cd apps/api && ruff format --check app tests`
- `cd apps/api && pytest -q` ❌ fails in this environment unless `PYTHONPATH=. ` is set.
- `cd apps/api && PYTHONPATH=. pytest -q` ✅ (`8 passed`)

### Web quality checks
- `cd apps/web && npm ci`
- `cd apps/web && npm run lint`
- `cd apps/web && npm run typecheck`

---

## Phase-by-Phase Findings

## Phase 0 — Foundations

### Deliverables
1. **Repository structure in place** — ✅
2. **Docker Compose local stack running** — ✅ (configuration present in root compose)
3. **Environment strategy and secret handling** — ✅ (`.env.example` present)
4. **Coding standards, linting, formatting** — ✅ (`ruff`, `next lint`, and `tsc --noEmit` scripts + CI)
5. **Initial documentation set** — ✅
6. **Architecture decision records started** — ✅ (`docs/adr/0001`, `docs/adr/0002`)

### DoD Check
- `docker compose up` services are defined for proxy/web/api/db/redis/worker — ✅ (config-level verification)
- API + web health endpoints exist — ✅ (`/health`, `/api/v1/health`, `/api/health`)

### Remaining Gap
- **Test runner ergonomics:** `pytest -q` from `apps/api` requires `PYTHONPATH=.`, which should be made explicit in project test docs or pytest config.

---

## Phase 1 — Core backend and auth

### Deliverables + DoD
All listed phase-1 deliverables remain implemented and covered by integration tests:
- owner bootstrap/login/logout/refresh
- protected route checks
- owner/spouse role enforcement

### Remaining Gap
- Minor: broaden negative-path authz tests for edge-case endpoints (nice-to-have, not DoD blocker).

---

## Phase 2 — Project and task domain

### Deliverables + DoD
Implemented in API and tests:
- Areas, Projects, Tasks, Recurring Commitments CRUD
- Task dependency graph + cycle prevention
- Privacy and spouse influence fields
- Version/history API

Web requirement for list/detail pages is technically met via `/tasks`, `/tasks/[id]`, `/projects`, `/projects/[id]`.

### Remaining Gaps
1. **Productized FE gap (post redesign):** primary redesigned landing page is presentation-heavy and not wired to phase-2 operational workflows.
2. **CRUD UX depth:** edit/delete/dependency management remains API-centric and utility-level in FE.

---

## Phase 3 — Scheduling and focus workflows

### Deliverables
Implemented in backend + tests:
- Daily plan endpoint
- Focus actions (`start`, `stop`, `sidetrack`, `unable`)
- Blocker taxonomy capture
- Pre/post energy capture
- Overload heuristic signals

### DoD Assessment
- **User can ask what to do now** — ⚠️ API yes, FE no direct integrated flow in redesigned shell.
- **User can track a task session** — ⚠️ API yes, FE action flow not surfaced in redesigned home experience.
- **User can record blockers quickly** — ⚠️ API yes, FE quick-capture flow absent in redesigned home.

### Critical Gap (Post-FE redesign)
The new homepage UI currently shows static timeline/brief/suggestions content and does not call phase-3 endpoints, creating a **backend/UX disconnect** for daily usage.

---

## Recommended Remediation Order

1. **Phase 3 FE wiring (highest priority):** connect redesigned home experience to daily-plan + focus actions + blocker/energy prompts.
2. **Phase 2 FE completion:** add edit/delete/dependency flows within the same updated design system.
3. **Test ergonomics fix:** remove need for manual `PYTHONPATH=. ` when running API tests locally.

---

## Overall Readout

- Backend implementation for phases 0–3 is substantially complete and validated by passing tests/lint/typecheck.
- The largest current risk after the FE redesign is **phase-3 usability**, not backend capability: users cannot reliably execute the “do now → focus → blocker/energy” loop from the new primary web experience.
