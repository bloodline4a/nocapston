from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a generic user'

    def handle(self, *args, **options):
        username = 'trilcmean'
        email = 'trilcenterprises@gmail.com'
        password = 'trilcenterprises'

        user = User.objects.create_user(username=username, email=email, password=password)

        self.stdout.write(self.style.SUCCESS(f'Successfully created user: {user.username}'))
