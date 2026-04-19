# Orbis FE Rework — Main Layout (Web) Specification

## 1) Purpose

This document defines the **base desktop layout system** for Orbis web views.
It is the structural companion to the design language and is intended to be the stable shell that all major screens (Day, Week, Long Term Plan) are composed within.

## 2) Scope

This spec covers:

- Fixed sidebar architecture
- Header/context bar behavior
- Main content composition rules
- Contextual right-side detail panel behavior
- User profile trigger and dropdown menu behavior
- Desktop action placement conventions

This spec does **not** define detailed per-screen content modules (those should be documented in screen-specific wireframes).

## 3) Base Wireframe

```text
┌──────────────────────────────────────────────────────────────┐
│ ┌──────────────────────┐ ┌────────────────────────────────┐ │
│ │ Sidebar              │ │ Main Content Area             │ │
│ │                      │ │                                │ │
│ │                      │ │                                │ │
│ │                      │ │                                │ │
│ │                      │ │                                │ │
│ │                      │ │                                │ │
│ │                      │ │                                │ │
│ └──────────────────────┘ └────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 4) Sidebar (Final Structure)

### 4.1 Structural Regions

```text
┌────────────────────────────┐
│ ORBIS                      │
│ v0.x.x                     │
│                            │
│ ───────────────────────── │
│                            │
│ ● Day                      │
│ ● Week                     │
│ ● Long Term Plan           │
│                            │
│                            │
│      flexible space        │
│                            │
│                            │
│ ───────────────────────── │
│                            │
│ [Avatar] John Doe       ▾  │
└────────────────────────────┘
```

1. Top: app identity (`ORBIS` + version)
2. Middle: primary navigation
3. Flexible spacer: absorbs remaining vertical space
4. Bottom: user trigger row (avatar + name + caret)

### 4.2 Sidebar Behavior

- Full viewport height
- Fixed/sticky while content area scrolls
- Navigation supports exactly one active item at a time
- Active item must be visually distinct via background + text emphasis

### 4.3 Expanded User Menu (Popover)

```text
        ┌───────────────────┐
        │ User Settings     │
        │ App Settings      │
        │ Logout            │
        └───────────────────┘
```

Open/close behavior:

- Click trigger → open popover
- Click outside → close
- Press `Escape` → close

---

## 5) Main Content Area

```text
┌───────────────────────────────────────────────┐
│ Header / Context Bar                          │
├───────────────────────────────────────────────┤
│                                               │
│                                               │
│               Main Content                    │
│                                               │
│                                               │
│                                               │
└───────────────────────────────────────────────┘
```

### 5.1 Header / Context Bar

Structure:

```text
[ Screen Title / Context ]      [ Actions / Controls ]
```

Examples by route:

- Day: `Today` + lightweight summary
- Week: date range + navigation arrows
- Long Term Plan: horizon/view toggle controls

Behavior:

- Fixed at top of the content region (recommended default)
- Use subtle spacing or divider treatment below the header

---

## 6) Detail Panel Pattern

The layout supports contextual details in a right-side panel.

### 6.1 Default (No Panel)

```text
┌───────────────────────────────────────────────┐
│ Header                                        │
├───────────────────────────────────────────────┤
│                                               │
│               Main Content                    │
│                                               │
└───────────────────────────────────────────────┘
```

### 6.2 With Detail Panel Open

```text
┌──────────────────────────────────────────────────────────────┐
│ Header                                                       │
├──────────────────────────────────────────────────────────────┤
│ Main Content              │ Detail Panel                    │
│                           │                                 │
│                           │                                 │
│                           │                                 │
└──────────────────────────────────────────────────────────────┘
```

### 6.3 Panel Behavior

- Enters from the right edge
- May overlay or partially push main content (implementation variant)
- Close methods:
  - close button (`X`)
  - click outside
  - `Escape`

Typical uses:

- task detail
- project detail
- suggestion rationale/explanation

---

## 7) Content Composition Rules (Inside Main Region)

Content should be organized as vertically stacked sections:

```text
[ Section Title ]
[ Content Block ]

[ Section Title ]
[ Content Block ]
```

Supported section patterns:

- timeline (Day)
- grid (Week)
- cards (Long Term/Scope views)
- structured lists (tasks/projects)

Spacing rhythm:

- Large spacing between major sections
- Medium spacing between related groups
- Small spacing inside components

---

## 8) Action Placement Rules (Desktop)

Preferred pattern (**Option A / Recommended**):

```text
[ Title ]                  [ + Add / Actions ]
```

Alternative pattern (**Option B**):

- Place actions inline inside the owning section

Global rule:

- No floating action button on desktop layout

---

## 9) Final Combined Reference Wireframes

### 9.1 Base

```text
┌──────────────────────────────────────────────────────────────┐
│ ┌──────────────────────┐ ┌────────────────────────────────┐ │
│ │ ORBIS                │ │ Header / Context              │ │
│ │ v0.x.x               │ ├────────────────────────────────┤ │
│ │                      │ │                                │ │
│ │ ● Day                │ │                                │ │
│ │ ● Week               │ │                                │ │
│ │ ● Long Term Plan     │ │        Main Content            │ │
│ │                      │ │                                │ │
│ │                      │ │                                │ │
│ │                      │ │                                │ │
│ │                      │ │                                │ │
│ │ ───────────────────  │ │                                │ │
│ │ [Avatar] John Doe ▾  │ │                                │ │
│ └──────────────────────┘ └────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### 9.2 With Detail Panel

```text
┌──────────────────────────────────────────────────────────────┐
│ ┌──────────────┐ ┌──────────────────────┬──────────────────┐ │
│ │ Sidebar      │ │ Main Content         │ Detail Panel     │ │
│ │              │ │                      │                  │ │
│ │              │ │                      │                  │ │
│ │              │ │                      │                  │ │
│ └──────────────┘ └──────────────────────┴──────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 10) Implementation Notes

- Treat this as the app-level shell contract before building deeper screen detail.
- Keep interactions low-friction and predictable (especially menu/panel close behavior).
- Align component surfaces and spacing with the design language document.

## 11) Next Recommended Documentation Step

Document the **"Today's Orbit"** screen inside this shell at wireframe level to validate:

- vertical rhythm
- information hierarchy
- reusable component primitives

