# AI Agent Guide

## Purpose
Enable agentic AI assistance inside the repository without letting the agent invent product behavior or change critical logic blindly.

## Source of truth order
1. `docs/REQUIREMENTS.md`
2. `docs/MVP_PLAN.md`
3. `docs/IMPLEMENTATION_PLAN.md`
4. code comments and tests
5. issue descriptions / ADRs

## Guardrails
- Do not change business behavior without updating docs or ADRs
- Do not remove approval gates around AI planning
- Do not expose private fields in spouse-facing views
- Do not collapse owner priority values and spouse influence values into one field
- Do not add gamification patterns by default
- Preserve low-friction, low-overwhelm UX principles

## Preferred agent tasks
- generate CRUD endpoints from documented models
- scaffold tests
- implement repository/service layers
- draft prompts from documented behaviors
- create migrations
- suggest refactors that preserve public contracts

## Required context before coding
The agent should read:
- `docs/REQUIREMENTS.md`
- `docs/ARCHITECTURE.md`
- relevant module README or service docs
- existing tests for touched code

## Definition of safe contribution
A change is safe when:
- it is consistent with requirements
- it does not widen scope silently
- it includes tests or at least explicit validation steps
- it does not weaken privacy or auth
