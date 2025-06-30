from django.contrib import admin
from .models import RideSearch, RideRequestToMover, Ride, Booking, ParcelDelivery, ParcelType


@admin.register(RideSearch)
class RideSearchAdmin(admin.ModelAdmin):
    list_display = ('customer', 'pickup_location', 'dropoff_location', 'eco_ride')
    list_filter = ('booking_time', 'booking_type', 'eco_ride', 'vehicle_type')
    search_fields = ('customer__user__email', 'vehicle_type__name', 'vehicle_make__name', 'vehicle_model__name')


@admin.register(RideRequestToMover)
class RideRequestToMoverAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'ride_search', 'mover', 'estimated_cost',
        'proposed_price', 'agreed_price', 'status'
    )
    list_filter = ('status',)
    search_fields = ('ride_search__customer__user__email', 'mover__driver__user__email')


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = (
        'ride_id', 'booking_request_mover', 'status', 'pickup_date',
        'pickup_time', 'rating'
    )
    list_filter = ('status',)
    search_fields = ('booking_request_mover__ride_search__user__email', 'ride_id')


@admin.register(ParcelType)
class ParcelTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(ParcelDelivery)
class ParcelDeliveryAdmin(admin.ModelAdmin):
    list_display = ('parcel_id', 'user', 'parcel_type', 'delivery_status')
    search_fields = ('user__email',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'content_type', 'object_id')
