# TrueNAS Setup Guide

This guide explains how to deploy Orbis on TrueNAS SCALE using the repository's Docker Compose stack.

## Scope
- Target: TrueNAS SCALE with Apps support.
- Deployment model: custom app using services from [`docker-compose.truenas.yml`](../docker-compose.truenas.yml).
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

These map to data durability expectations in the production Compose deployment.

## 3) Create the TrueNAS custom app
Use the Compose service definitions from [`docker-compose.truenas.yml`](../docker-compose.truenas.yml):
- `caddy`
- `web`
- `api`
- `worker`
- `postgres`
- `redis`

When configuring the app:
1. Map each persistent volume to your TrueNAS datasets.
2. Add environment variables from `.env.example` and set secure values in TrueNAS secrets/environment UI.
3. Expose only the proxy port externally (`8080:80` in the example).
4. Access the app through the proxy URL (for example: `http://192.168.5.201:8080`), not the web container port `3000`.

## 4) Why the proxy URL matters
- `localhost` in browser JavaScript always means the **end user's machine**, not the TrueNAS host.
- A hardcoded browser URL such as `http://localhost:8000/api/v1` fails for remote users because their own laptop/desktop usually has nothing listening on port `8000`.
- Using same-origin `/api/v1` keeps frontend API calls on the same host/port the user opened, and Caddy routes `/api/*` to the API container.

## 5) Next.js build-time note for `NEXT_PUBLIC_*`
- `NEXT_PUBLIC_*` variables are compiled into the browser bundle at `npm run build` time.
- Setting `NEXT_PUBLIC_API_BASE_URL` only at container runtime does **not** rewrite already-built client bundles.
- The production image build now bakes `NEXT_PUBLIC_API_BASE_URL=/api/v1` by default, which is the safest TrueNAS/LAN default when using Caddy.

Tip: start from [`.env.example`](../.env.example) and copy values into TrueNAS app config instead of baking secrets into images.

## 6) Configure required environment variables
At minimum, set:
- `API_SECRET_KEY`
- `POSTGRES_PASSWORD`

Also configure the app URLs/domains and any optional provider keys your deployment requires.

## 7) Database migrations are now automatic
The `api` service startup command checks the current Alembic revision and compares it with the latest migration head on every start/update.

- If revisions differ, it runs `alembic upgrade head` automatically.
- If already current, it logs that migrations are up to date and continues startup.
- If migration execution fails, startup exits non-zero and the failure is visible in container logs.

## 8) Post-deploy validation
Verify:
1. API health endpoint returns `200` through proxy path (`http://TRUENAS_IP:8080/api/v1/health`).
2. Owner bootstrap/login flow works.
3. Web UI can call API via proxy successfully.
4. Backup script produces expected artifacts.

Useful references:
- Hardening runbook: [`docs/PHASE7_HARDENING_AND_TRUENAS.md`](PHASE7_HARDENING_AND_TRUENAS.md)
- Backup script: [`infra/scripts/backup.sh`](../infra/scripts/backup.sh)
- Restore script: [`infra/scripts/restore.sh`](../infra/scripts/restore.sh)

## 9) Operations baseline
- Monitor auth-related `429` spikes (rate limiting).
- Monitor `401` spikes for failed token/API-key authentication.
- Keep regular backup cadence and test restore in staging/non-production.

## 10) Troubleshooting quick checks
- Services not healthy:
  - Check app/container logs in TrueNAS UI.
  - Confirm environment variables are populated.
  - Confirm persistent volume mounts are writable.
- API unavailable behind proxy:
  - Confirm proxy-to-api upstream networking and service names mirror Compose expectations.
  - Confirm `infra/caddy/Caddyfile` is mounted into the Caddy container.
- Login failures after redeploy:
  - Verify `API_SECRET_KEY` has not changed unexpectedly.
  - Verify database credentials still match persisted DB state.
