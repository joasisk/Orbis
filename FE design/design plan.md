# Orbis – Design Plan

## 1. Purpose

This document defines the scope of UI/UX design work for Orbis.

It provides:
- a complete list of screens to design
- a breakdown of reusable UI components
- prioritization guidance for implementation

This plan should be used by designers and developers to track progress and ensure consistency.

---

## 2. Screens to Design

---

### 2.1 Core Screens (Primary Product)

#### Day (Today’s Orbit)
Daily control center.

Includes:
- header / context bar
- morning brief
- timeline (tasks + events)
- needs attention section
- suggestions section

---

#### Week – Current Week
Execution-focused weekly view.

Characteristics:
- clean and readable
- minimal editing UI
- structured layout

---

#### Week – Future Weeks
Planning-focused weekly view.

Characteristics:
- editing controls visible
- suggestions visible
- higher interaction density

---

#### Long Term Plan – Overview
Strategic overview.

Includes:
- life areas (cards or list)
- view toggle (areas / projects / tasks)

---

#### Life Area Detail
Drill-down view.

Includes:
- list of projects
- related tasks
- summary information

---

#### Project Detail
Project-focused view.

Includes:
- project description
- task list
- progress indicators
- next actions

---

### 2.2 Interaction & Overlay Screens

#### Task Detail Panel
Primary interaction surface.

Includes:
- task information
- status controls
- scheduling controls
- notes

Presentation:
- desktop: right-side panel
- mobile: bottom sheet

---

#### Suggestion Detail Panel
Expanded AI explanation.

Includes:
- reasoning
- impact
- actions (accept / dismiss)

---

#### Week Edit Mode (State)
Editable state of week view.

Includes:
- drag & drop (desktop)
- visible editing affordances
- task reassignment controls

---

### 2.3 System & Settings Screens

#### Settings – Home
List of settings categories.

---

#### User Settings
- profile
- password
- account data

---

#### App Settings
- preferences
- system behavior

---

#### Notifications Settings
- reminders
- alerts
- daily brief timing

---

#### AI / Planning Settings
- suggestion behavior
- automation level

---

### 2.4 Entry Screens

#### Login Screen

---

#### First-Time Setup / Onboarding
- initial setup
- create first tasks or areas

---

### 2.5 Required UI States

These must be designed across screens:

- empty states
- loading states
- error states
- no suggestions state
- blocked / failed task states

---

## 3. Core UI Components

---

### 3.1 Navigation

#### Sidebar (Desktop)
- app identity (name + version)
- main navigation (Day, Week, Long Term Plan)
- user menu (expandable)

---

#### Bottom Navigation (Mobile)
- primary navigation items

---

#### User Menu
- collapsed (avatar + name)
- expanded dropdown:
  - user settings
  - app settings
  - logout

---

### 3.2 Layout & Structure

#### Section Container
- base layout block
- uses tonal layering and spacing

---

#### Header / Context Bar
- title / context
- actions (right-aligned)

---

### 3.3 Task & Content Components

#### Task Item (Critical Component)
Used across:
- Day
- Week
- Project

Includes:
- title
- time (optional)
- status
- interaction affordance

---

#### Task States (Variants)

Must support:
- planned
- completed
- blocked
- overdue
- deferred
- unsuccessful / failed
- suggested

---

#### Timeline Item
- time-based representation

---

#### Project Card
- used in Long Term Plan

---

#### Life Area Card
- high-level grouping element

---

### 3.4 AI & Feedback Components

#### Suggestion Card
- explanation
- actions:
  - accept
  - dismiss

---

#### Suggestion Detail View
- expanded reasoning

---

#### Attention Item
- blocked / overdue tasks

---

### 3.5 Interaction Components

#### Buttons
- primary
- secondary
- subtle

---

#### Chips
- filter chips
- state chips

---

#### Toggle / Switch
- edit mode
- settings controls

---

#### Segmented Control
- switch between:
  - areas / projects / tasks

---

#### Input Field
- bottom-heavy input style

---

### 3.6 Overlay Components

#### Detail Panel (Desktop)
- right-side panel

---

#### Bottom Sheet (Mobile)
- expandable interaction surface

---

#### Modal (Limited Use)
- only when necessary

---

### 3.7 Action Components

#### Primary Action Button

Desktop:
- placed in header

Mobile:
- floating action button (FAB)

Primary use:
- add task

---

#### Context Menu
- secondary actions for tasks

---

### 3.8 Feedback & System States

#### Empty State
- explanation
- primary action

---

#### Loading State
- skeleton or placeholder

---

#### Error State
- inline feedback

---

## 4. Design Priorities

---

### High Priority (Must Get Right First)

1. Day screen
2. Task item + task states
3. Task detail panel
4. Week (current vs future distinction)

---

### Medium Priority

5. Long Term Plan
6. Suggestion system
7. Navigation + layout polish

---

### Lower Priority (But Required)

8. Settings screens
9. Onboarding
10. Edge states

---

## 5. Key Design Principle

The system is **component-driven, not page-driven**.

Consistency and quality of these components define the overall UX:

- Task Item
- Section Container
- Suggestion Card
- Detail Panel

---

## 6. Deliverables

Design should include:

### Screens
- all primary screens
- key states (editing, empty, etc.)

---

### Components
- reusable UI elements
- state variations

---

### Interaction States
- hover
- active
- focus
- editing

---

## 7. Guiding Question

Every screen and component must answer:

> “What should the user do next?”

If the answer is unclear, the design needs improvement.