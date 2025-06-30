from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.mover.models import Mover, Vehicle
import getpass
import json


class Command(BaseCommand):
    help = 'Add vechicle to mover'

    def handle(self, *args, **options):
        all_movers = Mover.objects.all()
        all_vehicles = Vehicle.objects.all()
        vechicles = list(all_vehicles)
        for mover in all_movers:
            if not mover.vehicle:
                vehicle = vechicles.pop()
                mover.vehicle = vehicle
                mover.is_vehicle_added = True
                mover.save()