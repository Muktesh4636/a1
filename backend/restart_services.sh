#!/bin/bash

# Restart all game services
# Usage: ./restart_services.sh

cd "$(dirname "$0")"

echo "🛑 Stopping all services..."
pkill -f "start_game_timer" 2>/dev/null
pkill -f "daphne -b 0.0.0.0 -p 8232 dice_game.asgi:application" 2>/dev/null
pkill -f "manage.py runserver" 2>/dev/null
sleep 2

echo "✅ Services stopped"
echo ""
echo "🚀 Starting services..."

# Activate virtual environment
source venv/bin/activate

# Create logs directory if it doesn't exist
mkdir -p logs

# Start game timer in background with logs
echo "Starting game timer..."
python manage.py start_game_timer >> logs/game_timer.log 2>&1 &

# Start ASGI server (Daphne) in background with logs
echo "Starting Daphne ASGI server on port 8232..."
AUTOBAHN_USE_NVX=0 daphne -b 0.0.0.0 -p 8232 dice_game.asgi:application >> logs/django_server.log 2>&1 &

sleep 3

# Verify services are running
TIMER_COUNT=$(ps aux | grep -E "start_game_timer" | grep -v grep | wc -l | tr -d ' ')
SERVER_COUNT=$(ps aux | grep -E "daphne -b 0.0.0.0 -p 8232 dice_game.asgi:application" | grep -v grep | wc -l | tr -d ' ')

if [ "$TIMER_COUNT" -gt 0 ] && [ "$SERVER_COUNT" -gt 0 ]; then
    echo "✅ All services restarted successfully!"
    echo "   - Game Timer: Running"
    echo "   - Daphne ASGI Server: Running on port 8232"
else
    echo "⚠️  Warning: Some services may not have started properly"
    echo "   - Game Timer processes: $TIMER_COUNT"
    echo "   - Django Server processes: $SERVER_COUNT"
fi

