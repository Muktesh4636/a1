#!/bin/bash

# Script to update muktesh admin password on the server
# Run this on the deployment server

echo "Updating muktesh admin password on server..."

cd /opt/dice_game/backend || cd backend

# Check if we're in a Docker environment
if [ -f "docker-compose.yml" ] || docker ps | grep -q "dice_game"; then
    echo "Running in Docker environment..."
    docker compose exec -T web python manage.py shell << EOF
from accounts.models import User
from django.contrib.auth import authenticate

u = User.objects.filter(username='muktesh').first()
if u:
    u.set_password('muktesh123')
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print('✅ Password updated successfully!')
    auth = authenticate(username='muktesh', password='muktesh123')
    print(f'Authentication test: {auth is not None}')
    print(f'Superuser: {u.is_superuser}, Staff: {u.is_staff}')
else:
    print('❌ User muktesh not found!')
EOF
else
    echo "Running locally..."
    python3 manage.py shell << EOF
from accounts.models import User
from django.contrib.auth import authenticate

u = User.objects.filter(username='muktesh').first()
if u:
    u.set_password('muktesh123')
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print('✅ Password updated successfully!')
    auth = authenticate(username='muktesh', password='muktesh123')
    print(f'Authentication test: {auth is not None}')
    print(f'Superuser: {u.is_superuser}, Staff: {u.is_staff}')
else:
    print('❌ User muktesh not found!')
EOF
fi

echo ""
echo "✅ Done! You can now login with:"
echo "   Username: muktesh"
echo "   Password: muktesh123"
echo "   URL: http://159.198.46.36:8232/game-admin/login/"

