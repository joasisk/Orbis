# ADR 0002: Owner/Spouse Role and Access Model

- Status: Accepted
- Date: 2026-04-15

## Context
Phase 1 introduces account security and role-based access. The product requires one primary owner account with optional spouse visibility and influence support, while preserving owner authority on sensitive operations.

## Decision
Use a two-role authorization model:

- `owner`: full household administrative authority, including spouse account provisioning and owner-only operations.
- `spouse`: authenticated household member with constrained access to shared data and no owner-only management privileges.

Implementation uses JWT bearer authentication with refresh-session rotation. API endpoints use dependency-based role guards (`owner-only` and household-level guards) to enforce access policy.

## Consequences

### Positive
- Product policy is reflected directly in API boundaries.
- Clear foundation for privacy scopes in project/task visibility.
- Auditable auth events for key session actions.

### Trade-offs
- Additional test surface for negative-path authorization cases.
- Future invite-based onboarding may require additional flow complexity.
