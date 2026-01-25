#!/bin/bash

# Start game timer with logs visible in terminal
# Usage: ./start_game_timer_with_logs.sh

cd "$(dirname "$0")"
source venv/bin/activate

echo "Starting game timer (logs will be visible in this terminal)..."
echo "Press Ctrl+C to stop"
echo ""

python manage.py start_game_timer







