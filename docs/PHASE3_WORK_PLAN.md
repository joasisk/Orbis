# Phase 3 Work Plan — Scheduling and Focus Workflows

## Purpose
This plan translates Phase 3 goals into execution-ready workstreams using the current project documentation baseline.

## Documentation reviewed
- `docs/IMPLEMENTATION_PLAN.md` (Phase 3 goals, deliverables, and definition of done)
- `docs/MVP_PLAN.md` (daily-use expectations)
- `docs/REQUIREMENTS.md` (functional behavior for scheduling, blockers, and task execution)
- `docs/GITHUB_ISSUES_ROADMAP.md` (Issue 9–11 alignment)

---

## Phase 3 outcomes (target)
By the end of Phase 3, the system should allow a user to:
1. Ask what to do now and receive a ranked, explainable recommendation.
2. Run a focused work session with quick actions (`start`, `stop`, `sidetrack`, `unable-to-finish`).
3. Capture blockers and energy signals with low friction.
4. Detect probable overload and suggest reset behavior.

---

## Scope boundaries

### In scope
- Rules-based daily planning endpoint (v1, deterministic)
- Focus session lifecycle APIs + web UI flow
- Blocker taxonomy and capture
- Pre/post energy check-ins tied to sessions
- Overload detection v1 with explainable signals
- Minimal reporting/query support for captured signals

### Out of scope (deferred)
- LLM-generated daily planning (Phase 4+)
- Advanced analytics dashboards
- Push/mobile notifications beyond existing infrastructure
- Sophisticated behavioral coaching logic

---

## Workstreams and deliverables

## WS1 — Daily Plan Engine (rules-based v1)
**Goal:** Implement a deterministic "what should I do now" recommendation service.

### Deliverables
- Backend endpoint: `GET /api/v1/planning/daily-plan`
- Ranking algorithm v1 using:
  - deadlines (hard > soft)
  - priority
  - estimated effort fit
  - current/preferred energy
  - blockers and dependency readiness
- Explainability payload for each recommendation (`reasons[]`, `score_breakdown`)
- Guardrail: hard commitments are not overridden

### Exit criteria
- Endpoint returns ranked recommendations + explanations
- Deterministic tests prove same input => same ranking
- API response is consumed by web "Do now" panel

---

## WS2 — Focus Session Workflow
**Goal:** Track real execution behavior for tasks with minimal click overhead.

### Deliverables
- Backend actions/endpoints:
  - `POST /api/v1/focus/start`
  - `POST /api/v1/focus/stop`
  - `POST /api/v1/focus/sidetrack`
  - `POST /api/v1/focus/unable`
- Session model updates:
  - task id
  - started_at / ended_at
  - active/paused/final status
  - sidetrack note/reason
  - unable-to-finish reason
- Web focus controls with one-click action UX and clear state transitions

### Exit criteria
- User can complete full start->stop flow from web UI
- Sidetrack and unable flows persist required metadata
- Session history is queryable for future planning signals

---

## WS3 — Blockers and Energy Capture
**Goal:** Collect practical planning signals without slowing users down.

### Deliverables
- Blocker reason taxonomy (initial enum):
  - unclear requirement
  - missing dependency
  - external wait
  - low energy/focus
  - time fragmentation
  - mental resistance
  - context not available
- API + persistence for blocker events
- Required energy check-ins:
  - pre-task energy (on `start`)
  - post-task energy (on `stop` and `unable`)
- Validation rules and UX nudges for fast capture

### Exit criteria
- Blocker and energy values are saved with timestamps and task/session linkage
- Data can be queried by planning engine and future AI workflows
- Error handling prevents silent drops of check-in data

---

## WS4 — Overload Detection v1
**Goal:** Detect unsustainable daily load and trigger recovery suggestions.

### Deliverables
- Overload heuristic service (rule-based):
  - excessive carryover
  - repeated unable-to-finish events
  - high blocker frequency
  - persistent low post-task energy
  - overbooked calendar-to-effort ratio
- API response flags:
  - `overload_risk_level`
  - `drivers[]`
  - `recommended_reset_actions[]`
- UI indicators integrated in daily plan/focus context

### Exit criteria
- Overload signal appears in daily plan payload
- Users receive a short, actionable reset suggestion
- Rules are documented and test-covered

---

## Proposed implementation sequence
1. **Data contracts first**
   - Finalize schemas/events for session, blocker, energy, overload signals.
2. **Backend core**
   - Build daily plan endpoint + focus lifecycle actions + validations.
3. **Signal capture**
   - Add blocker taxonomy and energy checks into action flows.
4. **Overload heuristics**
   - Compute risk from captured data and expose in API.
5. **Frontend integration**
   - Daily "Do now" panel + focus controls + blocker/energy UX.
6. **Stabilization**
   - Integration tests, edge-case handling, docs updates.

---

## Dependency map
- Depends on Phase 2 entities and CRUD completeness (Tasks/Projects/etc.).
- Should complete before Phase 4 AI planning engine rollout to ensure high-quality signal data.
- Optional calendar weighting can consume integration data once Phase 5 is available.

---

## Risks and mitigations
- **Risk:** Ranking rules feel opaque.
  - **Mitigation:** Return reason codes and score breakdown in API payload.
- **Risk:** Users skip blocker/energy capture.
  - **Mitigation:** Keep inputs compact, default-friendly, and required only at key transitions.
- **Risk:** Overload heuristic is noisy.
  - **Mitigation:** Start with conservative thresholds and tune with observed usage data.
- **Risk:** Focus actions become state-inconsistent.
  - **Mitigation:** Enforce strict state machine + idempotency rules in API.

---

## Definition of done checklist (Phase 3)
- [ ] User can request "what to do now" and get ranked recommendations.
- [ ] User can run `start/stop/sidetrack/unable` flows end-to-end.
- [ ] Blockers are recordable in <10 seconds.
- [ ] Energy is captured before and after sessions as required.
- [ ] Overload risk is surfaced with suggested reset action.
- [ ] API + UI + integration tests pass for all major paths.
- [ ] Documentation updated for endpoints, states, and event schema.

---

## Suggested issue breakdown (execution-ready)
1. **P3-1:** Define scheduling/focus schemas and state machine contracts.
2. **P3-2:** Implement daily plan ranking endpoint with explainability.
3. **P3-3:** Implement focus session action endpoints.
4. **P3-4:** Add blocker taxonomy + energy check-in capture.
5. **P3-5:** Implement overload detection v1.
6. **P3-6:** Build web daily plan + focus mode UI.
7. **P3-7:** Add integration/e2e tests and finalize docs.

This issue split aligns directly with roadmap Issues 9–11 while making frontend/backend/test responsibilities explicit.
