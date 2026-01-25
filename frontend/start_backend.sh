#!/bin/bash

echo "🚀 Starting Django Backend Server..."
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Error: 'backend' directory not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Check if database needs migration
echo "🗄️  Checking database..."
python manage.py migrate --check > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "🔄 Running database migrations..."
    python manage.py migrate
fi

# Check if test user exists, if not create one
echo "👤 Checking test user..."
python create_test_user.py > /dev/null 2>&1

# Start server
echo ""
echo "✅ Starting Django server on http://localhost:8000"
echo "📝 Test credentials:"
echo "   Username: test"
echo "   Password: test123"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python manage.py runserver








