from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.dateparse import parse_date, parse_time
from .models import (
    VehicleType, VehicleMake, VehicleModel, VehicleBodyStyle, 
    ServiceType, Vehicle, VehicleImages, 
    DocumentType, Documents, Mover
)
from .serializers import (
    VehicleTypeSerializer, VehicleMakeSerializer, VehicleModelSerializer,
    VehicleBodyStyleSerializer, ServiceTypeSerializer,
    VehicleSerializer, VehicleWriteSerializer,
    VehicleImagesSerializer, DocumentTypeSerializer,
    DocumentsSerializer, DocumentsWriteSerializer,
    MoverSerializer, MoverSearchSerializer
)
from core.utils import get_distance_duration
import asyncio
import os
import pdb; 


class VehicleTypeViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer


class VehicleMakeViewSet(viewsets.ModelViewSet):
    queryset = VehicleMake.objects.all()
    serializer_class = VehicleMakeSerializer


class VehicleModelViewSet(viewsets.ModelViewSet):
    queryset = VehicleModel.objects.all()
    serializer_class = VehicleModelSerializer


class VehicleBodyStyleViewSet(viewsets.ModelViewSet):
    queryset = VehicleBodyStyle.objects.all()
    serializer_class = VehicleBodyStyleSerializer


class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    permission_classes = [IsAuthenticated] 

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return VehicleWriteSerializer
        return VehicleSerializer
    
    def create(self, request, *args, **kwargs):
        # pdb.set_trace()
        # Extract data from request
        data = request.data.copy()
        errors = {}

        # Resolve and assign foreign keys
        try:
            data['make'] = VehicleMake.objects.get(name=request.data.get('make')).id
        except VehicleMake.DoesNotExist:
            errors['make'] = "Invalid make"

        try:
            data['vehicle_type'] = VehicleType.objects.get(name=request.data.get('vehicle_type')).id
        except VehicleType.DoesNotExist:
            errors['vehicle_type'] = "Invalid vehicle type"

        body_style_name = request.data.get('body_style')
        if body_style_name:
            try:
                data['body_style'] = VehicleBodyStyle.objects.get(name=body_style_name).id
            except VehicleBodyStyle.DoesNotExist:
                errors['body_style'] = "Invalid body style"

        # Validate early if FK issues exist
        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        # Handle service_types (ManyToMany)
        service_type_names = request.data.get('service_types')
        service_types = ServiceType.objects.filter(name__in=service_type_names)
        
        if not service_types:
            return Response({"service_types": "At least one valid service type is required."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            ids = list(service_types.values_list('id', flat=True))
            data['service_types'] = ids

        # Validate and create Vehicle
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.save()
        vehicle.service_types.set(ids)
        vehicle.save()

        #  Assign vehicle to mover
        mover = Mover.objects.get(user=request.user)
        mover.vechicle = vehicle
        mover.is_vehicle_added = True
        mover.save()

        return Response(VehicleSerializer(vehicle).data, status=status.HTTP_201_CREATED)


class VehicleImagesViewSet(viewsets.ModelViewSet):
    queryset = VehicleImages.objects.all()
    serializer_class = VehicleImagesSerializer


class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer


class DocumentsViewSet(viewsets.ModelViewSet):
    queryset = Documents.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DocumentsWriteSerializer
        return DocumentsSerializer


class MoverViewSet(viewsets.ModelViewSet):
    queryset = Mover.objects.all()
    serializer_class = MoverSearchSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='search-available-rides')
    def search_available_rides(self, request):
        """
        POST /api/movers/search-available-rides/
        {
            "pickup_location": {
                "title": "DohaInspire Management Training Centre",
                "lat": 25.259938730956645,
                "lang": 51.53741897748352 
            },
            "dropoff_location": {
                "title": "Doha Jadeed Buildings 1 and 3 - QR Crew Accommodation",
                "lat": 25.278579420428017,
                "lang": 51.53200106872503
            },
            "booking_time": "now",
            "pickup_date": "2025-06-25",
            "pickup_time": "15:30",
            "booking_type": "Reservation",
            "vehicle_preferences": {
                "vehicle_type": "Van",
                "vehicle_make": "Toyota",
                "vehicle_model": "Hiace"
            }
        }
        """
        # pdb.set_trace()
        data = request.data

        service_name = data.get("service_type")

        # Step 1: Filter Mover based on is_online and service_type
        movers = Mover.objects.filter(is_online=True, vehicle__service_types__name__iexact=service_name).select_related("vehicle")

        # Step 2: Apply vehicle filters
        vehicle_prefs = data.get("vehicle_preferences", {})
        vehicle_type = vehicle_prefs.get("vehicle_type")
        vehicle_make = vehicle_prefs.get("vehicle_make")
        vehicle_model = vehicle_prefs.get("vehicle_model")

        if movers:
            if vehicle_type:
                movers = movers.filter(vehicle__vehicle_type__name__iexact=vehicle_type)

            if vehicle_make:
                movers = movers.filter(vehicle__make__name__iexact=vehicle_make)

            if vehicle_model:
                movers = movers.filter(vehicle__model__iexact=vehicle_model)
        
        # Step 3: Sort by distance, rate and rating
        if movers:
            # Calculate distance and duration 
            pickup = data.get("pickup_location")
            dropoff = data.get("dropoff_location")
            booking_type = data.get("booking_type")

            api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
            try:
                result = get_distance_duration(pickup, dropoff, api_key)
                distance = result['distance_meters']//1000
                search_results = []
                for driver in movers:
                    search_data = {}
                    search_data['driver_name'] = driver.user.get_full_name()
                    search_data['rating'] = driver.rating
                    search_data['phone'] = driver.get_contact
                    search_data['license'] = driver.driving_licence_number
                    search_data['make'] = driver.get_vehicle_make.name
                    search_data['model'] = driver.get_vehicle_model
                    search_data['capacity'] = driver.capacity
                    search_data['available'] = driver.available
                    search_data['image'] = driver.vehicle.get_hero_image_url()

                    search_data['estimated_cost'] = driver.vehicle.rate_per_km * distance
                    search_results.append(search_data)
                    

            except Exception as e:
                print(e)

            movers = movers.order_by('rating')

        # Step 3: Optional pickup time validation
        booking_time = data.get("booking_time")
        pickup_date = data.get("pickup_date")
        pickup_time = data.get("pickup_time")

        serializer = self.get_serializer(movers, many=True)
        return Response(search_results, status=status.HTTP_200_OK)