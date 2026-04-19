#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKUP_DIR="${1:-${ROOT_DIR}/backups/$(date -u +%Y%m%dT%H%M%SZ)}"
DB_CONTAINER="${ORBIS_DB_CONTAINER:-orbis-db}"
DB_NAME="${POSTGRES_DB:-orbis}"
DB_USER="${POSTGRES_USER:-orbis}"

mkdir -p "${BACKUP_DIR}"

echo "[backup] writing postgres dump to ${BACKUP_DIR}/postgres.sql"
docker exec "${DB_CONTAINER}" pg_dump -U "${DB_USER}" -d "${DB_NAME}" --no-owner --no-privileges > "${BACKUP_DIR}/postgres.sql"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  cp "${ROOT_DIR}/.env" "${BACKUP_DIR}/env.backup"
fi

cat > "${BACKUP_DIR}/manifest.txt" <<EOF
created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
postgres_container=${DB_CONTAINER}
postgres_db=${DB_NAME}
postgres_user=${DB_USER}
EOF

echo "[backup] completed: ${BACKUP_DIR}"
