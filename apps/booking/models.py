from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from apps.mover.models import VehicleType, VehicleMake, VehicleModel, Mover
from apps.customer.models import Customer
from core.models import CommonModel, Comment
from django.contrib.auth import get_user_model
from core.const import DURATION_TYPE_CHOICES, DELIVERY_STATUS
from core.utils import VehicleImageUploadTo, ImageUploadTo
import uuid

User = get_user_model()


class BookingAbs(CommonModel):
    pickup_location = models.JSONField(default=dict)
    dropoff_location = models.JSONField(default=dict)

    booking_time = models.CharField(max_length=10, choices=(("now", "Book Now"), ("later", "Book for Later")), default="now")
    pickup_date = models.DateField(blank=True, null=True)
    pickup_time = models.TimeField(blank=True, null=True)

    booking_type = models.CharField(max_length=15, choices=(("single", "Single Ride"), ("reservation", "Reservation")), default="single")
    duration = models.PositiveIntegerField(blank=True, null=True)
    duration_type = models.CharField(max_length=4, choices=DURATION_TYPE_CHOICES, blank=True, null=True)

    class Meta:
        abstract = True


class RideSearch(BookingAbs):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='ride_searches')
    vehicle_preferences = models.JSONField(default=dict)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True)
    vehicle_make = models.ForeignKey(VehicleMake, on_delete=models.SET_NULL, null=True)
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.SET_NULL, null=True)
    eco_ride = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=(("new_search", "New Search"), ("send_requesat", "Send Request"), ("accepted", "Accepted"), ("confirmed", "Confirmed"), ("rejected", "Rejected")), default="new_search")

    def __str__(self):
        return str(self.id)
    
    @property
    def get_user(self):
        return self.customer.user

    @property
    def pickup_location_title(self):
        title = self.pickup_location['title']
        return title
    
    @property
    def dropoff_location_title(self):
        title = self.dropoff_location['title']
        return title


class RideRequestToMover(models.Model):
    ride_search = models.ForeignKey(RideSearch, on_delete=models.CASCADE)
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    proposed_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    agreed_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    status = models.CharField(max_length=15, choices=(("pending", "Pending Request"), ("accepted", "Accepted"), ("confirmed", "Confirmed"), ("rejected", "Rejected"), ("expired", "Expired")), default="pending")
    comments = GenericRelation(Comment)

    class Meta:
        unique_together = ('ride_search', 'mover')

    def __str__(self):
        return str(self.id)


class Ride(models.Model):
    ride_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_request_mover = models.ForeignKey(RideRequestToMover, on_delete=models.CASCADE)

    status = models.CharField(max_length=15, choices=(("confirmed", "Confirmed"), ("pickedup", "Picked Up"), ("moving", "Moving"), ("dropedoff", "Droped Off"), ("issue", "Issue")))
    rating = models.PositiveSmallIntegerField(default=5)
    bookings = GenericRelation('Booking')

    def __str__(self):
        return str(self.ride_id)

    @property
    def pickup_date(self):
        return "pickup_date"
    
    @property
    def pickup_time(self):
        return "pickup_time"


class ParcelType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Parcel Type"
        verbose_name_plural = "Parcel Types"


class ParcelDelivery(BookingAbs):
    parcel_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parcel_deliveries')
    parcel_type = models.ForeignKey(ParcelType, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=8, decimal_places=2, help_text="Weight of the parcel in kg")
    recipient_contact = models.JSONField(default=dict)
    is_scheduled_delivery = models.BooleanField(default=False)
    delivery_date = models.DateField(blank=True, null=True)
    delivery_time = models.TimeField(blank=True, null=True)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default="waiting")
    special_instructions = models.TextField(max_length=500, blank=True, null=True)
    parcel_image = models.ImageField(upload_to=ImageUploadTo('parcel_image'), blank=True)
    bookings = GenericRelation('Booking')


class Booking(models.Model):
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Generic relation fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey('content_type', 'object_id')

