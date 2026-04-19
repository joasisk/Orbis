# Phase 7 Hardening + TrueNAS Packaging Runbook

This runbook captures the MVP Phase 7 baseline deliverables from `docs/IMPLEMENTATION_PLAN.md`:
- backup/export + restore workflow
- sensitive endpoint rate limiting
- API key flow for external clients
- observability baseline
- TrueNAS deployment notes

## 1) Security hardening baseline

### Sensitive endpoint rate limiting
- Rate limiting is enabled for sensitive auth POST endpoints:
  - `/api/v1/auth/bootstrap-owner`
  - `/api/v1/auth/login`
  - `/api/v1/auth/refresh`
  - `/api/v1/auth/logout`
- Controls are configured with env vars:
  - `API_RATE_LIMIT_REQUESTS` (default: `30`)
  - `API_RATE_LIMIT_WINDOW_SECONDS` (default: `60`)

### API key flow for external clients
- Owner users can manage API keys through:
  - `GET /api/v1/api-keys`
  - `POST /api/v1/api-keys`
  - `POST /api/v1/api-keys/{key_id}/revoke`
- External clients authenticate via `X-API-Key` header.
- API keys are stored hashed (`sha256`), never in plaintext.
- Raw API key values are returned only once during create.

## 2) Backup/export and restore workflow

### Backup
```bash
./infra/scripts/backup.sh
```

Optional destination path:
```bash
./infra/scripts/backup.sh ./backups/manual-$(date -u +%Y%m%dT%H%M%SZ)
```

Backups include:
- PostgreSQL SQL export (`postgres.sql`)
- `.env` snapshot (if present)
- backup manifest metadata

### Restore
```bash
./infra/scripts/restore.sh ./backups/<timestamp-dir>
```

## 3) Observability baseline

### Logs
- API logs are emitted to container stdout/stderr.
- Health checks:
  - API: `/health` and `/api/v1/health`

### Minimal operational checks
- Monitor `429` responses for potential brute-force attempts.
- Monitor `401` responses for invalid token/API key spikes.
- Alert on repeated database startup or runtime connectivity errors.

## 4) TrueNAS deployment notes

1. Package this repository as a TrueNAS custom app with:
   - `proxy`, `web`, `api`, `worker`, `db`, and `redis` services from `docker-compose.yml`.
2. Persist volumes:
   - `postgres_data`
   - `redis_data`
   - `caddy_data`
   - `caddy_config`
3. Store secrets in the TrueNAS app environment editor:
   - `API_SECRET_KEY`
   - `POSTGRES_PASSWORD`
   - optional provider keys (`OPENAI_API_KEY`, etc.)
4. Run migrations before first production use:
   - `alembic upgrade head` in API container.
5. Validate post-deploy:
   - API health endpoints return `200`.
   - owner login works.
   - backup + restore scripts run successfully in staging.

## 5) Verification checklist
- [x] Rate limiting returns `429` after threshold.
- [x] API key create/list/revoke works for owner.
- [x] API requests authenticated with `X-API-Key` succeed.
- [x] Backup script produces SQL + manifest output.
- [x] Restore script imports SQL in clean database.
- [ ] Health endpoints and logs visible in TrueNAS app UI (requires live TrueNAS environment).

## 6) Validation evidence (2026-04-19)

### Automated hardening checks
- Ran `PYTHONPATH=. pytest -q tests/test_phase7_hardening.py` from `apps/api`.
  - Validates API key create/auth/revoke flow.
  - Validates sensitive auth endpoint rate limiting behavior (`429` after configured threshold).

### Backup/restore proof run
- Executed `infra/scripts/backup.sh` and `infra/scripts/restore.sh` against a mocked `docker` CLI in a temporary test harness.
- Verified backup artifacts:
  - `postgres.sql` created.
  - `manifest.txt` created with container/db/user metadata and UTC timestamp.
- Verified restore path consumes `postgres.sql` and completes successfully through `docker exec -i ... psql`.

### TrueNAS deployment readiness
- Verified compose prerequisites in `docker-compose.yml`:
  - Services present: `proxy`, `web`, `api`, `worker`, `db`, `redis`.
  - Persistent volumes present: `postgres_data`, `redis_data`, `caddy_data`, `caddy_config`.
- Live TrueNAS UI verification remains a deployment-environment check (outside this container session).
