# UI ↔ API Gap Analysis (MVP Verification)

Date: 2026-04-19
Scope: Validate whether the current web UI is actually wired to API endpoints for the requested capabilities.

## Summary matrix

| Capability | Status | Evidence |
|---|---|---|
| Login works from UI | ✅ Implemented | `AuthEntry` posts to `/auth/login` and stores access/refresh tokens. |
| Logout works from UI | ✅ Implemented | `AppShell` posts to `/auth/logout` and clears local auth state. |
| Daily schedule fetched on proper FE route access | ⚠️ Partial | `/schedule` route exists, but day/week fetch is manual via “Load Week” and day-click; no auto-fetch on route load. |
| Weekly schedule fetched on proper FE route access | ⚠️ Partial | `/schedule` route exists, but `/schedules/weeks/{week_start_date}` is called only when user clicks “Load Week”. |
| Areas of life fetched on proper FE route access | ⚠️ Partial | Areas are fetched on `/` only after clicking “Refresh” (not automatic on route entry). |
| Projects fetched on proper FE route access | ⚠️ Partial | `/projects` page exists, but list fetch is manual via “Refresh” button. |
| All items can be created from UI | ❌ Not complete | UI creates Projects and Tasks, but has no UI create flow for Areas. |
| User settings fetched and updated | ✅ Implemented | Settings page can GET/PATCH `/settings/me` via “Load” and “Save settings”. |
| User can manage spouse | ❌ Not implemented in UI | API has `POST /users/spouse`, but no spouse management UI found. |
| Spouse can access data | ⚠️ API yes / UI no | API/domain supports spouse visibility on non-private shared/spouse records; no spouse-specific UX present. |
| Spouse can add tasks | ❌ Not supported (API policy) | `create_task` enforces owner-only for project-bound tasks; no spouse task-creation UI. |
| Spouse can update priorities | ⚠️ API yes / UI no | API exposes spouse influence update (`PATCH /tasks/{id}/spouse-influence`), but no UI flow for it. |

## Detailed findings

## 1) Login / logout
- **Login** is wired in UI through `AuthEntry` and posts credentials to `/auth/login`. On success it stores tokens and redirects to `/`.  
- **Logout** is wired in UI through `AppShell`, calls `/auth/logout` with refresh token, then clears local storage + cookie and redirects to `/login`.

Result: **Implemented**.

## 2) Daily + weekly schedule route hookup
- `/schedule` route renders `ScheduleDashboard`.
- `ScheduleDashboard` has API calls to:
  - `GET /schedules/weeks/{weekDate}`
  - `GET /schedules/days/{scheduleDate}`
- But these calls happen only after explicit user actions (`Load Week` and clicking a day card). There is no effect that auto-loads schedules upon route access.

Result: **Partially implemented** (endpoint wiring exists, route-triggered auto-fetch missing).

## 3) Areas of life + projects route hookup
- Areas are requested in `HomeDashboard` (`GET /areas`) on `/` **only when Refresh is clicked**.
- Projects list fetch exists in `EntityManagement` (`GET /projects`) for `/projects` route, also **manual Refresh only**.

Result: **Partially implemented** (manual fetch instead of automatic on route access).

## 4) Create flows from UI
- `EntityManagement` supports creation for:
  - `POST /projects`
  - `POST /tasks`
- No Area management/creation page or form was found in web app routes/components.

Result: **Not complete** for “all items can be created”.

## 5) User settings fetch/update
- `SettingsDashboard` is wired to:
  - `GET /settings/me` (`Load` button)
  - `PATCH /settings/me` (`Save settings` button)

Result: **Implemented**.

## 6) Spouse management and spouse capabilities
- API supports spouse account creation (`POST /users/spouse`) and spouse-influence updates for tasks (`PATCH /tasks/{id}/spouse-influence`).
- Web UI has no spouse management page/form and no spouse-influence editing controls.
- Domain policy currently restricts many writes to owner-only. For tasks, spouse can update influence fields via the dedicated endpoint, but not general owner fields.

Result:
- **Manage spouse in UI**: Not implemented.
- **Spouse access data**: API-level support exists; no dedicated UI workflow.
- **Spouse add tasks**: Not currently aligned with API owner-only write policy for project tasks.
- **Spouse update priorities**: Supported via spouse influence endpoint, but UI support missing.

## Suggested next MVP-sized steps
1. Add route-level auto-fetch on `/`, `/schedule`, and `/projects` when token exists.
2. Add basic Areas CRUD UI (at minimum create + list).
3. Add spouse management panel under `/settings`:
   - create spouse account (owner only)
   - show linked spouse state.
4. Add spouse-facing task influence controls:
   - `spouse_priority`, `spouse_urgency`, deadline influence fields.
5. Clarify requirement wording: if “spouse can add tasks” is mandatory, update API authorization policy and tests accordingly; otherwise reframe as “spouse can influence priorities”.
