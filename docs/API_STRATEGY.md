# API Strategy

## Versioning
- Start with `/api/v1`
- Use additive changes where possible
- Reserve breaking changes for `/v2`

## REST-first approach
Initial resources:
- /auth
- /users/me
- /areas
- /projects
- /tasks
- /recurring-commitments
- /plans
- /focus
- /calendar
- /notes
- /reminders
- /audit-events

## External frontend support
- API keys for machine or external client access
- user-scoped OAuth/OIDC can come later
- webhook subscriptions after MVP

## GraphQL later
Add when:
- multiple clients need tailored reads
- dashboard data becomes expensive or repetitive through REST
- schema is stable enough to support long-lived clients
