#!/bin/bash
# Run Django server for local development with media file serving

cd "$(dirname "$0")/.."
cd backend

echo "🚀 Starting Django Development Server..."
echo "=========================================="
echo ""
echo "✅ DEBUG=True (media files will be served)"
echo "✅ ALLOWED_HOSTS includes localhost"
echo "🌐 Server will be at: http://127.0.0.1:8004/"
echo "🔐 Admin panel: http://127.0.0.1:8004/game-admin/login/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run with DEBUG=True to serve media files
DEBUG=True python3 manage.py runserver 8004