from rest_framework import serializers
from .models import (
    VehicleType, VehicleMake, VehicleModel, VehicleBodyStyle, 
    ServiceType, Vehicle, VehicleImages, 
    DocumentType, Documents, Mover
)
from django.contrib.auth import get_user_model

User = get_user_model()


class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'


class VehicleMakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMake
        fields = '__all__'


class VehicleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleModel
        fields = '__all__'


class VehicleBodyStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleBodyStyle
        fields = '__all__'


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    make = VehicleMakeSerializer()
    vehicle_type = VehicleTypeSerializer()
    body_style = VehicleBodyStyleSerializer()
    service_types = ServiceTypeSerializer(many=True)

    class Meta:
        model = Vehicle
        fields = '__all__'


class VehicleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'


class VehicleImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImages
        fields = '__all__'


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = '__all__'


class DocumentsSerializer(serializers.ModelSerializer):
    doc_type = DocumentTypeSerializer()

    class Meta:
        model = Documents
        fields = '__all__'


class DocumentsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = '__all__'


class MoverSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Mover
        fields = '__all__'


class VehicleSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['license_plate', 'make', 'model', 'year', 'color']


class MoverSearchSerializer(serializers.ModelSerializer):
    vehicle = VehicleSummarySerializer(read_only=True)
    class Meta:
        model = Mover
        fields = '__all__'