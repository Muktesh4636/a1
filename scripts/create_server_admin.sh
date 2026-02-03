#!/bin/bash

# Script to create/update admin user on the deployment server
# Usage: Run this script on the server or via SSH

echo "🔐 Creating/Updating Admin User on Server..."
echo "=============================================="
echo ""

# Server details
SERVER_HOST="${SERVER_HOST:-72.61.254.71}"
SERVER_USER="${SERVER_USER:-root}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/dice_game}"

# User credentials
ADMIN_USERNAME="${ADMIN_USERNAME:-muktesh}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-muktesh123}"
ADMIN_EMAIL="${ADMIN_EMAIL:-muktesh@example.com}"

echo "Username: $ADMIN_USERNAME"
echo "Password: $ADMIN_PASSWORD"
echo "Email: $ADMIN_EMAIL"
echo ""

# Commands to run on server
SSH_COMMANDS="
set -e
cd ${DEPLOY_DIR}/backend || cd ${DEPLOY_DIR}

echo '📦 Checking Docker environment...'
if docker ps | grep -q 'dice_game_web'; then
    echo '✅ Docker containers found'
    echo ''
    echo '🔧 Creating/updating admin user...'
    docker compose exec -T web python manage.py shell << 'PYTHON_EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dice_game.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import authenticate

username = '${ADMIN_USERNAME}'
password = '${ADMIN_PASSWORD}'
email = '${ADMIN_EMAIL}'

try:
    user = User.objects.filter(username=username).first()
    
    if user:
        print(f'User \"{username}\" already exists. Updating to admin...')
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.email = email
        user.is_active = True
        user.save()
        print(f'✅ User \"{username}\" updated successfully!')
    else:
        print(f'Creating new admin user \"{username}\"...')
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f'✅ Admin user \"{username}\" created successfully!')
    
    # Verify
    auth = authenticate(username=username, password=password)
    if auth:
        print('✅ Authentication test: PASSED')
    else:
        print('❌ Authentication test: FAILED')
    
    print('')
    print('Admin credentials:')
    print(f'  Username: {username}')
    print(f'  Password: {password}')
    print(f'  Email: {email}')
    print(f'  Superuser: {user.is_superuser}')
    print(f'  Staff: {user.is_staff}')
    print(f'  Active: {user.is_active}')
    print('')
    print(f'🔐 Login URL: http://${SERVER_HOST}:8232/game-admin/login/')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
PYTHON_EOF

else
    echo '⚠️  Docker containers not found. Trying local execution...'
    cd backend || cd .
    python3 manage.py shell << 'PYTHON_EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dice_game.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import authenticate

username = '${ADMIN_USERNAME}'
password = '${ADMIN_PASSWORD}'
email = '${ADMIN_EMAIL}'

try:
    user = User.objects.filter(username=username).first()
    
    if user:
        print(f'User \"{username}\" already exists. Updating to admin...')
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.email = email
        user.is_active = True
        user.save()
        print(f'✅ User \"{username}\" updated successfully!')
    else:
        print(f'Creating new admin user \"{username}\"...')
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f'✅ Admin user \"{username}\" created successfully!')
    
    # Verify
    auth = authenticate(username=username, password=password)
    if auth:
        print('✅ Authentication test: PASSED')
    else:
        print('❌ Authentication test: FAILED')
    
    print('')
    print('Admin credentials:')
    print(f'  Username: {username}')
    print(f'  Password: {password}')
    print(f'  Email: {email}')
    print(f'  Superuser: {user.is_superuser}')
    print(f'  Staff: {user.is_staff}')
    print(f'  Active: {user.is_active}')
    print('')
    print(f'🔐 Login URL: http://${SERVER_HOST}:8232/game-admin/login/')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
PYTHON_EOF
fi

echo ''
echo '✅ Done!'
"

# Check if running locally or need to SSH
if [ "$1" = "local" ] || [ -d "${DEPLOY_DIR}" ]; then
    echo "Running commands locally..."
    eval "$SSH_COMMANDS"
else
    echo "Connecting to remote server via SSH..."
    echo "Server: ${SERVER_USER}@${SERVER_HOST}"
    echo ""
    echo "Run these commands on your deployment server:"
    echo "----------------------------------------------"
    echo "$SSH_COMMANDS"
    echo ""
    echo "Or SSH into server and run:"
    echo "ssh ${SERVER_USER}@${SERVER_HOST}"
    echo "cd ${DEPLOY_DIR}/backend"
    echo "docker compose exec -T web python manage.py shell"
    echo ""
    echo "Then paste the Python code from the script above."
fi

