# UI ↔ API Gap Implementation Plan (MVP)

Date: 2026-04-19  
Last verified against codebase: 2026-04-19  
Source analysis: `docs/UI_API_GAP_ANALYSIS.md`

## 1) Objective
Track verified implementation status for the documented web-to-API wiring gaps while staying inside MVP scope. This document is now a **living status plan** (completed vs remaining), not a greenfield proposal.

## 2) Requirements traceability
- `docs/REQUIREMENTS.md`
  - Functional #1 Project/task management (Areas/Projects/Tasks)
  - Functional #8 Wife visibility and influence
  - Functional #10 API and extensibility (REST-first consistency)
- `docs/MVP_PLAN.md`
  - Core data/workflow includes Areas/Projects/Tasks + spouse influence values
  - Weekly plan and daily use remain approval/owner-controlled
- `docs/IMPLEMENTATION_PLAN.md`
  - Phase 4.5 web catch-up/settings UX for API-backed routes and settings integration

## 3) Scope and guardrails
### In scope
1. Keep primary routes API-backed on route entry.
2. Keep Areas list/create parity in UI.
3. Keep owner-only spouse-management UX in Settings.
4. Keep spouse influence editing UX for tasks via dedicated endpoint.
5. Add missing weekly proposal and note-extraction web workflows.
6. Add missing owner-editable planned-action schedule controls in Settings.
7. Add/maintain tests for role boundaries and UI wiring behavior.

### Out of scope
- Weakening approval gates on planning/scheduling.
- Letting spouse edit owner priority fields directly.
- Broad spouse task-creation permission changes without explicit requirement/ADR decision.
- Non-MVP expansion (gamification/analytics/etc.).

## 4) Verification summary (2026-04-19)

| Workstream | Status | Verification summary |
|---|---|---|
| A. Route auto-fetch hardening | ✅ Completed | `/`, `/projects`, and `/schedule` fetch core data on route entry with token present; manual refresh/load remains available. |
| B. Areas UI parity (minimum) | ✅ Completed | Areas route + list/create/edit/delete UI exists and is wired to `/areas` endpoints. |
| C. Spouse management in Settings (owner) | ✅ Completed | Settings loads spouse status and supports owner spouse creation via `/users/spouse`. |
| D. Spouse influence controls on Tasks | ✅ Completed | Task detail supports spouse-only influence updates through `PATCH /tasks/{id}/spouse-influence`; owner can view influence fields. |
| E. Verification/regression coverage | ⚠️ Partial | API coverage exists for spouse/authz/domain flows; web automated tests for these UI flows are still missing. |
| F. Weekly proposal UI wiring | ❌ Not implemented | No web workflow found for generate/review/approve weekly proposals despite API endpoints existing. |
| G. Notes extraction review UI wiring | ❌ Not implemented | No web workflow found for note extraction preview + decision despite API endpoints existing. |
| H. Planned-action schedule settings UX | ❌ Not implemented | Settings UI/schema still expose baseline AI toggles; cadence/interval/pause controls are not yet present. |

## 5) Updated implementation plan (remaining work only)

### Phase F — Weekly proposal UI wiring (owner)
**Web changes**
- Add weekly proposal workspace under schedule context:
  - generate proposal (`POST /planning/weekly-proposals/generate` or `/generate-default`),
  - load latest (`GET /planning/weekly-proposals/latest`),
  - edit proposal day allocations,
  - approve proposal (`POST /planning/weekly-proposals/{proposal_id}/approve`).
- Keep explicit copy that generated proposals are non-authoritative until approval.

**Acceptance criteria**
- Owner can generate, inspect, adjust, and approve a proposal in UI.
- Generation does not mutate weekly/daily schedules until approve action.

### Phase G — Notes extraction review UI wiring (owner)
**Web changes**
- Add note extraction panel:
  - submit preview (`POST /planning/note-extractions/preview`),
  - show candidates,
  - accept/dismiss via decision endpoint (`POST /planning/note-extractions/{id}/decision`).
- Show created-task feedback after acceptance.

**Acceptance criteria**
- Owner can review candidate tasks before creation.
- No tasks are created until explicit accept decision.

### Phase H — Planned-action schedule settings
**Web changes**
- Extend settings form with planned-action controls:
  - app timezone for planned actions,
  - weekly planning cadence,
  - note-scan cadence,
  - reminder scan interval,
  - optional pause-until.

**API/data changes**
- Extend `/settings/me` schema and PATCH payload with schedule fields.
- Add validation for cadence completeness + interval bounds.
- Preserve guardrail: `ai_auto_generate_weekly` requires `ai_require_manual_approval=true`.

**Acceptance criteria**
- Owner can save/reload planned-action schedule config.
- Invalid combinations fail with field-specific errors.

### Phase E — Regression hardening (to complete after F/G/H)
**API tests**
- Maintain authz tests for spouse endpoints/influence separation.
- Add tests for any new settings/planning payload validation.

**Web tests**
- Add route auto-fetch behavior tests.
- Add form-flow tests for spouse management, weekly proposal, and note extraction paths.
- Add settings schedule-config rendering and validation tests.

## 6) Execution order from current state
1. Phase F (weekly proposal UI).
2. Phase G (note extraction review UI).
3. Phase H (planned-action settings).
4. Phase E (final regression and integration hardening).

## 7) Risks and mitigations (remaining)
- **Risk:** proposal workflow is mistaken for immediate schedule mutation.  
  **Mitigation:** explicit pre-approval labels, disabled “applied” messaging until approve succeeds.
- **Risk:** settings expansion increases cognitive load.  
  **Mitigation:** progressive disclosure and sensible defaults.
- **Risk:** API/UI contract drift as settings payload grows.  
  **Mitigation:** shared typed payloads and endpoint-focused tests.

## 8) Definition of done for this plan
- Remaining workstreams (F/G/H/E) are implemented and validated.
- Primary routes, Areas, spouse management, and spouse influence remain functional and role-safe.
- Weekly proposal and note extraction are fully operable from UI.
- Planned-action schedule settings are editable/persisted with guardrails intact.
- Any deferrals are explicitly documented with requirement/ADR references.
