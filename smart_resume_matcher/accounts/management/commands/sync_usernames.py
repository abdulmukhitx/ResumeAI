from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User

class Command(BaseCommand):
    help = 'Sync all user usernames with their email addresses to prevent conflicts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting username sync...') if hasattr(self.style, 'SUCCESS') else 'Starting username sync...')
        
        updated_count = 0
        
        with transaction.atomic():
            for user in User.objects.all():
                if user.username != user.email:
                    old_username = user.username
                    user.username = user.email
                    user.save(update_fields=['username'])
                    updated_count += 1
                    self.stdout.write(
                        f'Updated user: {old_username} -> {user.email}'
                    )
        
        self.stdout.write(
            f'Successfully synced {updated_count} users. '
            f'Total users: {User.objects.count()}'
        )
