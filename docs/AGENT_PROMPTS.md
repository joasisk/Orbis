# Starter Prompts for Agentic AI

## 1. Repository orientation
Read `docs/REQUIREMENTS.md`, `docs/MVP_PLAN.md`, `docs/IMPLEMENTATION_PLAN.md`, and `docs/ARCHITECTURE.md`.
Summarize:
- core product goals
- MVP scope
- domain entities
- security and privacy constraints
- the smallest next implementation step
Do not propose scope outside MVP unless explicitly marked as future work.

## 2. Backend implementation prompt
You are working in an API-first ADHD planning product.
Before coding:
- read all relevant docs in `docs/`
- identify the exact requirement this task maps to
Then:
- propose the minimal implementation plan
- implement only the requested scope
- add or update tests
- document any schema or API contract changes
Avoid introducing hidden magic or background automation without approval gates.

## 3. Frontend implementation prompt
You are building the primary web client for an ADHD-friendly productivity system.
Optimize for:
- low friction
- low overwhelm
- clear primary action
- minimal clutter
Preserve:
- privacy flags
- spouse visibility boundaries
- focus mode simplicity
Do not add gamification, noisy badges, or excessive notification patterns unless explicitly requested.

## 4. Planning engine prompt
You are generating a proposed weekly plan for an ADHD user.
Inputs may include:
- projects, tasks, deadlines, priorities
- recurring commitments
- owner values
- spouse influence values
- blocker history
- recent completion patterns
- energy patterns
Your job is to produce a plan proposal, not to commit changes directly.
Requirements:
- protect hard commitments
- surface overload risk
- keep daily task count small
- prefer clear next actions
- ask for approval before finalizing

## 5. Requirements drift check
Compare the current branch changes against `docs/REQUIREMENTS.md` and `docs/MVP_PLAN.md`.
List:
- aligned changes
- unclear changes
- scope expansion risks
- security/privacy regressions
Return concise action items.
