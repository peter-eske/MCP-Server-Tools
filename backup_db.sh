#!/bin/bash
# ── DB Backup für litellm PostgreSQL ───────────────────────────────────────
# Usage: ./backup_db.sh                    # normal (löscht alte > 7d)
#        ./backup_db.sh --no-prune         # ohne clean-up
#        ./backup_db.sh --help

set -euo pipefail

BACKUP_DIR="/root/backups/litellm"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_CONTAINER="debate-postgres"
DB_USER="litellm"
DB_NAME="litellm"
DB_PASS="litellm_gateway_secret_2025"

mkdir -p "$BACKUP_DIR"

echo "[$(date '+%H:%M:%S')] Backup start: $DB_NAME → $BACKUP_DIR/"

docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  > "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql"

gzip -f "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql"

echo "[$(date '+%H:%M:%S')] Wrote: ${DB_NAME}_${TIMESTAMP}.sql.gz"
echo "[$(date '+%H:%M:%S')] Size:  $(ls -lh "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz" | awk '{print $5}')"

if [[ "${1:-}" != "--no-prune" ]]; then
  find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -delete
  echo "[$(date '+%H:%M:%S')] Pruned backups older than ${RETENTION_DAYS}d"
fi

echo "[$(date '+%H:%M:%S')] Backup done."
