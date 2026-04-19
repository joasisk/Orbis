# Orbis Usage Guide

This document covers using Orbis as a deployed product (not contributing code).

## Access points
- Web app: served through the reverse proxy.
- API health: `/api/v1/health`
- API docs (if enabled in your deployment): `/docs`

## First-time use
1. Open the web app URL.
2. Complete owner bootstrap/login flow.
3. Configure basic settings in the Settings area.
4. Create Areas/Projects/Tasks and generate plans.

## Core usage flows
- Domain organization:
  - Manage Areas, Projects, and Tasks from the web UI.
- Planning:
  - Use planning endpoints/workflows to generate schedule artifacts.
- Focus workflows:
  - Run focus sessions and review focus signals.
- Reminders:
  - Configure reminders and validate notification timing.

## API consumers
- Interactive API docs: `/docs`
- API key management endpoints: `/api/v1/api-keys` (owner role)
- External auth header: `X-API-Key`

## Backups and restore
- Backup:
  ```bash
  ./infra/scripts/backup.sh
  ```
- Restore:
  ```bash
  ./infra/scripts/restore.sh ./backups/<timestamp-dir>
  ```

## Deployment-specific usage docs
- TrueNAS setup and operations: [`docs/TRUENAS_SETUP.md`](TRUENAS_SETUP.md)
- Hardening runbook: [`docs/PHASE7_HARDENING_AND_TRUENAS.md`](PHASE7_HARDENING_AND_TRUENAS.md)
