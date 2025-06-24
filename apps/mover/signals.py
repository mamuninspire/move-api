from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VehicleImages

# Utility function to resize image
def resize_image(image_field, size):
    image = Image.open(image_field)
    image.convert('RGB')  # Ensure consistent format
    image.thumbnail(size)  # Resize while maintaining aspect ratio

    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)
    return ContentFile(buffer.read())

# @receiver(post_save, sender=VehicleImages)
def generate_resized_images(sender, instance, created, **kwargs):
    # import pdb; pdb.set_trace()
    if created:
        sizes = {
            'thumbnail': (100, 100),
            'medium': (300, 300),
            'large': (600, 600),
        }

        original_filename = instance.original.name.split('/')[-1].split('.')[0]

        # Thumbnail
        thumb_file = resize_image(instance.original, sizes['thumbnail'])
        instance.thumbnail.save(f"{original_filename}_thumb.jpg", thumb_file, save=False)

        # Medium
        medium_file = resize_image(instance.original, sizes['medium'])
        instance.medium.save(f"{original_filename}_medium.jpg", medium_file, save=False)

        # Large
        large_file = resize_image(instance.original, sizes['large'])
        instance.large.save(f"{original_filename}_large.jpg", large_file, save=False)

        instance.save()
