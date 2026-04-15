# Phase 1 Gap Analysis (Documentation vs Implementation)

## Scope
Compared **Phase 1 — Core backend and auth** from `docs/IMPLEMENTATION_PLAN.md` against current backend implementation in `apps/api`.

---

## Deliverables Status

### 1) FastAPI app bootstrapped
**Status:** ✅ Implemented  
**Evidence:** App exists with lifespan, health routes, and v1 router inclusion in `app/main.py`.

### 2) PostgreSQL connection and migrations
**Status:** ✅ Implemented  
**Evidence:** SQLAlchemy engine/session in `app/core/db.py`; Alembic auth/session/audit migrations exist.

### 3) Auth model: owner role, spouse role
**Status:** ⚠️ Partially implemented  
**What exists:**
- Owner bootstrap path exists (`POST /api/v1/auth/bootstrap-owner`) and creates role=`owner`.
- Role checks exist (`require_roles`) and owner-only endpoint exists.

**Gap:**
- No explicit spouse onboarding/creation flow.
- No role enum/check constraint at DB level (roles are free-form string).
- No spouse-specific protected route demonstrating spouse access policy.

### 4) Secure password auth
**Status:** ✅ Implemented (baseline)  
**Evidence:** Password hashing/verification using `passlib` PBKDF2; login verifies hash.

### 5) Refresh token flow
**Status:** ✅ Implemented  
**Evidence:** Login creates refresh session, refresh rotates token (revokes old + issues new), logout revokes by token.

### 6) API auth middleware
**Status:** ✅ Implemented  
**Evidence:** `get_current_user` bearer-token dependency validates JWT and active user.

### 7) Audit log model starter
**Status:** ✅ Implemented  
**Evidence:** `AuditEvent` model and migration; auth flows write audit events (bootstrap/login/refresh/logout).

---

## Definition of Done Status

### DoD: login/logout works
**Status:** ✅ Likely implemented  
**Evidence:** Login/logout endpoints and service methods are present and connected.

### DoD: protected endpoint works
**Status:** ✅ Implemented  
**Evidence:** `/api/v1/users/me` requires authenticated user.

### DoD: roles enforce access
**Status:** ⚠️ Partially implemented  
**Evidence:** Owner-only endpoint uses centralized role guard.

**Gap:**
- Role enforcement exists mechanically, but spouse-flow behavior is not demonstrated by dedicated endpoints or lifecycle support.

---

## Missing Items to Fully Satisfy Phase 1

1. **Spouse account lifecycle support**
   - Add API flow to create/invite spouse user (owner-controlled).
   - Ensure spouse role assignment is intentional and auditable.

2. **Role integrity hardening**
   - Replace free-form role string with constrained enum/check in DB + schema validation.

3. **Spouse authorization coverage**
   - Add at least one spouse-allowed route and one owner-only route with explicit forbidden behavior for spouse.

4. **Phase-1 verification tests**
   - Add integration tests for bootstrap, login/logout, token refresh rotation, `/users/me`, and role-based access outcomes.

---

## Recommended Next Steps (Priority Order)

1. Implement spouse creation/invite endpoint + audit event.
2. Add role enum/check constraint migration.
3. Add spouse-visible endpoint and explicit policy tests.
4. Add integration test suite for all Phase 1 DoD scenarios.
