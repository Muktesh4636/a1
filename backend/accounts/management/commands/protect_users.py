"""
Management command to check user count and warn if database appears empty
Run this before migrations or operations that might affect data
"""
from django.core.management.base import BaseCommand, CommandError
from accounts.models import User


class Command(BaseCommand):
    help = 'Check user count and warn if database appears to have been reset'

    def add_arguments(self, parser):
        parser.add_argument(
            '--allow-empty',
            action='store_true',
            help='Allow empty database (for initial setup)',
        )
        parser.add_argument(
            '--warn-only',
            action='store_true',
            help='Only warn, do not raise error',
        )

    def handle(self, *args, **options):
        user_count = User.objects.count()
        
        if user_count == 0:
            self.stdout.write(self.style.ERROR(''))
            self.stdout.write(self.style.ERROR('⚠️  ⚠️  ⚠️  WARNING: NO USERS FOUND IN DATABASE ⚠️  ⚠️  ⚠️'))
            self.stdout.write(self.style.ERROR(''))
            self.stdout.write(self.style.ERROR('This might indicate:'))
            self.stdout.write(self.style.ERROR('  1. Database was flushed/reset'))
            self.stdout.write(self.style.ERROR('  2. Data was accidentally deleted'))
            self.stdout.write(self.style.ERROR('  3. Fresh database initialization'))
            self.stdout.write(self.style.ERROR(''))
            
            if options['allow_empty']:
                self.stdout.write(self.style.WARNING('⚠️  Proceeding with empty database (--allow-empty flag set)'))
                return 0
            elif options['warn_only']:
                self.stdout.write(self.style.WARNING('⚠️  Warning only mode - proceeding anyway'))
                return 0
            else:
                self.stdout.write(self.style.WARNING('To proceed with empty database, use --allow-empty flag'))
                self.stdout.write(self.style.ERROR(''))
                raise CommandError("Database appears empty - use --allow-empty to proceed")
        
        self.stdout.write(self.style.SUCCESS(f'✅ User count check passed: {user_count} users found'))
        return user_count
