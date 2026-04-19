# UI ↔ API Gap Implementation Plan (MVP)

Date: 2026-04-19  
Source analysis: `docs/UI_API_GAP_ANALYSIS.md`

## 1) Objective
Close the documented web-to-API wiring gaps without expanding MVP scope. Specifically:
- make primary routes load API data on route entry,
- complete minimum CRUD parity for Areas,
- add owner spouse-management UX,
- add spouse influence editing UX for tasks,
- preserve owner-control and approval-first scheduling guardrails.

## 2) Requirements traceability
- `docs/REQUIREMENTS.md`
  - Functional #1 Project/task management (Areas/Projects/Tasks)
  - Functional #8 Wife visibility and influence
  - Functional #10 API and extensibility (REST-first consistency)
- `docs/MVP_PLAN.md`
  - Core data/workflow includes Areas/Projects/Tasks + spouse influence values
  - Weekly plan and daily use remain approval/owner-controlled
- `docs/IMPLEMENTATION_PLAN.md`
  - Phase 4.5 web catch-up/settings UX explicitly calls for API-backed primary routes and settings integration surfaces

## 3) Scope
### In scope (MVP-sized)
1. Route-entry auto-fetch for existing dashboards.
2. Areas list/create UI (minimum viable parity with Projects/Tasks create flows).
3. Owner-only spouse management controls in Settings.
4. Spouse influence controls on task detail/list row (priority/urgency/deadline influence fields only).
5. Tests for authz boundaries and UI wiring states (loading/success/error).

### Out of scope
- Changing planning/schedule approval gates.
- Letting spouse directly edit owner priority fields.
- Broad spouse task creation policy changes (unless explicitly approved as requirement change).
- New gamification, analytics, or non-MVP expansion.

## 4) Gap-to-workstream mapping

| Gap from analysis | Planned implementation |
|---|---|
| Manual data loading on `/`, `/projects`, `/schedule` | Add route-entry effect hooks to fetch on first render when auth token exists; keep manual refresh as fallback. |
| No Areas create/list flow | Add Areas UI module and route section (or dashboard panel) with list + create form wired to `GET /areas` and `POST /areas`. |
| No spouse management UI | Add settings subsection for owner to create/manage spouse link via `POST /users/spouse` and spouse status fetch endpoint(s). |
| No spouse influence UI | Add spouse influence edit controls for `PATCH /tasks/{id}/spouse-influence` with strict field mapping and role-aware rendering. |
| Requirement ambiguity for "spouse can add tasks" | Leave policy unchanged in this plan; document as follow-up product decision/ADR if required. |

## 5) Implementation phases

## Phase A — Route auto-fetch hardening
**Web changes**
- `apps/web` dashboard components:
  - trigger initial fetch in `useEffect` for home areas, projects index, and schedule week/day bootstrap.
  - retain explicit refresh/load actions for recovery and manual retry.
- ensure no duplicate in-flight requests (simple request state guard).

**Acceptance criteria**
- Navigating directly to `/`, `/projects`, `/schedule` with valid auth loads data without extra clicks.
- Empty states are distinct from error states.

## Phase B — Areas UI parity (minimum)
**Web changes**
- Add Areas management surface consistent with existing project/task UI conventions.
- Include:
  - list existing areas,
  - create area form (name + minimal metadata allowed by API contract),
  - optimistic or post-create refetch behavior.

**API changes**
- None expected if `GET/POST /areas` already stable.
- If contract mismatch appears, align web payload to API schema rather than broadening API.

**Acceptance criteria**
- Owner can create Area from UI and see it appear in list after submit.

## Phase C — Spouse management in Settings (owner only)
**Web changes**
- Add `Spouse` card/section under settings:
  - create spouse account form,
  - linked spouse status display,
  - clear owner-only visibility and permission messaging.

**API changes**
- Use existing `POST /users/spouse`.
- If missing read endpoint for spouse status, add minimal owner-scoped read endpoint (MVP-safe) and tests.

**Acceptance criteria**
- Owner can create spouse from settings.
- Non-owner cannot access spouse-management actions.

## Phase D — Spouse influence controls on Tasks
**Web changes**
- Add spouse influence editor for supported fields only:
  - spouse priority,
  - spouse urgency,
  - spouse deadline influence.
- Role-aware rendering:
  - owner can view spouse influence,
  - spouse can submit influence values,
  - no editing of owner priority fields through this control.

**API changes**
- Consume existing `PATCH /tasks/{id}/spouse-influence`.
- Tighten validation/error responses only if required for consistent UX.

**Acceptance criteria**
- Spouse can update influence values from UI.
- Owner fields remain unchanged unless owner edits them through owner-specific endpoints.

## Phase E — Verification and regression protection
**API tests**
- Authz tests for spouse endpoint and spouse-influence patch.
- Ensure owner/spouse field separation invariants remain intact.

**Web tests**
- Component/integration tests for auto-fetch on mount and error/empty handling.
- Form submission tests for Areas create and spouse-management flows.

**Manual checks**
- Login as owner: verify `/`, `/projects`, `/schedule` auto-load.
- Login as spouse: verify spouse influence control visibility and successful patch.

## 6) Proposed execution order
1. Phase A (route auto-fetch) — broad UX win, low risk.
2. Phase B (Areas parity) — closes core CRUD gap.
3. Phase C (spouse management) — settings completion.
4. Phase D (spouse influence UI) — spouse capability completion.
5. Phase E (tests/regression) — finalize quality gate.

## 7) Risks and mitigations
- **Risk:** accidental scope creep into spouse-write permissions.  
  **Mitigation:** enforce dedicated spouse influence endpoint usage only.
- **Risk:** route auto-fetch introduces noisy repeated calls.  
  **Mitigation:** one-shot mount fetch + in-flight guard + manual retry button.
- **Risk:** API contract drift for areas/settings payloads.  
  **Mitigation:** type-safe API client contracts and endpoint-focused tests before UI merge.

## 8) Definition of done for this plan
- All "Partial/Not implemented" items in `docs/UI_API_GAP_ANALYSIS.md` are either:
  1) implemented and validated, or
  2) explicitly deferred with requirement/ADR decision record.
- Primary routes are API-backed on entry.
- Areas create/list, spouse management, and spouse influence flows are accessible in UI with correct role boundaries.
- No approval gates or privacy boundaries are weakened.
