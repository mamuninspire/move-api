from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import getpass


class Command(BaseCommand):
    help = 'Creates a new customer user'

    def add_arguments(self, parser):
        parser.add_argument('email', nargs='?', type=str, help='Email address of the customer')
        parser.add_argument('password', nargs='?', type=str, help='Password for the customer')
        parser.add_argument('--first_name', type=str, default='', help='First name of the customer')
        parser.add_argument('--last_name', type=str, default='', help='Last name of the customer')

    def handle(self, *args, **options):
        User = get_user_model()
        email = options['email']
        password = options['password']
        first_name = options.get('first_name', '')
        last_name = options.get('last_name', '')

        if not email:
            email = input("Email: ").strip()

        if not password:
            password = getpass.getpass("Password: ")

        try:
            user = User.objects.create_customer(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Add user to their respective group
            try:
                group = Group.objects.get(name__iexact="Customer")
                user.groups.add(group)
            except Group.DoesNotExist:
                pass

            self.stdout.write(self.style.SUCCESS(f'Successfully created customer: {email}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error creating customer: {e}'))
