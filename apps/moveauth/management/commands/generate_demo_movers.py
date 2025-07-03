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
        # import pdb; pdb.set_trace()
        group = Group.objects.get(name="Mover")
        with open("data/demo_movers.json") as f:
            users = json.load(f)
            for user in users:
                print(f"email: {user['email']}")
                mover = User.objects.create_user(
                    email=user['email'], 
                    password=user['password'], 
                    role="MOVER", 
                    first_name=user['first_name'], 
                    last_name=user['last_name'],
                    dob=user['dob'],
                    gender=user['gender']
                )
                mover.groups.add(group)
                mover = Mover.objects.create(user=mover)
                mover.driving_licence_number = user['driving_licence_number']
                mover.phone_number = user['phone_number']
                mover.save()

