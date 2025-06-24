from django.utils.deconstruct import deconstructible
from django.core.files.storage import default_storage

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