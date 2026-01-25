#!/bin/bash

# Script to create database on deployment server
# Run this on your server

echo "🗄️  Creating PostgreSQL Database..."
echo "==================================="
echo ""

cd /opt/dice_game || exit 1

# Get database credentials from environment or docker-compose
DB_NAME="${DB_NAME:-dice_game}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"

echo "Creating database: $DB_NAME"
echo "User: $DB_USER"
echo ""

# Create database using docker exec
docker compose exec -T db psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" 2>&1 || {
    echo "Database might already exist, checking..."
    docker compose exec -T db psql -U "$DB_USER" -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" | grep -q 1 && {
        echo "✅ Database $DB_NAME already exists"
    } || {
        echo "❌ Failed to create database"
        exit 1
    }
}

echo ""
echo "✅ Database check complete"
echo ""

# Now run migrations
echo "🔄 Running migrations..."
docker compose exec -T web python manage.py migrate --noinput || {
    echo "⚠️  Migration failed - web service might not be accessible yet"
    echo "Wait for web service to start, then run:"
    echo "  docker compose exec web python manage.py migrate"
}

echo ""
echo "✅ Done!"












