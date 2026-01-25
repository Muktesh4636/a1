#!/bin/bash

# Comprehensive script to fix admin login issues
# This will check, create, and verify the admin user

cat << 'PYTHON_SCRIPT'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dice_game.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import authenticate

username = 'muktesh'
password = 'muktesh123'
email = 'muktesh@example.com'

print("=" * 70)
print("ADMIN USER DIAGNOSTIC AND FIX")
print("=" * 70)
print()

# Step 1: List all users
print("Step 1: Checking all users in database...")
print("-" * 70)
all_users = User.objects.all()
print(f"Total users: {all_users.count()}")
for u in all_users:
    print(f"  - {u.username} (superuser: {u.is_superuser}, staff: {u.is_staff}, active: {u.is_active})")
print()

# Step 2: Check if muktesh exists
print("Step 2: Checking for 'muktesh' user...")
print("-" * 70)
user = User.objects.filter(username=username).first()

if user:
    print(f"✅ User '{username}' EXISTS")
    print(f"   ID: {user.id}")
    print(f"   Email: {user.email}")
    print(f"   Superuser: {user.is_superuser}")
    print(f"   Staff: {user.is_staff}")
    print(f"   Active: {user.is_active}")
    print(f"   Date Joined: {user.date_joined}")
    print()
    print("Updating user with correct settings...")
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.email = email
    user.is_active = True
    user.save()
    print("✅ User updated!")
else:
    print(f"❌ User '{username}' NOT FOUND")
    print()
    print("Creating new admin user...")
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print("✅ User created!")
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

print()
print("Step 3: Verifying authentication...")
print("-" * 70)

# Test authentication multiple ways
auth1 = authenticate(username=username, password=password)
if auth1:
    print("✅ Authentication with username/password: PASSED")
else:
    print("❌ Authentication with username/password: FAILED")

# Also try with request=None (some Django versions need this)
try:
    auth2 = authenticate(request=None, username=username, password=password)
    if auth2:
        print("✅ Authentication with request=None: PASSED")
    else:
        print("❌ Authentication with request=None: FAILED")
except:
    pass

# Verify user object directly
user.refresh_from_db()
print()
print("Step 4: Final user status...")
print("-" * 70)
print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Superuser: {user.is_superuser}")
print(f"Staff: {user.is_staff}")
print(f"Active: {user.is_active}")
print(f"Has usable password: {user.has_usable_password()}")

# Check password hash
if hasattr(user, 'password'):
    print(f"Password hash exists: {len(user.password) > 0}")

print()
print("=" * 70)
if auth1:
    print("✅ SUCCESS! User is ready to login")
    print("=" * 70)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Login URL: http://159.198.46.36:8232/game-admin/login/")
    print("=" * 70)
else:
    print("❌ WARNING: Authentication test failed")
    print("=" * 70)
    print("The user exists but authentication is not working.")
    print("This might be a Django authentication backend issue.")
    print("Try logging in anyway - sometimes the test fails but login works.")
    print("=" * 70)
PYTHON_SCRIPT

