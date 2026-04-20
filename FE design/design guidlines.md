# Orbis – UX Design Guidelines

## 1. Purpose

This document defines the UX principles, interaction patterns, and structural rules for Orbis.

It focuses on:
- layout behavior
- interaction consistency
- user flow clarity
- component usage

Visual styling (colors, typography, spacing tokens) is defined separately in the Design System Specification.

---

## 2. Core UX Principles

### 2.1 Execution → Planning → Strategy

The product is structured into three mental layers:

- **Day** → execution (what to do now)
- **Week** → planning (what to adjust)
- **Long Term Plan** → strategy (why it matters)

Each screen must clearly reflect its purpose and not mix concerns.

---

### 2.2 Calm by Default

- Default state is **readable and low-noise**
- Editing and advanced controls are **hidden until needed**
- Avoid overwhelming the user with controls

---

### 2.3 User in Control

- No automatic changes to schedule or tasks
- AI suggestions must always be:
  - visible
  - explainable
  - dismissible

---

### 2.4 Fast Interaction

- Common actions should require minimal steps
- Avoid deep navigation
- Prefer inline or panel-based editing

---

### 2.5 Context Preservation

- Do not navigate away unnecessarily
- Use overlays or side panels for details
- User should always understand where they are

---

## 3. Alignment with Design Language

### 3.1 Structure vs Expression

- Core interaction areas must remain **structured and predictable**
- Visual expression (asymmetry, flow) is applied at the **section level**, not interaction level

**Structured zones:**
- navigation
- lists (tasks, timeline)
- week view

**Expressive zones:**
- Day screen layout
- Long Term Plan overview

---

### 3.2 Section Definition (No-Line Rule)

- Sections must be separated using:
  - tonal surface changes
  - whitespace
- Borders must not be used for layout separation

---

### 3.3 Interaction Clarity Without Borders

Interactive elements must be clearly identifiable via:
- contrast between surface layers
- hover / active state changes
- spacing and grouping
- motion (subtle transitions)

Never rely on borders for affordance.

---

### 3.4 Depth Model

- Use **tonal layering** as primary depth system
- Use shadows only for floating elements (modals, overlays)
- Avoid heavy or sharp drop shadows

---

### 3.5 Glass Usage

- Glassmorphism is only for:
  - overlays
  - modals
  - floating panels

Do not use glass effects for primary content areas.

---

### 3.6 Soft Signals with Clarity

- Avoid aggressive colors (e.g. pure red)
- Use softer tones (e.g. terracotta) for warnings

However:
- critical states must still be clearly distinguishable
- always combine:
  - color
  - icon
  - label

---

## 4. Layout System

### 4.1 Desktop Layout

- Fixed **left sidebar**
- Main content area
- Optional right-side **detail panel**


---

### 4.2 Mobile Layout

- Bottom navigation
- Single column content
- Bottom sheets for detail views

---

### 4.3 Fixed vs Scrollable

**Fixed:**
- sidebar
- header (recommended)

**Scrollable:**
- main content

---

## 5. Navigation

### 5.1 Primary Navigation

Located in sidebar (desktop) or bottom nav (mobile):

- Day
- Week
- Long Term Plan

Rules:
- only one active state
- consistent placement
- no dynamic reordering

---

### 5.2 User Menu

- Located at bottom of sidebar
- Collapsed by default (avatar + name)
- Expands into dropdown on click

Contains:
- User Settings
- App Settings
- Logout

---

## 6. Content Structure

### 6.1 Section-Based Layout

All screens are composed of vertical sections:

Sections are separated by:
- whitespace
- surface layering

---

### 6.2 Content Types

- Timeline (Day)
- Grid or agenda (Week)
- Cards (Long Term Plan)
- Lists (tasks, projects)

---

### 6.3 Content Priority

Order of importance:

1. Context (header)
2. Primary content
3. Attention items
4. Suggestions
5. Secondary information

---

## 7. Interaction Patterns

### 7.1 Item Interaction

Default behavior:

- Tap / Click → open detail panel
- Do not navigate to a new page

---

### 7.2 Mobile Gestures

- Swipe right → mark complete
- Swipe left → additional actions

---

### 7.3 Editing Model

- Viewing is default
- Editing must be explicitly activated

Examples:
- Week view has “Edit Mode”
- Inputs are hidden until needed

---

### 7.4 Detail Views

**Mobile:**
- bottom sheet (expandable)

**Desktop:**
- right-side panel

Used for:
- tasks
- projects
- suggestions

---

## 8. Task States

Tasks must clearly communicate their state.

Required states:

- Planned
- Completed
- Blocked
- Overdue
- Deferred
- Unsuccessful / Failed
- Suggested

Rules:
- consistent across all screens
- visually distinguishable
- always visible at a glance

---

## 9. AI Suggestions

### 9.1 Placement

- separate section or inline where relevant
- never override primary content

---

### 9.2 Behavior

Each suggestion must include:
- explanation (“why”)
- actions:
  - Accept
  - Dismiss
  - Inspect

---

### 9.3 UX Rules

- never auto-apply changes
- never interrupt core workflow
- avoid excessive frequency

---

## Form and Menu Consistency Rules

### Input Shape Consistency

- All standard inputs (`input`, `select`, `textarea`) must keep the same corner rounding on all corners.
- Do not use reduced bottom corner radius on text inputs.
- Bottom-edge focus emphasis is still allowed (for accessibility and active-state clarity), but it must not alter corner geometry.

### Settings Form Layout

- In Settings screens, form controls must stack vertically.
- Avoid horizontal wrapping layouts for key form fields.
- Each label/control pair should read top-to-bottom to preserve readability and reduce cognitive load.

### User Menu Item Uniformity

- All items inside the user menu dropdown must share the same surface, typography, spacing, and alignment style.
- Links and buttons in the same menu must be visually identical unless a destructive action variant is explicitly introduced.

---

## 10. Screen-Specific Behavior

### 10.1 Day

- focus on clarity and execution
- minimal editing controls
- highlight attention items and suggestions
- supports more expressive layout (controlled asymmetry)

---

### 10.2 Week

Two modes:

#### Current Week
- read-focused
- editing hidden

#### Future Weeks
- planning-focused
- editing visible
- suggestions visible

**Note:**
Week view is a **structured zone** and should remain visually aligned and predictable.

---

### 10.3 Long Term Plan

- hierarchical navigation
- drill-down structure:
  - life area → project → tasks
- supports expressive layout and card-based structure

---

## 11. Global Actions

**Desktop:**
- placed in header (top-right)

**Mobile:**
- floating action button (FAB)

Primary action:
- add task

---

## 12. Empty States

Every major screen must handle empty state.

### Requirements
- clear explanation
- primary action (CTA)

---

## 13. Error & Edge States

- display inline when possible
- avoid blocking modals
- keep user in context

---

## 14. Motion & Transitions

### Usage

- opening detail panels
- switching modes
- navigation transitions

---

### Rules

- fast and subtle
- directional (helps orientation)
- never decorative

---

## 15. Responsiveness

### Mobile First

Design must:
- work fully on mobile
- prioritize vertical flow
- avoid reliance on hover

---

### Desktop Enhancements

- multi-column layouts
- side panels
- hover states (optional enhancement)

---

## 16. Consistency Rules

- same action = same behavior everywhere
- same state = same visual representation
- same interaction = same result

---

## 17. Key UX Principle

Every screen must answer:

> “What should the user do next?”

If the answer is unclear, the design needs improvement.
