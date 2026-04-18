#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <backup_dir>"
  exit 1
fi

BACKUP_DIR="$1"
DB_CONTAINER="${ORBIS_DB_CONTAINER:-orbis-db}"
DB_NAME="${POSTGRES_DB:-orbis}"
DB_USER="${POSTGRES_USER:-orbis}"

if [[ ! -f "${BACKUP_DIR}/postgres.sql" ]]; then
  echo "missing ${BACKUP_DIR}/postgres.sql"
  exit 1
fi

echo "[restore] restoring postgres dump from ${BACKUP_DIR}/postgres.sql"
cat "${BACKUP_DIR}/postgres.sql" | docker exec -i "${DB_CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}"

echo "[restore] completed"
