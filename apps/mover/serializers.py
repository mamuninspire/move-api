from rest_framework import serializers
from .models import (
    Driver, Vehicle, Mover, VehicleImages, DocumentType,
    Documents, VehicleType, VehicleMake, VehicleModel, ServiceType
)
from django.contrib.auth import get_user_model

User = get_user_model()


class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ['id', 'name', 'icon', 'iconcolor', 'bgcolor']


class VehicleMakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMake
        fields = ['id', 'name']


class VehicleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleModel
        fields = ['id', 'name']


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ['id', 'name']


class DriverSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Driver
        fields = [
            'driver_id', 'user', 'name', 'mobile', 'is_mobile_verified',
            'whatsapp', 'is_whatsapp_verified', 'driving_licence_number',
            'driving_licence_copy', 'is_driving_licence_uploaded',
            'driving_licence_verification_status', 'driving_licence_expire_date',
            'driver_rating', 'total_rides', 'total_deliveries'
        ]


class VehicleSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)
    make = VehicleMakeSerializer(read_only=True)
    vehicle_type = VehicleTypeSerializer(read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'


class VehicleImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImages
        fields = [
            'vehicle', 'image_1', 'image_2', 'image_3', 'image_4', 'uploaded_at'
        ]


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'name']


class DocumentsSerializer(serializers.ModelSerializer):
    doc_type = DocumentTypeSerializer(read_only=True)

    class Meta:
        model = Documents
        fields = ['id', 'vehicle', 'doc', 'doc_type', 'uploaded_at']


class MoverSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)

    class Meta:
        model = Mover
        fields = [
            'mover_id', 'driver', 'is_online', 'is_available',
            'is_rider', 'is_parcel_delivery', 'is_cargo_delivery',
            'service_area', 'current_location'
        ]
