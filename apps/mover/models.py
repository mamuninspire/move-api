from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.const import FUEL_TYPE, TRANSMISSION_TYPE, SERVICE_STATUS, LICENSE_VERIFICATION_STATUS
from core.models import CommonModel
from core.utils import document_upload_to, VehicleImageUploadTo
import uuid


User = get_user_model()


class VehicleType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=15, blank=True, null=True)
    iconcolor = models.CharField(max_length=20, blank=True, null=True)
    bgcolor = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vehicle Type"
        verbose_name_plural = "Vehicle Types"


class VehicleMake(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vehicle Make"
        verbose_name_plural = "Vehicle Makes"


class VehicleModel(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vehicle Model"
        verbose_name_plural = "Vehicle Models"


class ServiceType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Service Type"
        verbose_name_plural = "Service Types"


class Driver(CommonModel):
    driver_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    mobile = models.CharField(max_length=20, blank=True, null=True)
    is_mobile_verified = models.BooleanField(default=False)

    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    is_whatsapp_verified = models.BooleanField(default=False)

    driving_licence_number = models.CharField(max_length=50, null=False, blank=False, unique=True)
    driving_licence_copy = models.FileField(upload_to="driver/licence", blank=True, null=True)
    is_driving_licence_uploaded = models.BooleanField(default=False)
    driving_licence_verification_status = models.CharField(max_length=15, choices=LICENSE_VERIFICATION_STATUS, default="pending")
    driving_licence_expire_date = models.DateField(blank=True, null=True)

    driver_rating = models.DecimalField(default=0.0, max_digits=2, decimal_places=1, editable=False)
    total_rides = models.PositiveIntegerField(default=0, editable=False)
    total_deliveries = models.PositiveIntegerField(default=0, editable=False)
    

    def save(self, *args, **kwargs):
        print(f"Uploading licence: {self.driving_licence_number}")
        super().save(*args, **kwargs)

    @property
    def name(self):
        return self.user.get_full_name()

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"


class Vehicle(CommonModel):
    license_plate = models.CharField(max_length=20, unique=True, primary_key=True)
    make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE)
    model = models.CharField(max_length=50)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True)

    insurance_number = models.CharField(max_length=100, blank=True, null=True)
    insurance_expiry = models.DateField(blank=True, null=True)
    registration_expiry = models.DateField(blank=True, null=True)
    
    fuel_type = models.CharField(max_length=50, choices=FUEL_TYPE, default="diesel")
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_TYPE, default="manual")
    eco_friendly = models.BooleanField(default=False)

    available_seats = models.PositiveIntegerField(default=1)
    capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Max load capacity in kilograms")

    rate_per_hour = models.DecimalField(max_digits=8, decimal_places=2, help_text="Hourly reservation rate in local currency")
    rate_per_day = models.DecimalField(max_digits=8, decimal_places=2, help_text="Daily reservation rate in local currency")
    rate_per_km = models.DecimalField(max_digits=8, decimal_places=2, help_text="Rate per kilometer in local currency")

    on_board = models.BooleanField(default=False)
    service_status = models.CharField(max_length=20, choices=SERVICE_STATUS, default="available")
    
    is_doc_uploaded = models.BooleanField(default=False)
    is_doc_verified = models.BooleanField(default=False)
    is_images_uploaded = models.BooleanField(default=False)
    is_images_verified = models.BooleanField(default=False)

    description = models.TextField(max_length=250, blank=True, null=True)
    service_types = models.ManyToManyField(ServiceType, related_name="vehicle_service_types")
    

    def __str__(self):
        return f"{self.make.name} {self.model_name} ({self.year})"


class VehicleImages(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='vehicle_images')
    
    image_1 = models.ImageField(upload_to=VehicleImageUploadTo('image_1'))
    image_2 = models.ImageField(upload_to=VehicleImageUploadTo('image_2'),  blank=True)
    image_3 = models.ImageField(upload_to=VehicleImageUploadTo('image_3'),  blank=True)
    image_4 = models.ImageField(upload_to=VehicleImageUploadTo('image_4'),  blank=True)

    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Images for Vehicle {self.vehicle.id}"


class DocumentType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Document Type"
        verbose_name_plural = "Document Types"


class Documents(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='driver_documents')
    doc = models.FileField(upload_to=document_upload_to, blank=True, null=True)
    doc_type = models.ForeignKey(DocumentType, blank=True, null=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Documents for Vehicle {self.vehicle.id}"


class Mover(models.Model):
    mover_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.OneToOneField(Driver, on_delete=models.CASCADE)
    vechicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)
    is_rider = models.BooleanField(default=True)
    is_parcel_delivery = models.BooleanField(default=False)
    is_plant_hire = models.BooleanField(default=False)
    service_area = models.JSONField(default=dict)
    current_location = models.JSONField(default=dict)

