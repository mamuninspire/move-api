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
        "origin": f"{pickup['lat']},{pickup['lon']}",
        "destination": f"{dropoff['lat']},{dropoff['lon']}",
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
        "origin": f"{pickup['lat']},{pickup['lon']}",
        "destination": f"{dropoff['lat']},{dropoff['lon']}",
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


# def process_driver(driver):
#     """Process single driver and return data dict"""
#     driver_data = {
#         'ride_search_id': ride_search_id,
#         'mover_id': driver.mover_id,
#         'driver_name': driver.user.get_full_name(),
#         'rating': driver.rating,
#         'phone': driver.get_contact,
#         'license': driver.driving_licence_number,
#         'make': driver.get_vehicle_make.name if driver.get_vehicle_make else None,
#         'model': driver.get_vehicle_model,
#         'capacity': driver.capacity,
#         'available': driver.available,
#         'image': driver.vehicle.get_hero_image_url() if driver.vehicle else None,
#         'duration_type': duration_type,
#         'estimated_cost': None
#     }

#     # Estimate cost
#     if booking_type == "reservation" and driver.vehicle:
#         driver_data['estimated_cost'] = (
#             driver.vehicle.rate_per_day if duration_type == "DAY"
#             else driver.vehicle.rate_per_hour
#         )

#     elif booking_type == "single" and driver.vehicle:
#         # Call Google API
#         distance_result = get_distance_duration(pickup, dropoff, api_key)
#         if distance_result:
#             distance_km = distance_result.get('distance_meters', 0) / 1000
#             driver_data['estimated_cost'] = round(
#                 driver.vehicle.rate_per_km * Decimal(str(distance_km)), 2
#             )
#         else:
#             driver_data['estimated_cost'] = None

#     return driver_data