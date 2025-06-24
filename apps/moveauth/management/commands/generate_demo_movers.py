from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.mover.models import Mover
import getpass
import json


class Command(BaseCommand):
    help = 'Import demo movers'

    def handle(self, *args, **options):
        User = get_user_model()
        import pdb; pdb.set_trace()
        group = Group.objects.get(name="Mover")
        with open("data/demo_drivers.json") as f:
            users = json.load(f)
            for user in users:
                print(f"email: {user['email']}")
                mover = User.objects.create_user(email=user['email'], password=user['password'], account_type="MOVER", first_name=user['first_name'], last_name=user['last_name'])
                mover.groups.add(group)
                Mover.objects.create(user=mover)

