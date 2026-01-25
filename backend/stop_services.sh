#!/bin/bash

# Stop all game services
# Usage: ./stop_services.sh

echo "🛑 Stopping all services..."

# Stop game timer
pkill -f "start_game_timer" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Game timer stopped"
else
    echo "ℹ️  Game timer was not running"
fi

# Stop Django server
pkill -f "daphne -b 0.0.0.0 -p 8232 dice_game.asgi:application" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Daphne ASGI server stopped"
else
    echo "ℹ️  Daphne ASGI server was not running"
fi

sleep 1

# Verify all services are stopped
TIMER_COUNT=$(ps aux | grep -E "start_game_timer" | grep -v grep | wc -l | tr -d ' ')
SERVER_COUNT=$(ps aux | grep -E "daphne -b 0.0.0.0 -p 8232 dice_game.asgi:application" | grep -v grep | wc -l | tr -d ' ')

if [ "$TIMER_COUNT" -eq 0 ] && [ "$SERVER_COUNT" -eq 0 ]; then
    echo ""
    echo "✅ All services stopped successfully!"
else
    echo ""
    echo "⚠️  Warning: Some processes may still be running"
    echo "   - Game Timer processes: $TIMER_COUNT"
    echo "   - Daphne ASGI Server processes: $SERVER_COUNT"
fi



