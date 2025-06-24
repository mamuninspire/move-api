from django.utils.deconstruct import deconstructible
from django.core.files.storage import default_storage

import httpx


@deconstructible
class VehicleImageUploadTo:
    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        vehicle_id = instance.vehicle.id if instance.vehicle else 'unknown'
        filename = f"{vehicle_id}-{self.field_name}.{ext}"
        file_path = f"vehicles/original/{filename}"

        # Delete file if already exists
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        return file_path

def document_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    return f"vehicles/documents/{instance.vehicle.id}-{instance.doc_type.name}.{ext}"


@deconstructible
class ImageUploadTo:
    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        vehicle_id = instance.vehicle.id if instance.vehicle else 'unknown'
        filename = f"{vehicle_id}-{self.field_name}.{ext}"
        file_path = f"images/{filename}"

        # Delete file if already exists
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        return file_path



async def get_distance_duration_async(pickup, dropoff, api_key):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{pickup['lat']},{pickup['lang']}",
        "destination": f"{dropoff['lat']},{dropoff['lang']}",
        "key": api_key
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if data['status'] == 'OK':
        leg = data['routes'][0]['legs'][0]
        return {
            "distance_text": leg['distance']['text'],
            "distance_meters": leg['distance']['value'],
            "duration_text": leg['duration']['text'],
            "duration_seconds": leg['duration']['value']
        }
    else:
        return {"error": data.get("error_message", "No route found")}


import requests

def get_distance_duration(pickup, dropoff, api_key):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{pickup['lat']},{pickup['lang']}",
        "destination": f"{dropoff['lat']},{dropoff['lang']}",
        "key": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        leg = data['routes'][0]['legs'][0]
        return {
            "distance_text": leg['distance']['text'],
            "distance_meters": leg['distance']['value'],
            "duration_text": leg['duration']['text'],
            "duration_seconds": leg['duration']['value']
        }
    else:
        return {"error": data.get("error_message", "No route found")}
