# Orbis UI/UX Documentation (MVP)

## 1. Purpose

This document consolidates the UI/UX direction for Orbis by combining:

- screen scope from `design plan.md`
- interaction and behavior rules from `design guidlines.md`
- visual system rules from `design language.md`

It is intended as an implementation-ready guide for designers and frontend engineers.

> Note: The **main layout shell is already defined** in `main layout wireframe.md`. This document builds on that shell and does not replace it.

---

## 2. Foundation and Scope

### 2.1 Product constraints

The UI/UX must support an ADHD-friendly experience that is:

- low-noise by default
- clear in hierarchy
- predictable in interaction
- calm rather than urgency-driven

### 2.2 MVP scope guardrails

- Keep Day, Week, and Long Term Plan as the 3 primary navigation destinations.
- Keep AI actions user-controlled (visible, explainable, dismissible).
- Avoid gamification patterns and noisy engagement mechanics.
- Preserve privacy boundaries for private items and spouse-facing visibility.

---

## 3. Information Architecture

### 3.1 Primary mental model

The app is organized as a three-layer system:

1. **Day** = execution (what to do now)
2. **Week** = planning (what to adjust)
3. **Long Term Plan** = strategy (why it matters)

### 3.2 Navigation model

#### Desktop

- Fixed left sidebar
- Main content column
- Optional right-side detail panel

#### Mobile

- Bottom navigation
- Single-column content
- Bottom sheets for detail views

### 3.3 Main layout ownership

The shell behavior below is already decided and should be reused consistently:

- sidebar remains fixed/sticky
- main area scrolls
- context/header bar at top of content region
- user menu anchored in sidebar footer
- detail panel opens contextually from the right on desktop

---

## 4. Screen Documentation

## 4.1 Core screens

### Day (Today’s Orbit)

**Goal:** Minimize decision fatigue and guide immediate execution.

**Required sections (top-to-bottom):**

1. Header/context strip (date + lightweight context)
2. Morning brief
3. Timeline (tasks + events)
4. Needs Attention
5. Suggestions

**Interaction notes:**

- Prioritize readability over density.
- Show advanced controls only on demand.
- Opening task details should not navigate away from Day.

---

### Week — Current Week (execution mode)

**Goal:** Review and execute the active week with minimal editing friction.

**Characteristics:**

- clean layout
- reduced editing affordances by default
- strong scanability for day-by-day load

**Interaction notes:**

- Keep interaction shallow; avoid nested flows.
- Surface blockers and overload risk clearly but softly.

---

### Week — Future Weeks (planning mode)

**Goal:** Support intentional planning and reassignment.

**Characteristics:**

- visible editing controls
- suggestion visibility
- higher interaction density than current-week view

**Interaction notes:**

- Editing controls can be persistently visible in this state.
- Keep AI suggestions explicit and reversible.

---

### Long Term Plan — Overview

**Goal:** Present strategic trajectory across life areas.

**Required modules:**

- life areas (cards/list)
- view toggles (areas/projects/tasks)

**Interaction notes:**

- Use expressive section-level layouts while preserving structured controls.
- Keep strategic context visible when drilling down.

---

### Life Area Detail

**Goal:** Show progress and workload inside one life area.

**Required modules:**

- project list
- related tasks
- summary metrics/indicators

---

### Project Detail

**Goal:** Operationalize project execution without losing context.

**Required modules:**

- project summary/description
- task list
- progress indicators
- next actions

---

## 4.2 Interaction and overlays

### Task Detail Panel

**Primary interaction surface for task operations.**

Contents:

- task information
- status controls
- scheduling controls
- notes

Presentation:

- desktop: right-side panel
- mobile: bottom sheet

Behavior:

- open from contextual click/tap
- close via `X`, outside click/tap, or `Escape` (desktop)

---

### Suggestion Detail Panel

Purpose:

- explain why suggestion exists
- communicate impact
- provide clear actions: accept / dismiss

Rule:

- never hide critical rationale behind unclear labels

---

### Week Edit Mode (state)

Purpose:

- explicit planning mode with editable affordances

Expected affordances:

- desktop drag-and-drop
- assignment/reassignment controls
- visible edit state indicators

---

## 4.3 Settings and entry screens

Settings hierarchy:

1. Settings Home
2. User Settings
3. App Settings
4. Notification Settings
5. AI/Planning Settings

Entry flow:

- Login
- First-time setup/onboarding

Onboarding principle:

- create momentum with minimal fields and immediate first value

---

## 5. System States (Required Across Screens)

Design these states for every major view and panel:

- empty
- loading
- error
- no suggestions
- blocked/failed task

State rules:

- each state should explain what happened
- each state should include next action when possible
- preserve calm tone, avoid alarmist language

---

## 6. Interaction Model and Behavioral Rules

### 6.1 Calm by default

- Hide advanced controls unless editing is intentionally activated.
- Avoid visual clutter and over-instrumented dashboards.

### 6.2 Context preservation

- Prefer overlays/panels over route changes for detail actions.
- Keep parent context visible during edits whenever possible.

### 6.3 Fast interaction principles

- Minimize click depth for top tasks (start, reschedule, complete, block).
- Keep frequent actions close to their owning content.

### 6.4 AI trust rules

All AI-driven suggestions must be:

- visible
- explainable
- optional
- reversible where applicable

---

## 7. Visual and Component Standards

## 7.1 No-Line Rule

For sectioning and layout separation:

- do not use hard borders/dividers as primary separators
- use whitespace + tonal surface changes instead

## 7.2 Tonal depth model

- Use layered surfaces for hierarchy.
- Reserve shadows for floating surfaces (modals/panels/overlays).
- Keep shadows soft and ambient.

## 7.3 Glass usage boundaries

Glassmorphism is allowed for:

- overlays
- floating panels
- modals

Not for:

- primary content blocks
- core reading surfaces

## 7.4 Typography intent

- Editorial hierarchy for anchors/headings.
- High legibility body text with comfortable line height.
- Keep labels clear, short, and unambiguous.

## 7.5 Component behavior summary

- Buttons: tactile but subtle feedback (hover/press).
- Cards/lists: whitespace-separated, no divider-line dependence.
- Chips: soft semantic cues, not alarm-based color logic.
- Inputs: grounded focus treatment with clear active state.

---

## 8. Responsive Behavior

### Desktop

- Sidebar fixed left.
- Header/context row at top of content.
- Detail panel can open to the right.

### Mobile

- Bottom navigation for top-level routes.
- Detail interactions move to bottom sheets.
- Prefer vertically stacked sections and progressive disclosure.

---

## 9. Implementation Handoff Checklist

For each screen build, confirm:

1. It maps to Day / Week / Long Term purpose clearly.
2. It uses the existing main layout shell (not a custom shell).
3. It includes required empty/loading/error variants.
4. It keeps AI actions explainable and dismissible.
5. It follows no-line + tonal layering rules.
6. It preserves context through panel/sheet interactions.

---

## 10. Design-to-Development Deliverables

Each finalized screen should include:

- annotated wireframe
- component inventory used
- interaction notes (entry, edit, close, error)
- responsive notes (desktop/mobile differences)
- state coverage matrix (normal + edge states)

---

## 11. Future Documentation Add-ons (Post-MVP)

- accessibility-specific interaction spec (keyboard map, focus model)
- motion timing/token table
- content style guide (microcopy patterns)
- spouse-facing visibility UI rules by role

