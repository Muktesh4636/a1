#!/bin/bash

# Automated Backup Script
# Run this via cron to backup database regularly
# Example cron: 0 */6 * * * /opt/dice_game/scripts/automated_backup.sh

set -e

DEPLOY_DIR="${DEPLOY_DIR:-/opt/dice_game}"
BACKUP_DIR="${BACKUP_DIR:-/opt/dice_game/backups}"
MAX_BACKUPS="${MAX_BACKUPS:-20}"  # Keep last 20 backups

cd "$DEPLOY_DIR" || exit 1

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Log file
LOG_FILE="$BACKUP_DIR/backup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting automated backup..."

# Check if database is running
if ! docker compose ps db | grep -q Up; then
    log "ERROR: Database is not running, cannot create backup"
    exit 1
fi

# Create backup
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
BACKUP_FILE_COMPRESSED="${BACKUP_FILE}.gz"

if docker compose exec -T db pg_dump -U postgres dice_game > "$BACKUP_FILE" 2>/dev/null; then
    # Compress backup
    gzip "$BACKUP_FILE"
    BACKUP_SIZE=$(du -h "$BACKUP_FILE_COMPRESSED" | cut -f1)
    log "✅ Backup created successfully: $BACKUP_FILE_COMPRESSED ($BACKUP_SIZE)"
    
    # Cleanup old backups (keep last MAX_BACKUPS)
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
        DELETED=$(ls -t "$BACKUP_DIR"/backup_*.sql.gz | tail -n +$((MAX_BACKUPS + 1)) | wc -l)
        ls -t "$BACKUP_DIR"/backup_*.sql.gz | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm -f
        log "🧹 Cleaned up $DELETED old backup(s), keeping last $MAX_BACKUPS"
    fi
    
    # Verify backup integrity
    if gzip -t "$BACKUP_FILE_COMPRESSED" 2>/dev/null; then
        log "✅ Backup integrity verified"
    else
        log "⚠️  WARNING: Backup file may be corrupted!"
    fi
else
    log "❌ ERROR: Backup failed!"
    exit 1
fi

log "Backup completed successfully"
exit 0






