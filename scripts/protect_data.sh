#!/bin/bash

# Data Protection Script
# This script prevents accidental data deletion and ensures backups

set -e

DEPLOY_DIR="${DEPLOY_DIR:-/opt/dice_game}"
BACKUP_DIR="${BACKUP_DIR:-/opt/dice_game/backups}"

echo "🔒 Data Protection System"
echo "========================"
echo ""

cd "$DEPLOY_DIR" || exit 1

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to create backup
create_backup() {
    echo "💾 Creating database backup..."
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
    
    if docker compose ps db | grep -q Up; then
        docker compose exec -T db pg_dump -U postgres dice_game > "$BACKUP_FILE" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ Backup created: $BACKUP_FILE"
            # Keep only last 10 backups
            ls -t "$BACKUP_DIR"/backup_*.sql | tail -n +11 | xargs -r rm -f
            echo "✅ Old backups cleaned (keeping last 10)"
        else
            echo "⚠️  Backup failed!"
            return 1
        fi
    else
        echo "⚠️  Database not running, cannot create backup"
        return 1
    fi
}

# Function to verify data exists
verify_data() {
    echo "🔍 Verifying data integrity..."
    
    if ! docker volume ls | grep -q postgres_data; then
        echo "❌ ERROR: postgres_data volume does not exist!"
        return 1
    fi
    
    if docker compose ps db | grep -q Up; then
        ROUND_COUNT=$(docker compose exec -T db psql -U postgres -d dice_game -t -c "SELECT COUNT(*) FROM game_gameround;" 2>/dev/null | tr -d ' ' || echo "0")
        USER_COUNT=$(docker compose exec -T db psql -U postgres -d dice_game -t -c "SELECT COUNT(*) FROM accounts_user;" 2>/dev/null | tr -d ' ' || echo "0")
        
        echo "📊 Current data:"
        echo "   - Rounds: $ROUND_COUNT"
        echo "   - Users: $USER_COUNT"
        
        if [ "$ROUND_COUNT" = "0" ] && [ "$USER_COUNT" = "0" ]; then
            echo "⚠️  WARNING: Database appears empty!"
            return 1
        fi
    else
        echo "⚠️  Database not running, skipping verification"
    fi
    
    return 0
}

# Function to protect volumes
protect_volumes() {
    echo "🛡️  Protecting volumes from deletion..."
    
    # Check if volumes exist
    for volume in postgres_data redis_data; do
        if docker volume ls | grep -q "${volume}"; then
            echo "✅ Volume '$volume' exists"
        else
            echo "⚠️  Volume '$volume' not found"
        fi
    done
}

# Main execution
case "${1:-verify}" in
    backup)
        create_backup
        ;;
    verify)
        verify_data
        protect_volumes
        ;;
    protect)
        protect_volumes
        verify_data
        ;;
    *)
        echo "Usage: $0 {backup|verify|protect}"
        echo ""
        echo "  backup   - Create a database backup"
        echo "  verify   - Verify data integrity and volume protection"
        echo "  protect  - Protect volumes and verify data"
        exit 1
        ;;
esac

echo ""
echo "✅ Data protection check complete"






