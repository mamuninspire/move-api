from django.contrib import admin
from .models import (
    VehicleType, VehicleMake, ServiceType, VehicleModel,
    Driver, Vehicle, VehicleImages, DocumentType, Documents, Mover
)


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'iconcolor', 'bgcolor')
    search_fields = ('name',)


@admin.register(VehicleMake)
class VehicleMakeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        'driver_id', 'user', 'mobile', 'is_mobile_verified',
        'driving_licence_number', 'driving_licence_verification_status',
        'driver_rating', 'total_rides', 'total_deliveries'
    )
    list_filter = (
        'is_mobile_verified', 'is_whatsapp_verified',
        'driving_licence_verification_status'
    )
    search_fields = ('user__email', 'mobile', 'driving_licence_number')
    readonly_fields = ('driver_rating', 'total_rides', 'total_deliveries')
    ordering = ('-driver_rating',)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        'license_plate', 'make', 'model', 'year', 'vehicle_type',
        'fuel_type', 'transmission', 'eco_friendly', 'on_board', 'service_status',
        'rate_per_hour', 'rate_per_day', 'rate_per_km'
    )
    list_filter = ('vehicle_type', 'fuel_type', 'transmission', 'eco_friendly', 'service_status')
    search_fields = ('license_plate', 'make__name', 'model')
    readonly_fields = ('license_plate',)
    autocomplete_fields = ('make', 'vehicle_type')


@admin.register(Mover)
class MoverAdmin(admin.ModelAdmin):
    list_display = (
        'mover_id', 'driver', 'is_online', 'is_available',
        'is_rider', 'is_parcel_delivery', 'is_cargo_delivery'
    )
    list_filter = ('is_online', 'is_available', 'is_rider', 'is_parcel_delivery', 'is_cargo_delivery')
    search_fields = ('driver__user__email',)


@admin.register(VehicleImages)
class VehicleImagesAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
    search_fields = ('vehicle__license_plate',)


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'doc_type', 'uploaded_at')
    search_fields = ('vehicle__license_plate', 'doc_type__name')
    autocomplete_fields = ('vehicle', 'doc_type')
