# Phase 0–3 Gap Analysis (Documentation vs Implementation)

## Scope
This analysis compares commitments in `docs/IMPLEMENTATION_PLAN.md` for **Phase 0 through Phase 3** against the current codebase implementation across infrastructure, API, data model, web app, and tests.

Assessment date: **2026-04-15**.

---

## Executive Summary

| Phase | Status | Summary |
|---|---|---|
| Phase 0 — Foundations | ⚠️ Partially complete | Repo, compose stack, env strategy, docs, and architecture baseline are present; explicit coding standards/lint pipeline and ADR trail are not yet established. |
| Phase 1 — Core backend and auth | ✅ Mostly complete | Auth/login/logout/refresh, role checks, spouse creation flow, and audit events exist with integration tests. |
| Phase 2 — Project and task domain | ⚠️ Mostly complete | Core entities, CRUD APIs, dependency cycle checks, history model, and web task/project list/detail exist; some policy and UX completion gaps remain. |
| Phase 3 — Scheduling and focus workflows | ⚠️ Substantially implemented, not fully DoD-complete | Daily plan, focus start/stop/sidetrack/unable endpoints, blocker/energy capture, overload heuristics, and API tests exist; web Phase 3 UX and “what to do now” product polish remain incomplete. |

---

## Phase 0 — Foundations

### Deliverables

1. **Repository structure in place**  
   **Status:** ✅ Implemented  
   **Evidence:** Monorepo layout with `apps/api`, `apps/web`, `docs`, `infra` and compose root is present.

2. **Docker Compose local stack running**  
   **Status:** ✅ Implemented (configuration present)  
   **Evidence:** `docker-compose.yml` defines `proxy`, `web`, `api`, `db`, `redis`, `worker` services.

3. **Environment strategy and secret handling**  
   **Status:** ✅ Implemented (baseline)  
   **Evidence:** `.env.example` documents required variables and secrets placeholders; README quickstart uses env bootstrap.

4. **Coding standards, linting, formatting**  
   **Status:** ❌ Not fully implemented  
   **Gap:** No root lint/format config was found for Python or web stack and `apps/web/package.json` does not expose lint/typecheck scripts.

5. **Initial documentation set**  
   **Status:** ✅ Implemented  
   **Evidence:** Architecture, requirements, implementation, repo structure, and agent-guidance docs are present.

6. **Architecture decision records started**  
   **Status:** ❌ Not implemented  
   **Gap:** No ADR directory/files were found; documentation references ADR practice but no initial ADR records are present.

### Definition of Done

- **DoD: `docker compose up` starts proxy, web, api, db, redis, worker**  
  **Status:** ✅ Config-level complete (runtime not re-verified in this pass).
- **DoD: health endpoints exist for api and web**  
  **Status:** ✅ Implemented (`/health`, `/api/v1/health`, and Next.js `/api/health`).

### Phase 0 Gaps

1. Add explicit lint/format/typecheck standards and scripts (at minimum: Python lint+format and web lint+typecheck).
2. Add CI workflow to enforce these checks.
3. Add first ADR entries (architecture baseline and auth/role model rationale).

---

## Phase 1 — Core backend and auth

### Deliverables

1. **FastAPI app bootstrapped** — ✅ Implemented.
2. **PostgreSQL connection and migrations** — ✅ Implemented (SQLAlchemy + Alembic revisions).
3. **Auth model (owner/spouse roles)** — ✅ Implemented (role enum + DB check constraint + spouse creation endpoint).
4. **Secure password auth** — ✅ Implemented (hashed password verification).
5. **Refresh token flow** — ✅ Implemented (refresh-session rotation and revoke on use).
6. **API auth middleware** — ✅ Implemented (JWT bearer dependency and role guards).
7. **Audit log model starter** — ✅ Implemented (audit events on key auth actions).

### Definition of Done

- **Login/logout works** — ✅ Implemented.
- **Protected endpoint works** — ✅ Implemented (`/users/me`).
- **Roles enforce access** — ✅ Implemented (`owner-only`, `household`, and owner-gated spouse creation).

### Residual Phase 1 Gaps

1. Add explicit integration assertions for spouse restrictions vs owner-only endpoints (broader negative-path coverage).
2. Consider invite-based spouse onboarding (email invite/activation) if required by product policy.

---

## Phase 2 — Project and task domain

### Deliverables

1. **Areas of Life** — ✅ Implemented (model + CRUD).
2. **Projects** — ✅ Implemented (model + CRUD + visibility/privacy fields).
3. **Tasks** — ✅ Implemented (model + CRUD + priority/urgency/deadline fields).
4. **Recurring commitments** — ✅ Implemented (list/create/get/update/delete).
5. **Task dependencies** — ✅ Implemented with cycle detection and delete/list/create flows.
6. **Privacy flags + owner/spouse influence inputs** — ✅ Implemented in API/data model.
7. **History/versioning model** — ✅ Implemented (entity version writes on create/update/delete + read endpoint).

### Definition of Done

- **API CRUD for all core entities** — ✅ Implemented (including recurring commitment detail route).
- **Task/project list and detail pages in web app** — ✅ Implemented (phase-2 CRUD shell).
- **Version entries created on meaningful changes** — ⚠️ Partially implemented; changes are logged, but “meaningful” policy remains implicit rather than documented.

### Residual Phase 2 Gaps

1. Formalize “meaningful change” policy per entity and align version logging expectations/tests.
2. Expand UI beyond create/list/detail into complete edit/delete/dependency-management workflows (currently API-first completeness exceeds UX completeness).
3. Strengthen authorization/privacy matrix tests for spouse visibility edge cases across all entities.

---

## Phase 3 — Scheduling and focus workflows

### Deliverables

1. **Daily plan concept** — ✅ Implemented (ranked recommendations, score breakdown, primary + fallback recommendations).
2. **Focus mode endpoint and actions (start/stop/sidetrack/unable)** — ✅ Implemented.
3. **Blocker reason tracking** — ✅ Implemented (taxonomy constraint + blocker event persistence).
4. **Energy input before/after task** — ✅ Implemented (required pre-task and post-task inputs in respective endpoints).
5. **Overload detection v1** — ⚠️ Implemented at baseline heuristic level; present but still simple.

### Definition of Done

- **User can ask system what to do now** — ⚠️ Partially complete (API exists; web phase-3 daily-plan UX is not yet delivered).
- **User can track a task session** — ✅ Implemented in API.
- **User can record blockers quickly** — ✅ Implemented in API.

### Residual Phase 3 Gaps

1. Build Phase 3 web UX (daily “Do now”, start/stop/sidetrack/unable controls, blocker/energy prompts).
2. Evolve overload heuristics and tune thresholds from observed usage data.
3. Add end-to-end tests that cover the full loop from recommendation → session flow → updated recommendations.

---

## Priority Remediation Plan (Cross-Phase)

1. **Phase 0 hardening first:** add lint/format/typecheck standards + CI enforcement + seed ADRs.
2. **Phase 3 usability second:** implement web UX for daily plan and focus flows so backend capability is user-accessible.
3. **Phase 2/3 quality third:** expand integration/E2E test matrix for visibility, authorization, and scheduling behavior regression coverage.
4. **Policy clarity fourth:** document “meaningful versioning change” semantics and overload heuristic contract.

---

## Overall Readout

- The implementation appears to have progressed **beyond older phase-specific gap docs** in several areas, especially for Phase 1 and Phase 3 backend capability.
- Current risk is less about missing core backend endpoints and more about **operational rigor (Phase 0 guardrails)** and **user-facing completion (Phase 3 web workflow)**.
