#!/bin/bash

# Script to verify and create admin user on server
# This will check if user exists and create/update if needed

echo "🔍 Verifying and Creating Admin User on Server..."
echo "=================================================="
echo ""

# Server details
SERVER_HOST="72.61.254.71"
SERVER_USER="root"
DEPLOY_DIR="/opt/dice_game"

# User credentials
ADMIN_USERNAME="muktesh"
ADMIN_PASSWORD="muktesh123"
ADMIN_EMAIL="muktesh@example.com"

echo "Server: ${SERVER_USER}@${SERVER_HOST}"
echo "Username: ${ADMIN_USERNAME}"
echo ""

# Create the Python script to run
cat > /tmp/create_admin_server.py << 'PYTHON_SCRIPT'
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dice_game.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import authenticate

username = 'muktesh'
password = 'muktesh123'
email = 'muktesh@example.com'

print(f"Checking for user: {username}")
print("-" * 50)

try:
    user = User.objects.filter(username=username).first()
    
    if user:
        print(f"✅ User '{username}' EXISTS")
        print(f"   Email: {user.email}")
        print(f"   Superuser: {user.is_superuser}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Active: {user.is_active}")
        print("")
        print("Updating user...")
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.email = email
        user.is_active = True
        user.save()
        print("✅ User updated successfully!")
    else:
        print(f"❌ User '{username}' NOT FOUND")
        print("")
        print("Creating new admin user...")
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print("✅ User created successfully!")
    
    print("")
    print("Verifying authentication...")
    auth = authenticate(username=username, password=password)
    
    if auth:
        print("✅ Authentication test: PASSED")
        print("")
        print("=" * 50)
        print("SUCCESS! User is ready to login")
        print("=" * 50)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Login URL: http://72.61.254.71:8232/game-admin/login/")
    else:
        print("❌ Authentication test: FAILED")
        print("Password may not be set correctly")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

echo "📋 Commands to run on server:"
echo "=============================="
echo ""
echo "SSH into server:"
echo "  ssh ${SERVER_USER}@${SERVER_HOST}"
echo ""
echo "Then run:"
echo "  cd ${DEPLOY_DIR}/backend"
echo "  docker compose exec -T web python manage.py shell < /tmp/create_admin_server.py"
echo ""
echo "Or copy and paste this command:"
echo "--------------------------------"
echo "docker compose exec -T web python manage.py shell << 'EOF'"
cat /tmp/create_admin_server.py
echo "EOF"
echo ""

# Cleanup
rm -f /tmp/create_admin_server.py

