# TrueNAS Setup Guide

This guide explains how to deploy Orbis on TrueNAS SCALE using the repository's Docker Compose stack.

## Scope
- Target: TrueNAS SCALE with Apps support.
- Deployment model: custom app using services from `docker-compose.yml`.
- Goal: production-like self-hosted setup with persistent data and baseline hardening.

For hardening controls and Phase 7 validation context, see [`docs/PHASE7_HARDENING_AND_TRUENAS.md`](PHASE7_HARDENING_AND_TRUENAS.md).

## 1) Prerequisites
- TrueNAS SCALE host with Apps enabled.
- A dataset path for persistent app data.
- Network access to pull container images and access your TrueNAS UI.
- A secure value prepared for:
  - `API_SECRET_KEY`
  - `POSTGRES_PASSWORD`
- Optional AI provider keys (for example `OPENAI_API_KEY`) only if you plan to use AI-backed endpoints.

## 2) Prepare persistent storage
Create or designate persistent storage for the following service volumes:
- `postgres_data`
- `redis_data`
- `caddy_data`
- `caddy_config`

These map to data durability expectations in the existing Compose deployment.

## 3) Create the TrueNAS custom app
Use the Compose service definitions from [`docker-compose.yml`](../docker-compose.yml):
- `proxy`
- `web`
- `api`
- `worker`
- `db`
- `redis`

When configuring the app:
1. Map each persistent volume to your TrueNAS datasets.
2. Add environment variables from `.env.example` and set secure values in TrueNAS secrets/environment UI.
3. Expose only the ports you need externally (typically the reverse proxy).

## 4) Configure required environment variables
At minimum, set:
- `API_SECRET_KEY`
- `POSTGRES_PASSWORD`

Also configure the app URLs/domains and any optional provider keys your deployment requires.

Tip: start from [`.env.example`](../.env.example) and copy values into TrueNAS app config instead of baking secrets into images.

## 5) Database migrations are now automatic
The `api` service startup command checks the current Alembic revision and compares it with the latest migration head on every start/update.

- If revisions differ, it runs `alembic upgrade head` automatically.
- If already current, it logs that migrations are up to date and continues startup.
- If migration execution fails, startup exits non-zero and the failure is visible in container logs.

## 6) Post-deploy validation
Verify:
1. API health endpoint returns `200`.
2. Owner bootstrap/login flow works.
3. Web UI can call API via proxy successfully.
4. Backup script produces expected artifacts.

Useful references:
- Hardening runbook: [`docs/PHASE7_HARDENING_AND_TRUENAS.md`](PHASE7_HARDENING_AND_TRUENAS.md)
- Backup script: [`infra/scripts/backup.sh`](../infra/scripts/backup.sh)
- Restore script: [`infra/scripts/restore.sh`](../infra/scripts/restore.sh)

## 7) Operations baseline
- Monitor auth-related `429` spikes (rate limiting).
- Monitor `401` spikes for failed token/API-key authentication.
- Keep regular backup cadence and test restore in staging/non-production.

## 8) Troubleshooting quick checks
- Services not healthy:
  - Check app/container logs in TrueNAS UI.
  - Confirm environment variables are populated.
  - Confirm persistent volume mounts are writable.
- API unavailable behind proxy:
  - Confirm proxy-to-api upstream networking and service names mirror Compose expectations.
- Login failures after redeploy:
  - Verify `API_SECRET_KEY` has not changed unexpectedly.
  - Verify database credentials still match persisted DB state.
