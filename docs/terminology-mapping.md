# UI Terminology Mapping (Frontend-Only, MVP Safe)

This document tracks the temporary terminology split between existing backend/API/data model names and the new product-facing UI language.

## Scope

- **In scope:** frontend UI copy and labels.
- **Out of scope (intentionally unchanged):** backend code, API contracts, DB schema, TypeScript domain model property names, and integration payload keys.

## Mapping table

| Backend / API / model term (unchanged) | New UI / product term | Where used in UI | Future migration notes |
|---|---|---|---|
| `lifeArea`, `area`, `life areas` | `Orbit`, `Orbits` | Navigation, area selectors, area workspace headings/empty states, home dashboard scope footnote | Keep `area_id` in requests/responses until a dedicated API contract migration is planned. |
| `weeklySchedule`, `week`, `weekly` | `Trajectory`, `Trajectories` | Schedule screen title, controls, section cards, loading/empty states, planning settings wording | Continue calling `/schedules/weeks/*` and `ai_auto_generate_weekly`; migrate only with coordinated BE versioning. |
| `daySchedule`, `daily plan`, `focus session`, `focus actions` | `Burn` | Home dashboard day-plan copy, focus-planning screen headings/buttons/status/errors, week detail prompt copy | Existing endpoints (`/planning/daily-plan`, `/focus/*`) remain unchanged; consider adding a thin UI view-model adapter during future BE rename. |
| `recurringTask`, `recurring tasks` | `Rhythm`, `Rhythms` | Product terminology constants + documented convention (no dedicated recurring-task UI surface in current frontend yet) | Introduce runtime usage in UI once recurring-task surfaces are added or exposed in MVP flows. |

## Temporary coexistence notes

1. Code-level variable/property names such as `area_id`, `weeklySchedule`, `dailySchedule`, `FocusSessionResponse`, and `ai_auto_generate_weekly` remain as-is for compatibility.
2. User-visible copy now favors **Orbit / Trajectory / Burn** in the updated surfaces.
3. A small shared terminology module (`apps/web/src/lib/ui-terminology.ts`) was added to reduce future copy drift and support eventual migration.
