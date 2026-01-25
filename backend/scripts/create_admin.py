#!/usr/bin/env python
"""
Script to create a Django superuser (admin) for the dice game
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dice_game.settings')
django.setup()

from accounts.models import User

def create_admin(username='admin', password='admin123', email='admin@example.com'):
    """Create a Django superuser"""
    try:
        # Check if user exists
        user = User.objects.filter(username=username).first()
        if user:
            if user.is_superuser:
                print(f"✅ Superuser '{username}' already exists!")
                print(f"Password: {password}")
                print(f"Email: {email}")
                return user
            else:
                # Make existing user a superuser
                user.is_superuser = True
                user.is_staff = True
                user.set_password(password)
                user.save()
                print(f"✅ User '{username}' is now a superuser!")
                print(f"Password: {password}")
                return user
        
        # Create new superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        print(f"✅ Superuser created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Email: {email}")
        print(f"\n🔐 You can now login to Django Admin at:")
        print(f"   http://localhost:8000/admin/")
        
        return user
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return None

if __name__ == '__main__':
    import sys
    
    # Get credentials from command line or use defaults
    username = sys.argv[1] if len(sys.argv) > 1 else 'admin'
    password = sys.argv[2] if len(sys.argv) > 2 else 'admin123'
    email = sys.argv[3] if len(sys.argv) > 3 else 'admin@example.com'
    
    create_admin(username, password, email)



