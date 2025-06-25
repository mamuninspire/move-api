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


class VehicleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'


class VehicleImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImages
        fields = ['image_1', 'image_2', 'image_3', 'image_4', 'uploaded_at']




class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'name']


class DocumentsSerializer(serializers.ModelSerializer):
    doc_type = DocumentTypeSerializer()  # nested doc_type info

    class Meta:
        model = Documents
        fields = ['id', 'doc', 'doc_type', 'uploaded_at']


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


class VehicleSerializer(serializers.ModelSerializer):
    make = VehicleMakeSerializer()
    vehicle_type = VehicleTypeSerializer()
    body_style = VehicleBodyStyleSerializer()
    service_types = ServiceTypeSerializer(many=True)
    vehicle_images = VehicleImagesSerializer(read_only=True)
    driver_documents = DocumentsSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'

        
class MoverSearchSerializer(serializers.ModelSerializer):
    vehicle = VehicleSummarySerializer(read_only=True)
    class Meta:
        model = Mover
        fields = '__all__'