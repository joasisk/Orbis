# Orbis — Screen Designs (MVP Wireframes)

This file provides concrete MVP wireframes for **each screen** listed in the design plan, aligned with:

- `design plan.md`
- `design guidlines.md`
- `design language.md`
- `main layout wireframe.md`
- `ui-ux documentation.md`

The desktop shell (sidebar + header + optional right panel) is reused across primary app screens.

---

## 1) Shared App Shell (Desktop)

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ SIDEBAR (fixed)      │ HEADER / CONTEXT BAR (fixed in main area)         │
│ - ORBIS + version    ├────────────────────────────────────────────────────┤
│ - Day                │                                                    │
│ - Week               │ MAIN CONTENT (scrollable)                          │
│ - Long Term Plan     │                                                    │
│                      │                                                    │
│                      │                                                    │
│ [Avatar + Name ▾]    │                                                    │
└────────────────────────────────────────────────────────────────────────────┘
```

Right detail panel variant:

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ SIDEBAR         │ HEADER                                                  │
├─────────────────┼──────────────────────────────────────────────────────────┤
│                 │ MAIN CONTENT               │ DETAIL PANEL               │
│                 │                            │ (task / suggestion / item) │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 2) Day (Today’s Orbit)

### Desktop

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Header: Today • date • quick context                [quick actions] │
├──────────────────────────────────────────────────────────────────────┤
│ Morning Brief (summary + focus hint)                                │
├──────────────────────────────────────────────────────────────────────┤
│ Timeline (tasks + events by time)                                   │
│ 08:00  [Task Item]                                                   │
│ 09:30  [Calendar Event]                                              │
│ 11:00  [Task Item]                                                   │
├──────────────────────────────────────────────────────────────────────┤
│ Needs Attention (blocked / overdue / failed)                         │
├──────────────────────────────────────────────────────────────────────┤
│ Suggestions (AI cards with accept / dismiss)                         │
└──────────────────────────────────────────────────────────────────────┘
```

### Mobile

```text
[Header]
[Morning Brief]
[Timeline]
[Needs Attention]
[Suggestions]
[Bottom Nav: Day | Week | Long Term]
```

---

## 3) Week — Current Week (Execution)

### Desktop

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Header: Week of Apr 20–26             [<] [>] [Today]               │
├──────────────────────────────────────────────────────────────────────┤
│ Week Grid / Agenda (read-first)                                      │
│ Mon  Tue  Wed  Thu  Fri  Sat  Sun                                    │
│ [tasks grouped by day, minimal edit controls visible]                │
├──────────────────────────────────────────────────────────────────────┤
│ Overload / blockers strip (soft signal style)                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Mobile

```text
[Week Header + range nav]
[Day tabs / compact agenda blocks]
[Task rows (tap -> bottom sheet)]
[Bottom Nav]
```

---

## 4) Week — Future Weeks (Planning)

### Desktop

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Header: Future Week • date range             [Edit Mode: ON]         │
├──────────────────────────────────────────────────────────────────────┤
│ Planning Grid                                                         │
│ - drag/drop handles visible                                           │
│ - reassignment controls visible                                       │
│ - suggestion markers visible                                          │
├──────────────────────────────────────────────────────────────────────┤
│ Planning Suggestions Panel/List (accept/dismiss)                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Mobile

```text
[Header + week range]
[Planning list with move controls]
[Suggestions list]
[Bottom Sheet for edit details]
```

---

## 5) Long Term Plan — Overview

### Desktop

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Header: Long Term Plan         [Segmented: Areas | Projects | Tasks] │
├──────────────────────────────────────────────────────────────────────┤
│ Life Area Cards / List                                                 │
│ [Health] [Work] [Family] [Home] [Personal Growth]                     │
│ (editorial spacing, structured card actions)                           │
└──────────────────────────────────────────────────────────────────────┘
```

### Mobile

```text
[Header]
[Segmented Control]
[Stacked area cards]
[Bottom Nav]
```

---

## 6) Life Area Detail

### Desktop

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Header: Life Area > Health                         [Area actions]     │
├──────────────────────────────────────────────────────────────────────┤
│ Summary band (progress / active projects / pressure)                  │
├──────────────────────────────────────────────────────────────────────┤
│ Projects List                                                         │
│ - Project Card                                                        │
│ - Project Card                                                        │
├──────────────────────────────────────────────────────────────────────┤
│ Related Tasks                                                         │
└──────────────────────────────────────────────────────────────────────┘
```

### Mobile

```text
[Header + breadcrumb]
[Summary]
[Projects]
[Related Tasks]
```

---

## 7) Project Detail

### Desktop

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Header: Project > Kitchen Deep Clean              [Project actions]   │
├──────────────────────────────────────────────────────────────────────┤
│ Description / intent                                                   │
├──────────────────────────────────────────────────────────────────────┤
│ Progress indicators (status + completion trend)                        │
├──────────────────────────────────────────────────────────────────────┤
│ Task List                                                              │
│  - task row                                                            │
│  - task row                                                            │
├──────────────────────────────────────────────────────────────────────┤
│ Next Actions                                                           │
└──────────────────────────────────────────────────────────────────────┘
```

### Mobile

```text
[Header]
[Description]
[Progress]
[Task List]
[Next Actions]
```

---

## 8) Task Detail Panel (Overlay)

### Desktop (right panel)

```text
┌──────────────────────────────┐
│ Task Title              [X]  │
├──────────────────────────────┤
│ Status controls              │
│ Schedule controls            │
│ Notes                        │
│ Dependencies / blockers      │
├──────────────────────────────┤
│ [Save] [Mark blocked]        │
└──────────────────────────────┘
```

### Mobile (bottom sheet)

```text
┌──────────────────────────────┐
│ Task Title              [X]  │
│ Status                       │
│ Scheduling                   │
│ Notes                        │
│ Actions                      │
└──────────────────────────────┘
```

---

## 9) Suggestion Detail Panel (Overlay)

### Desktop / Mobile structure

```text
┌───────────────────────────────────────────┐
│ Suggestion Title                     [X]  │
├───────────────────────────────────────────┤
│ Why this suggestion? (reasoning)          │
│ Impact if accepted                        │
│ Alternatives / trade-offs                 │
├───────────────────────────────────────────┤
│ [Accept Suggestion]   [Dismiss]           │
└───────────────────────────────────────────┘
```

---

## 10) Week Edit Mode (State Design)

```text
Normal Week View
  -> toggle Edit Mode ON
      -> task cards gain drag handles
      -> drop zones highlighted
      -> reassignment controls visible
      -> save/cancel bar shown
```

Desktop affordances:

- drag & drop within week grid
- explicit "editing" state label in header
- save/cancel actions stay pinned

Mobile affordances:

- move-up/move-down or day picker controls
- bottom sheet for assignment changes

---

## 11) Settings Screens

## 11.1 Settings Home

```text
┌──────────────────────────────────────────────┐
│ Settings                                     │
├──────────────────────────────────────────────┤
│ User Settings                                │
│ App Settings                                 │
│ Notification Settings                        │
│ AI / Planning Settings                       │
└──────────────────────────────────────────────┘
```

## 11.2 User Settings

```text
[Profile]
[Password]
[Account data / export]
[Save]
```

## 11.3 App Settings

```text
[Preferences]
[System behavior]
[Toggles and defaults]
[Save]
```

## 11.4 Notification Settings

```text
[Reminder style]
[Alert preferences]
[Daily brief timing]
[Save]
```

## 11.5 AI / Planning Settings

```text
[Suggestion behavior controls]
[Automation level (approval-gated)]
[Transparency options]
[Save]
```

---

## 12) Entry Screens

## 12.1 Login

```text
┌────────────────────────────────────┐
│ ORBIS                              │
│ Email                              │
│ Password                           │
│ [Log In]                           │
│ [Forgot password]                  │
└────────────────────────────────────┘
```

## 12.2 First-Time Setup / Onboarding

```text
Step 1: Welcome + product promise
Step 2: Create first life area/project/task
Step 3: Set preferences (reminders / day structure)
Step 4: Confirm and enter Day view
```

Principles:

- minimal required inputs
- immediate first success
- no overwhelming branching

---

## 13) Required State Variants (All Primary Screens)

For each screen above, define these variants in design files:

1. Empty
2. Loading
3. Error
4. No suggestions
5. Blocked/failed task emphasis

State treatment rules:

- combine icon + label + calm color signal
- include next best action
- maintain layout stability between states

---

## 14) Cross-Screen Component Usage Matrix

| Component | Day | Week | Long Term | Life Area | Project | Settings |
|---|---|---|---|---|---|---|
| Header / Context Bar | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Section Container | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Task Item | ✓ | ✓ | (Tasks view) | ✓ | ✓ | - |
| Suggestion Card | ✓ | ✓ (future/edit mode) | - | - | - | - |
| Detail Panel / Sheet | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| Segmented Control | - | optional | ✓ | optional | - | - |
| Toggle / Switch | - | ✓ (edit mode) | optional | optional | optional | ✓ |

---

## 15) Designer Handoff Checklist (Per Screen)

- Include desktop + mobile wireframe.
- Include normal + required state variants.
- Mark interaction entry points (tap/click targets).
- Mark open/close behavior for any panel/sheet.
- Map components to existing system tokens (no-line, tonal layers, soft depth).
- Ensure AI actions are explainable, dismissible, and non-destructive by default.

