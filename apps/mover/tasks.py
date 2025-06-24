# vehicles/tasks.py
from celery import shared_task
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from .models import VehicleImage

def resize_image(image_field, size):
    image = Image.open(image_field)
    image.convert('RGB')
    image.thumbnail(size)

    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)
    return ContentFile(buffer.read())

@shared_task
def generate_vehicle_image_versions(image_id):
    try:
        instance = VehicleImage.objects.get(id=image_id)
        original_filename = instance.original.name.split('/')[-1].split('.')[0]

        sizes = {
            'thumbnail': (100, 100),
            'medium': (300, 300),
            'large': (600, 600),
        }

        thumb_file = resize_image(instance.original, sizes['thumbnail'])
        instance.thumbnail.save(f"{original_filename}_thumb.jpg", thumb_file, save=False)

        medium_file = resize_image(instance.original, sizes['medium'])
        instance.medium.save(f"{original_filename}_medium.jpg", medium_file, save=False)

        large_file = resize_image(instance.original, sizes['large'])
        instance.large.save(f"{original_filename}_large.jpg", large_file, save=False)

        instance.save()
    except VehicleImage.DoesNotExist:
        pass
