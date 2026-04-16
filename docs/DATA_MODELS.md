# Data Models

## Purpose
This document centralizes the current database model and the planned schedule/performance model extension so backend, frontend, and AI-planning work use a shared vocabulary.

## Source of truth
- Runtime models: `apps/api/app/models/*.py`
- Migration history: `apps/api/alembic/versions/*.py`
- Planned extension: `docs/SCHEDULE_AND_PERFORMANCE_MODEL_PLAN.md`

---

## Current implemented model (as of 2026-04-16)

## Mermaid ERD (implemented tables)
```mermaid
erDiagram
    users {
      string id PK
      string email UK
      string hashed_password
      string role "owner|spouse"
      bool is_active
      datetime created_at
    }

    session_tokens {
      string id PK
      string user_id FK
      string token_hash UK
      datetime expires_at
      datetime revoked_at
      datetime created_at
    }

    audit_events {
      string id PK
      string actor_user_id FK "nullable"
      string event_type
      json metadata
      datetime created_at
    }

    areas_of_life {
      string id PK
      string owner_user_id FK
      string name
      text description
      datetime created_at
      datetime updated_at
    }

    projects {
      string id PK
      string owner_user_id FK
      string area_id FK
      string name
      text description
      string status
      bool is_private
      string visibility_scope "owner|spouse|shared"
      int priority
      int urgency
      datetime deadline
      string deadline_type "soft|hard"
      int spouse_priority
      int spouse_urgency
      datetime spouse_deadline
      string spouse_deadline_type "soft|hard"
      datetime created_at
      datetime updated_at
    }

    tasks {
      string id PK
      string owner_user_id FK
      string project_id FK "nullable"
      string title
      text notes
      string status
      bool is_private
      string visibility_scope "owner|spouse|shared"
      int priority
      int urgency
      datetime deadline
      string deadline_type "soft|hard"
      int spouse_priority
      int spouse_urgency
      datetime spouse_deadline
      string spouse_deadline_type "soft|hard"
      datetime created_at
      datetime updated_at
    }

    recurring_commitments {
      string id PK
      string owner_user_id FK
      string title
      string cadence "daily|weekly|monthly"
      int interval_count
      int duration_minutes
      float energy_weight
      datetime starts_on
      datetime ends_on
      datetime created_at
      datetime updated_at
    }

    task_dependencies {
      string id PK
      string owner_user_id FK
      string task_id FK
      string depends_on_task_id FK
      datetime created_at
    }

    entity_versions {
      string id PK
      string owner_user_id FK
      string entity_type
      string entity_id
      string actor_user_id FK "nullable"
      string event_type
      json changed_fields
      datetime created_at
    }

    focus_sessions {
      string id PK
      string owner_user_id FK
      string task_id FK
      string status "active|completed|unable"
      datetime started_at
      datetime ended_at
      float pre_task_energy
      float post_task_energy
      int sidetrack_count
      text sidetrack_note
      text unable_reason
      datetime created_at
      datetime updated_at
    }

    blocker_events {
      string id PK
      string owner_user_id FK
      string task_id FK
      string focus_session_id FK "nullable"
      string blocker_reason
      text note
      datetime created_at
    }

    weekly_plan_proposals {
      string id PK
      string owner_user_id FK
      string week_start_date
      string status "proposed|approved|rejected"
      string provider_key
      string prompt_template_version
      json evaluation_log
      datetime created_at
      datetime approved_at
    }

    weekly_plan_items {
      string id PK
      string proposal_id FK
      string owner_user_id FK
      string task_id FK
      string suggested_day
      int suggested_minutes
      text rationale
      int rank
      datetime created_at
    }

    note_extractions {
      string id PK
      string owner_user_id FK
      string source_title
      string source_ref
      text note_content
      string provider_key
      json candidate_tasks
      string status "proposed|accepted|dismissed"
      datetime created_at
      datetime reviewed_at
    }

    users ||--o{ session_tokens : has
    users ||--o{ audit_events : actor
    users ||--o{ areas_of_life : owns
    users ||--o{ projects : owns
    users ||--o{ tasks : owns
    users ||--o{ recurring_commitments : owns
    users ||--o{ task_dependencies : owns
    users ||--o{ entity_versions : owns
    users ||--o{ focus_sessions : owns
    users ||--o{ blocker_events : owns
    users ||--o{ weekly_plan_proposals : owns
    users ||--o{ weekly_plan_items : owns
    users ||--o{ note_extractions : owns

    areas_of_life ||--o{ projects : contains
    projects ||--o{ tasks : groups
    tasks ||--o{ task_dependencies : blocked_by
    tasks ||--o{ focus_sessions : runs_in
    focus_sessions ||--o{ blocker_events : context
    tasks ||--o{ blocker_events : blocked_by
    weekly_plan_proposals ||--o{ weekly_plan_items : contains
    tasks ||--o{ weekly_plan_items : suggested
```

## Current behavior notes
- `weekly_plan_proposals` + `weekly_plan_items` represent AI planning artifacts, not explicit daily schedule execution records.
- Focus/blocker tables provide execution telemetry (energy/distraction/blocker signals), but daily plan acceptance/execution is not yet first-class.
- Spouse influence values are kept separate from owner values in project/task records.

---

## Planned schedule/performance extension (not yet implemented)

## Mermaid ERD (planned additions)
```mermaid
erDiagram
    weekly_schedules {
      string id PK
      string owner_user_id FK
      date week_start_date
      string status "proposed|accepted|rejected"
      string source_proposal_id FK "nullable"
      datetime created_at
      datetime accepted_at
    }

    daily_schedules {
      string id PK
      string weekly_schedule_id FK
      string owner_user_id FK
      date schedule_date
      string status "proposed|accepted|adjusted"
      int mood_score
      float morning_energy
      float evening_energy
      text self_evaluation
      datetime created_at
      datetime updated_at
    }

    daily_schedule_items {
      string id PK
      string daily_schedule_id FK
      string owner_user_id FK
      string task_id FK
      int planned_minutes
      int actual_minutes
      string outcome_status "planned|done|postponed|failed|partial|skipped"
      int order_index
      int distraction_count
      text distraction_notes
      date postponed_to_date
      text failure_reason
      datetime created_at
      datetime updated_at
    }

    weekly_schedules ||--o{ daily_schedules : contains
    daily_schedules ||--o{ daily_schedule_items : plans
```

## Planned lifecycle model
- Weekly schedule lifecycle: `proposed -> accepted|rejected`.
- Daily schedule lifecycle: `proposed -> accepted -> adjusted`.
- Day item lifecycle: `planned -> done|postponed|failed|partial|skipped`.

## Planned implementation timing
See dated rollout in `docs/SCHEDULE_AND_PERFORMANCE_MODEL_PLAN.md` (current target window: 2026-05-04 to 2026-06-12).

---

## Ownership, privacy, and approval guardrails
- Owner approval gate remains mandatory for applying AI-generated schedule changes.
- Private items must not leak into spouse-visible schedule views.
- Owner priority fields remain distinct from spouse influence fields.

