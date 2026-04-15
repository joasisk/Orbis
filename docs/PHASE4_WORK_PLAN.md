# Phase 4 Work Plan — AI Planning Engine

## Purpose
Translate **Phase 4 — AI planning engine** from implementation intent into an executable delivery plan for engineering.

Primary source references used:
- `docs/IMPLEMENTATION_PLAN.md` (Phase 4 deliverables and DoD)
- `docs/REQUIREMENTS.md` (AI weekly planning + notes integration constraints)
- `docs/MVP_PLAN.md` (MVP scope boundaries)
- `docs/ARCHITECTURE.md` (service boundaries and worker role)

## Phase 4 outcomes to deliver
By the end of this phase, the team should have:
1. A provider abstraction layer for AI calls.
2. A weekly planning generation job (Sunday proposal flow).
3. An approval workflow so no schedule changes happen silently.
4. A note-to-task extraction workflow with user review controls.
5. Prompt templates and evaluation logging for quality iteration.
6. Guardrails and auditability for all AI-proposed changes.

## Scope assumptions
- In scope: backend API + worker + minimal web review/approval UI + audit/logging.
- Out of scope: advanced analytics, mobile clients, broad two-way sync, and plugin marketplace.
- Integration target: one initial note ingestion path and one provider abstraction that can support multiple providers.

## Workstreams

### WS1 — AI provider abstraction (foundation)
**Goal:** decouple planning/note workflows from any single LLM vendor.

**Tasks**
- Define `AIProvider` interface (chat/completion + structured output contract).
- Add provider registry + config-driven selection.
- Implement first provider adapter and a mock/test adapter.
- Add timeout/retry/idempotency policy for worker-initiated AI calls.
- Add redaction-safe request/response logging.

**Deliverables**
- Provider interface module.
- First provider adapter + tests.
- Config docs for provider switching.

**Exit criteria**
- Planning service can run against real provider and mock provider without code changes.

---

### WS2 — Weekly planning proposal job
**Goal:** generate a weekly schedule proposal on cadence without directly mutating committed plans.

**Tasks**
- Build planner input assembler (deadlines, priorities, recurring commitments, energy history, blockers, overload signals, calendar constraints).
- Create deterministic pre-check layer (input validation, missing-data handling).
- Implement scheduled worker trigger (default Sunday 20:00; configurable).
- Persist proposal snapshot with rationale/explanations and confidence metadata.
- Add idempotency keying to avoid duplicate proposal generation.

**Deliverables**
- Worker job + scheduler config.
- Proposal persistence schema and API read endpoints.
- Observability: job run status and failure reasons.

**Exit criteria**
- A scheduled run generates one reviewable proposal record with no direct schedule writes.

---

### WS3 — Approval and edit workflow
**Goal:** guarantee human-in-the-loop control for any schedule mutation.

**Tasks**
- Define proposal lifecycle states: `draft`, `proposed`, `accepted`, `edited_and_accepted`, `rejected`, `expired`.
- Build API endpoints for review actions (accept/edit/reject).
- Implement diff-aware apply pipeline (what changes are being approved).
- Enforce permission + role checks around approvals.
- Record full audit trail for each review action and resulting mutation.

**Deliverables**
- Approval endpoints + service logic.
- Proposal diff view payload contract for frontend.
- Audit event coverage for all review state transitions.

**Exit criteria**
- No schedule changes are possible unless an explicit approval action is recorded.

---

### WS4 — Note-to-task extraction workflow
**Goal:** turn imported notes into candidate tasks/projects with explicit user control.

**Tasks**
- Create note ingestion contract (manual import first).
- Build extraction prompt + schema for candidate items.
- Persist extraction suggestions with source-note linkage.
- Add user actions: accept, edit, dismiss.
- Add safeguards for duplicate/similar task suggestions.

**Deliverables**
- Ingestion endpoint + extraction worker path.
- Candidate suggestion table(s) + status tracking.
- API for suggestion review actions.

**Exit criteria**
- Imported note can produce candidate tasks that remain non-authoritative until user action.

---

### WS5 — Prompt templates, evaluation logging, and guardrails
**Goal:** support safe iteration and measurable quality improvements.

**Tasks**
- Version prompt templates (weekly plan + note extraction).
- Log prompt/version + model/provider + token usage + latency + outcome status.
- Define quality rubric for proposal usefulness and extraction precision.
- Implement simple evaluation runner for regression checks on curated fixtures.
- Add operational guardrails (max changes per run, blocked categories, fail-closed behavior).

**Deliverables**
- Prompt template registry/versioning strategy.
- Eval log schema and initial benchmark dataset.
- Guardrail policy config and enforcement hooks.

**Exit criteria**
- Team can compare prompt/provider variants and detect regressions before rollout.

## Suggested execution sequence (4-week plan)

### Week 1
- Complete WS1 core interface and adapter scaffolding.
- Implement WS2 planner input assembler + proposal schema.
- Decide proposal lifecycle model for WS3.

### Week 2
- Ship scheduled weekly proposal worker path (WS2).
- Add approval APIs and state machine transitions (WS3).
- Implement foundational audit event emissions.

### Week 3
- Build note import + extraction pipeline (WS4).
- Add candidate review endpoints and status transitions (WS4).
- Start prompt version logging and eval table scaffolding (WS5).

### Week 4
- Finalize guardrails + fail-closed behavior (WS5).
- Complete regression fixtures and baseline eval run (WS5).
- Hardening pass: retries, observability dashboards, docs, and DoD verification.

## Dependency map
- WS1 is a prerequisite for WS2 and WS4.
- WS2 and WS3 can proceed in parallel after proposal schema is stable.
- WS5 starts early for instrumentation but finishes after WS2–WS4 are functional.

## Risks and mitigations
- **Risk:** low-quality AI outputs reduce trust.
  - **Mitigation:** strict approval gating, diff visibility, evaluation fixtures, and conservative apply limits.
- **Risk:** noisy or sparse inputs degrade planning quality.
  - **Mitigation:** deterministic input validation and fallback behavior for missing signals.
- **Risk:** provider instability or latency spikes.
  - **Mitigation:** retries with limits, timeout budgets, and provider abstraction for failover.
- **Risk:** accidental schedule mutation.
  - **Mitigation:** enforce write path through approval state machine only, with auditable events.

## Definition of Done checklist (traceable)
- [ ] Sunday planning job creates a proposal.
- [ ] Proposal can be accepted or edited.
- [ ] Imported note can generate candidate tasks.
- [ ] No silent schedule changes.
- [ ] Approval required before schedule mutations.
- [ ] Prompt/eval logging available for quality iteration.

## Recommended Phase 4 issue breakdown
1. Implement provider abstraction and first adapter.
2. Add weekly proposal schema + persistence.
3. Build weekly proposal scheduler/worker.
4. Build proposal review APIs and lifecycle states.
5. Implement proposal diff/apply service with approval enforcement.
6. Add audit coverage for AI proposal and review actions.
7. Implement manual note ingestion endpoint.
8. Implement note extraction worker + candidate storage.
9. Add candidate review API (accept/edit/dismiss).
10. Add prompt versioning + eval logging + regression fixtures.
11. Add guardrails (limits, blocklists, fail-closed behavior).
12. Run Phase 4 DoD verification checklist.
