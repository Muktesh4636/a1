# Quick Guide: Create Admin User on Server

## Method 1: SSH and Run Command (Fastest)

SSH into your server and run:

```bash
ssh root@72.61.254.71
cd /opt/dice_game/backend
docker compose exec -T web python manage.py shell << 'EOF'
from accounts.models import User
from django.contrib.auth import authenticate

username = 'muktesh'
password = 'muktesh123'
email = 'muktesh@example.com'

user = User.objects.filter(username=username).first()
if user:
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.email = email
    user.is_active = True
    user.save()
    print('✅ User updated!')
else:
    user = User.objects.create_superuser(username=username, email=email, password=password)
    print('✅ User created!')

auth = authenticate(username=username, password=password)
print(f'Auth test: {auth is not None}')
print(f'Superuser: {user.is_superuser}, Staff: {user.is_staff}')
EOF
```

## Method 2: Use the Script

Run the script on the server:

```bash
ssh root@72.61.254.71
cd /opt/dice_game
bash scripts/create_server_admin.sh local
```

## Login After Creation

- **URL:** http://72.61.254.71:8232/game-admin/login/
- **Username:** muktesh
- **Password:** muktesh123

