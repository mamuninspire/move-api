from rest_framework import viewsets, status
# from rest_framework.views import APIView
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
    MoverSerializer, MoverSearchSerializer, MoverProfileSerializer
)
from core.utils import get_distance_duration
from decimal import Decimal
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
    
    @action(detail=False, methods=["get"], url_path="metadata")
    def metadata(self, request):
        return Response({
            "vehicle_types": VehicleTypeSerializer(VehicleType.objects.all(), many=True).data,
            "vehicle_makes": VehicleMakeSerializer(VehicleMake.objects.all(), many=True).data,
            "vehicle_models": VehicleModelSerializer(VehicleModel.objects.all(), many=True).data,
        })
    
    @action(detail=False, methods=['get'], url_path='my')
    def my_vehicle(self, request):
        try:
            mover = Mover.objects.get(user=request.user)
        except Mover.DoesNotExist:
            return Response({"detail": "You are not a registered mover."}, status=404)

        if not mover.vehicle:
            return Response({"detail": "No vehicle assigned to your profile."}, status=404)

        serializer = self.get_serializer(mover.vehicle)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        # Extract data from request
        if request.user.mover.vehicle:
            return Response({"message": "Vehicle alread added. You can only add one vehicle"})
        
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
            data['vehicle_type'] = VehicleType.objects.get(name__icontains="other").id
            # errors['vehicle_type'] = "Invalid vehicle type"

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
        mover.vehicle = vehicle
        mover.is_vehicle_added = True

        if 'ride' in service_type_names:
            mover.is_rider = True
        if 'plant_hire' in service_type_names:
            mover.is_plant_hire = True
        if 'delivery' in service_type_names:
            mover.is_parcel_delivery = True

        mover.save()

        return Response(VehicleSerializer(vehicle).data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        try:
            mover = Mover.objects.get(user=request.user)
        except Mover.DoesNotExist:
            return Response({"detail": "You are not a registered mover."}, status=404)

        if not mover.vehicle:
            return Response({"detail": "No vehicle assigned to your profile to update."}, status=404)

        vehicle = mover.vehicle

        data = request.data.copy()
        errors = {}

        if 'make' in data:
            try:
                data['make'] = VehicleMake.objects.get(name=data['make']).id
            except VehicleMake.DoesNotExist:
                errors['make'] = "Invalid make"

        if 'vehicle_type' in data:
            try:
                data['vehicle_type'] = VehicleType.objects.get(name=data['vehicle_type']).id
            except VehicleType.DoesNotExist:
                errors['vehicle_type'] = "Invalid vehicle type"

        if 'body_style' in data:
            try:
                data['body_style'] = VehicleBodyStyle.objects.get(name=data['body_style']).id
            except VehicleBodyStyle.DoesNotExist:
                errors['body_style'] = "Invalid body style"

        if errors:
            return Response({"errors": errors}, status=400)

        if 'service_types' in data:
            service_types = ServiceType.objects.filter(name__in=data['service_types'])
            if not service_types:
                return Response({"service_types": "At least one valid service type is required."}, status=400)
            else:
                ids = list(service_types.values_list('id', flat=True))
                data['service_types'] = ids

        serializer = self.get_serializer(vehicle, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_vehicle = serializer.save()

        if 'service_types' in data:
            updated_vehicle.service_types.set(data['service_types'])

        return Response(VehicleSerializer(updated_vehicle).data, status=200)
        
    def destroy(self, request, *args, **kwargs):
        try:
            mover = Mover.objects.get(user=request.user)
        except Mover.DoesNotExist:
            return Response({"detail": "You are not a registered mover."}, status=404)

        vehicle_id = self.kwargs.get('pk')
        if str(mover.vehicle.id) != str(vehicle_id):
            return Response({"detail": "You are not allowed to delete this vehicle."}, status=403)

        vehicle = mover.vehicle

        mover.vehicle = None
        mover.is_vehicle_added = False
        mover.save()

        vehicle.delete()

        return Response({"detail": "Vehicle deleted successfully."}, status=204)


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

    def retrieve(self, request, *args, **kwargs):
        mover_id = self.kwargs.get('pk')

        try:
            mover = Mover.objects.get(mover_id=mover_id)
        except Mover.DoesNotExist:
            return Response({"detail": "Mover not found."}, status=404)

        serializer = MoverProfileSerializer(mover)

        # You could add extra custom data if needed
        data = serializer.data
        # data['extra_info'] = "Some extra data if you like"

        return Response(data)

    def update(self, request, *args, **kwargs):
        mover_id = self.kwargs.get('pk')

        try:
            mover = Mover.objects.get(pk=mover_id)
        except Mover.DoesNotExist:
            return Response({"detail": "Mover not found."}, status=404)

        # Example: Allow users to update only their own mover profile
        if mover.user != request.user:
            return Response({"detail": "You do not have permission to update this mover."}, status=403)

        serializer = self.get_serializer(mover, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=200)



    @action(detail=False, methods=['post'], url_path='search-available-rides')
    def search_available_rides(self, request):
        """
        POST /api/v1/movers/search-available-rides/
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
            "booking_time": "book_now",
            "pickup_date": "2025-06-25",
            "pickup_time": "15:30",
            "booking_type": "Reservation",
            "eco_friendly": "false",
            "vehicle_preferences": {
                "vehicle_type": "Van",
                "vehicle_make": "Toyota",
                "vehicle_model": "Hiace"
            }
        }
        """
        # pdb.set_trace()
        data = request.data

        # Step 1: Filter Mover based on is_online and service_type
        movers = Mover.objects.filter(is_online=True, is_rider=True).select_related("vehicle")

        # Step 2: Apply vehicle filters
        
        # b 
        
        # Step 3: Sort by distance, rate and rating
        if movers:
            # Calculate distance and duration 
            pickup = data.get("pickup_location")
            dropoff = data.get("dropoff_location")
            booking_type = data.get("booking_type")

            
            try:
                
                search_results = []
                for driver in movers:
                    search_data = {}
                    search_data['mover_id'] = driver.mover_id
                    search_data['driver_name'] = driver.user.get_full_name()
                    search_data['rating'] = driver.rating
                    search_data['phone'] = driver.get_contact
                    search_data['license'] = driver.driving_licence_number
                    search_data['make'] = driver.get_vehicle_make.name
                    search_data['model'] = driver.get_vehicle_model
                    search_data['capacity'] = driver.capacity
                    search_data['available'] = driver.available
                    search_data['image'] = driver.vehicle.get_hero_image_url()

                    if booking_type == "reservation":
                        duration_type = data.get("duration_type") if data.get("duration_type") else None
                        # duration = data.get("duration") if data.get("duration") else 1

                        if duration_type == "DAY":
                            est = driver.vehicle.rate_per_day
                            search_data['estimated_cost'] = est
                        else:
                            est = driver.vehicle.rate_per_hour
                            search_data['estimated_cost'] = est

                    elif booking_type == "single":
                        api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
                        result = get_distance_duration(pickup, dropoff, api_key)
                        print(result)
                        distance = result['distance_meters']/1000
                        search_data['estimated_cost'] = round(driver.vehicle.rate_per_km * Decimal(str(distance)), 2)
                    else:
                        search_data['estimated_cost'] = 100
                    
                    search_data['duration_type'] = duration_type

                    search_results.append(search_data)
                    

            except Exception as e:
                print(e)

            # movers = movers.order_by('rating')
            # pdb.set_trace()
        

        # Step 3: Optional pickup time validation
        booking_time = data.get("booking_time")
        pickup_date = data.get("pickup_date")
        pickup_time = data.get("pickup_time")

        serializer = self.get_serializer(movers, many=True)
        return Response(search_results, status=status.HTTP_200_OK)