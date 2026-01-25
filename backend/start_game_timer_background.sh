#!/bin/bash

# Start game timer in background with logs saved to file
# Usage: ./start_game_timer_background.sh

cd "$(dirname "$0")"
source venv/bin/activate

# Create logs directory if it doesn't exist
mkdir -p logs

# Start game timer with output redirected to log file
echo "Starting game timer in background..."
echo "Logs will be saved to: logs/game_timer.log"
echo "View logs with: tail -f logs/game_timer.log"

python manage.py start_game_timer >> logs/game_timer.log 2>&1 &

echo "Game timer started (PID: $!)"
echo "To view logs: tail -f logs/game_timer.log"







