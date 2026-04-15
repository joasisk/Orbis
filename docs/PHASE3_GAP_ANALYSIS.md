# Phase 3 Gap Analysis (Documentation vs Implementation)

## Scope
Compared **Phase 3 — Scheduling and focus workflows** commitments in `docs/IMPLEMENTATION_PLAN.md` and `docs/PHASE3_WORK_PLAN.md` against the current implementation across API, data model, web UI, and tests.

---

## Deliverables Status

### 1) Daily plan concept
**Status:** ⚠️ Partially implemented  
**What exists:**
- API route `GET /api/v1/planning/daily-plan` is implemented.
- Rules-based scoring includes deadline pressure, priority/urgency, spouse influence, dependency readiness, and optional current-energy fit.
- Response includes explainability (`reasons`, `score_breakdown`) and deterministic ranking tie-break (`task_id`).
- Tests validate ranking behavior and deterministic ordering for same input.

**Gap:**
- Current implementation scores all visible non-terminal tasks but does not enforce a primary-task + fallback framing described in product requirements.
- Daily plan currently returns a hard-coded overload payload (`overload_risk_level="low"`, empty drivers/actions), so the overload output is present structurally but not computed.
- “Hard commitments are not overridden” guardrail is not explicitly modeled/validated yet (no scheduling commitment model is consulted in ranking).

### 2) Focus mode endpoint and task execution actions (`start/stop/sidetrack/unable`)
**Status:** ❌ Not implemented  
**What exists:**
- No `/api/v1/focus/*` routes were found.
- No phase 3 service methods or schemas for focus lifecycle actions are present.

**Gap:**
- Missing all required focus APIs:
  - `POST /api/v1/focus/start`
  - `POST /api/v1/focus/stop`
  - `POST /api/v1/focus/sidetrack`
  - `POST /api/v1/focus/unable`
- Missing state machine enforcement and idempotency rules for session transitions.
- Missing persistence for session metadata (task linkage, timestamps, state, sidetrack/unable reasons).

### 3) Blocker reason tracking
**Status:** ❌ Not implemented  
**What exists:**
- No blocker taxonomy enum/schema/model is currently defined for Phase 3.

**Gap:**
- No API or DB persistence for blocker events.
- No evidence of blocker capture integrated into daily plan or future planning signal reads.
- Required taxonomy from Phase 3 work plan is not implemented.

### 4) Energy input before/after task
**Status:** ❌ Not implemented as capture workflow; ⚠️ partial as planning input  
**What exists:**
- `daily-plan` accepts an optional query param `current_energy` and incorporates it in scoring.

**Gap:**
- No required pre-task energy capture on start.
- No required post-task energy capture on stop/unable.
- No persistent energy history tied to tasks/sessions.

### 5) Overload detection v1
**Status:** ❌ Not implemented (placeholder only)  
**What exists:**
- Response schema includes overload fields (`overload_risk_level`, `drivers`, `recommended_reset_actions`).

**Gap:**
- No heuristic logic for carryover, unable events, blocker frequency, post-task energy trends, or effort-overbooking.
- No rule documentation or tests for overload signal generation.
- No actionable reset suggestions currently produced.

### 6) Web daily-use workflow integration
**Status:** ❌ Not implemented for Phase 3 scope  
**What exists:**
- Web homepage and component messaging remain explicitly Phase 2 oriented (project/task CRUD shell).

**Gap:**
- No “Do now” daily plan panel.
- No focus-mode UI controls for `start/stop/sidetrack/unable`.
- No blocker/energy capture UX.
- No overload indicator surfaced in UI.

---

## Definition of Done Status (Phase 3)

### DoD: user can ask system what to do now
**Status:** ⚠️ Partially implemented  
**Reasoning:**
- A rules-based daily-plan endpoint exists and returns ranked recommendations with explainability.
- However, overload and commitment guardrails are not yet operational and web “Do now” UX is missing.

### DoD: user can track a task session
**Status:** ❌ Not implemented  
**Reasoning:**
- Focus lifecycle endpoints, persistence, and UI flows are absent.

### DoD: user can record blockers quickly
**Status:** ❌ Not implemented  
**Reasoning:**
- No blocker taxonomy, API capture path, storage model, or UX currently exists.

---

## Critical Gaps (Priority Order)

1. **Implement focus session domain + APIs (P3-1/P3-3)**
   - Add session model/migration and strict transition state machine.
   - Implement `start/stop/sidetrack/unable` endpoints with validation and idempotency.

2. **Implement blocker + energy signal capture (P3-4)**
   - Add blocker taxonomy enum and event persistence.
   - Require pre-energy on start and post-energy on stop/unable.
   - Link signals to task/session and timestamp.

3. **Implement overload heuristic engine (P3-5)**
   - Compute risk level from captured events/signals.
   - Populate `drivers` + `recommended_reset_actions` with explainable outputs.
   - Add threshold tests and rule documentation.

4. **Complete daily-plan guardrails and semantics (P3-2)**
   - Encode hard-commitment guardrails explicitly.
   - Support one-primary + fallback recommendation mode if this remains product intent.
   - Add tests covering commitment-protection logic.

5. **Build Phase 3 web UX (P3-6)**
   - Add daily “Do now” panel wired to `daily-plan`.
   - Add focus action controls and lightweight blocker/energy prompts.
   - Surface overload badge + reset suggestions in the same workflow.

6. **Expand test coverage (P3-7)**
   - Add API/service tests for focus transitions, signal capture validation, and overload rules.
   - Add integration tests spanning plan -> start -> sidetrack/unable/stop -> next plan adjustments.

---

## Suggested Next Sprint Slice

1. **Backend contracts first:** define focus session, blocker event, and energy check-in schemas/migrations.
2. **Execution flow second:** ship focus lifecycle endpoints and required validation rules.
3. **Signal intelligence third:** compute overload risk using real captured data.
4. **UX completion fourth:** ship daily plan + focus controls + blockers/energy prompts in web app.
5. **Confidence fifth:** add end-to-end tests that prove Phase 3 DoD behaviors.
