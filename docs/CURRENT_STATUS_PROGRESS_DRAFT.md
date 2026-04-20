# Current Status Snapshot (MVP Readiness)

Assessment date: **2026-04-20**.

This snapshot is aligned to:
1. `docs/REQUIREMENTS.md`
2. `docs/MVP_PLAN.md`
3. `docs/IMPLEMENTATION_PLAN.md`
4. `docs/ARCHITECTURE.md`

---

## Executive summary

The project is **close to MVP completion**.

- Core API and web workflows for task management, weekly planning, focus execution, calendar integration, and notes extraction are implemented.
- Automated checks currently pass for API and web static quality gates.
- Remaining work is concentrated in **final UX parity** (spouse deadline input path, settings cadence controls) and **deployment proof** (live TrueNAS verification).

---

## Validation checks (this assessment)

### API
- `cd apps/api && pytest -q` -> pass (`29 passed`).

### Web
- `cd apps/web && npm run lint` -> pass.
- `cd apps/web && npm run typecheck` -> pass.

---

## Phase progress summary

## Phase 0 — Foundations
**Status:** ✅ Complete

## Phase 1 — Core backend and auth
**Status:** ✅ Complete

## Phase 2 — Project and task domain
**Status:** ✅ Complete

## Phase 3 — Scheduling and focus workflows
**Status:** ✅ Complete

## Phase 4 — AI planning engine
**Status:** ✅ Complete

## Phase 4.1 — Schedule/performance model extension
**Status:** ✅ Complete

## Phase 4.5 — Web catch-up + settings UX
**Status:** ⚠️ Mostly complete

- Home and schedule are API-backed.
- Weekly proposal and note extraction are UI-wired.
- Remaining: expose full planned-action cadence controls in settings UI.

## Phase 5 — Calendar and reminder integration
**Status:** ✅ Complete (MVP baseline)

## Phase 6 — Wife visibility and influence experience
**Status:** ⚠️ Mostly complete

- Spouse dashboard and influence updates are in place.
- Remaining: spouse dashboard quick-edit parity for spouse deadline inputs.

## Phase 7 — Hardening and TrueNAS packaging
**Status:** ⚠️ Mostly complete

- Rate limiting, API key flow, and backup/restore checks exist.
- Remaining: final live-environment TrueNAS proof run documentation.

---

## MVP-close checklist (recommended)

1. Add spouse dashboard quick-edit controls for `spouse_deadline` + `spouse_deadline_type`.
2. Add settings UI controls for existing API-backed cadence/timezone fields.
3. Execute and document one complete TrueNAS deploy verification pass.

---

## Delivery confidence

- **High confidence:** backend MVP capabilities and quality gates.
- **Medium-high confidence:** day-to-day owner UX.
- **Medium confidence:** final spouse-flow parity and deployment handoff evidence.
