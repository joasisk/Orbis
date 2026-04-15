# Project Requirements

## Product vision
A self-hosted AI-assisted time management system for ADHD or easily distracted users that reduces decision fatigue, improves follow-through, and balances long-term projects with daily responsibilities.

## Primary users
- Primary: owner user
- Secondary: spouse with limited visibility and influence

## Core outcomes
- User always knows what to do next
- Lower missed deadlines and forgotten maintenance
- Lower overwhelm
- Better balance across work, family, home, and personal growth

## Functional requirements

### 1. Project and task management
- Support Areas of Life -> Projects -> Tasks
- Support one-off tasks
- Support recurring commitments separate from projects
- Support soft and hard deadlines
- Support task estimates, energy level, dependencies, privacy flag, and status
- Support task history and versioning

### 2. AI weekly planning
- Generate a proposed week plan every Sunday at 20:00
- Consider deadlines, priorities, recurring commitments, energy history, blockers, and overload risk
- Require approval before committing plan changes

### 3. Focus mode
- Provide a "what should I do now?" mode
- Show one primary task and optional fallback tasks
- Allow start, stop, sidetrack, and unable-to-finish actions
- Track approximate time spent

### 4. Failure and blocker handling
- User can mark failure reasons such as:
  - missing prerequisite
  - missing material
  - mental blocker
  - unclear task
  - time constraint
- System should use these signals in rescheduling and task refinement

### 5. Reminders
- Gentle and adaptive reminder model
- Avoid spam and gamified tone
- Learn from user response patterns over time

### 6. Calendar integration
- Read external calendars
- Write scheduled tasks into supported calendars
- Protect existing commitments
- Support time-blocking
- Distinguish hard commitments from soft plan blocks

### 7. Notes integration
- Manual import of selected notes
- Periodic vault/folder scanning
- AI extraction of candidate projects and tasks
- Preserve links to source note
- Suggested items can be accepted, edited, or dismissed

### 8. Wife visibility and influence
- Wife can view visible schedule items
- User can mark items private
- Wife can add her own importance and deadline inputs without overwriting owner's values
- Her inputs should be weighted more strongly for truly critical household/family items
- She cannot directly rewrite owner schedule or core priority values

### 9. Privacy and hosting
- Core data stored locally
- Selective sharing to external AI providers
- Auditability of AI-triggered suggestions and actions
- Export for backup and migration

### 10. API and extensibility
- Public API for first-party and third-party frontends
- REST first, GraphQL later
- API key support for external clients
- Event/webhook capability
- Plugin-friendly integration layer

## Non-functional requirements
- Deployable as Docker-based TrueNAS custom app
- Secure login and proper API security
- Mobile-friendly API design
- Scalable enough for future iOS and Android clients
- Clear separation between frontend, backend, worker, and integration layers

## Out of scope for MVP
- multi-user general-purpose platform
- native mobile apps
- broad two-way sync ecosystem
- advanced analytics
- gamification
- offline-first behavior
