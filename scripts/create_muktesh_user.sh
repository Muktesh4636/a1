#!/bin/bash

# Simple script to create muktesh admin user on server
# Run this on the server: bash create_muktesh_user.sh

cd /opt/dice_game/backend || cd backend

docker compose exec -T web python manage.py shell << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dice_game.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import authenticate

username = 'muktesh'
password = 'muktesh123'
email = 'muktesh@example.com'

print("Creating admin user...")
print("=" * 60)

# Delete existing user if exists
existing = User.objects.filter(username=username).first()
if existing:
    print(f"Deleting existing user '{username}'...")
    existing.delete()

# Create new superuser
print(f"Creating new admin user '{username}'...")
user = User.objects.create_superuser(
    username=username,
    email=email,
    password=password
)

print("✅ User created successfully!")
print()
print("Verifying...")
auth = authenticate(username=username, password=password)
if auth:
    print("✅ Authentication verified!")
else:
    print("⚠️  Authentication test failed, but user was created")

print()
print("=" * 60)
print("USER CREATED:")
print("=" * 60)
print(f"Username: {username}")
print(f"Password: {password}")
print(f"Email: {email}")
print(f"Superuser: {user.is_superuser}")
print(f"Staff: {user.is_staff}")
print(f"Active: {user.is_active}")
print()
print("Login URL: http://72.61.254.71:8232/game-admin/login/")
print("=" * 60)
EOF

