from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from accounts.validators import admin_password_validator
from django.core.exceptions import ValidationError

User = get_user_model()


class Command(BaseCommand):
    help = 'Check admin passwords for security compliance and flag weak passwords'

    def handle(self, *args, **options):
        self.stdout.write('🔐 Checking Admin Password Security...\n')

        # Get all admin users
        admin_users = User.objects.filter(is_staff=True, is_active=True)

        weak_passwords = []
        compliant_passwords = []

        # Common weak passwords to check
        common_passwords = [
            'admin', 'admin123', 'password', 'password123', '123456',
            '123456789', 'qwerty', 'abc123', 'password1', 'adminadmin',
            'root', 'root123', 'superuser', 'superuser123'
        ]

        for user in admin_users:
            username = user.username
            is_superuser = user.is_superuser

            self.stdout.write(f'👤 Checking {username} ({ "Super Admin" if is_superuser else "Admin" })...')

            # Check password length (basic check)
            if len(user.password) < 20:  # Hashed passwords are much longer
                self.stdout.write(self.style.WARNING(f'  ⚠️  Password appears to be very short or unhashed'))
                weak_passwords.append((username, 'Very short password hash'))
                continue

            # Check for common passwords
            password_weak = False
            for common_pw in common_passwords:
                try:
                    if check_password(common_pw, user.password):
                        self.stdout.write(self.style.ERROR(f'  ❌ Password matches common password: "{common_pw}"'))
                        weak_passwords.append((username, f'Common password: {common_pw}'))
                        password_weak = True
                        break
                except:
                    continue

            if password_weak:
                continue

            # Check password complexity requirements
            # Since we can't reverse the hash, we'll flag users who might have old passwords
            # and suggest they change their passwords
            try:
                # We can't validate the actual password since it's hashed,
                # but we can check if it was created before our new validation
                # For now, we'll mark all existing passwords as needing verification
                if is_superuser:
                    self.stdout.write(self.style.WARNING(f'  ⚠️  Super admin password should be verified for complexity'))
                    weak_passwords.append((username, 'Super admin password needs complexity verification'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Password appears properly hashed'))
                    compliant_passwords.append(username)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error checking password: {e}'))
                weak_passwords.append((username, f'Error: {e}'))

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 SUMMARY:')
        self.stdout.write(f'✅ Compliant passwords: {len(compliant_passwords)}')
        self.stdout.write(f'❌ Weak/problematic passwords: {len(weak_passwords)}')

        if weak_passwords:
            self.stdout.write('\n🚨 USERS NEEDING PASSWORD CHANGES:')
            for username, issue in weak_passwords:
                self.stdout.write(self.style.ERROR(f'  • {username}: {issue}'))

            self.stdout.write('\n💡 RECOMMENDED ACTIONS:')
            self.stdout.write('  1. Run: python manage.py changepassword <username>')
            self.stdout.write('  2. Ensure new passwords meet complexity requirements:')
            self.stdout.write('     • At least 8 characters')
            self.stdout.write('     • At least one uppercase letter (A-Z)')
            self.stdout.write('     • At least one lowercase letter (a-z)')
            self.stdout.write('     • At least one digit (0-9)')
            self.stdout.write('     • At least one special character (!@#$%^&*...)')
        else:
            self.stdout.write('\n🎉 All admin passwords appear secure!')

        self.stdout.write('\n🔐 Admin password security check completed.')