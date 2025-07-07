from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from .models import RideSearch, RideRequestToMover, Ride, ParcelDelivery, ParcelType, Booking
from .serializers import (
    RideSearchSerializer,
    RideRequestToMoverSerializer,
    RideSerializer,
    ParcelDeliverySerializer,
    ParcelTypeSerializer,
    BookingSerializer
)
from apps.mover.models import Mover, VehicleType, VehicleModel, VehicleMake
from apps.customer.models import Customer
from core.utils import get_distance_duration
from dotenv import load_dotenv
import os
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()
import pdb


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # default page size
    page_size_query_param = 'page_size'
    max_page_size = 100


class RideSearchViewSet(viewsets.ModelViewSet):
    queryset = RideSearch.objects.all()
    serializer_class = RideSearchSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    def get_queryset(self):
        # pdb.set_trace()
        # Optionally filter by user or mover, assuming relationships exist
        user = self.request.user
        role = user.role
        if role == 'CUSTOMER':
            customer = Customer.objects.get(user=user)
            return RideSearch.objects.filter(customer=customer)
        else:
            return Response({"message": "Wrong request"})
        

    def perform_create(self, serializer):
        customer = getattr(self.request.user, 'customer_profile', None)
        if not customer:
            raise PermissionDenied("You must have a customer profile to create a ride search.")
        serializer.save(customer=customer)

    def create(self, request, *args, **kwargs):
        data = request.data
        print(f"===== data=====")
        print(data)
        
        if data.get("booking_time") == 'now':
            data.pop("pickup_date")
            data.pop("pickup_time")
        
        booking_type = data.get('booking_type')
        if booking_type == 'single':
            duration_type = data.pop("duration_type")
            duration = data.pop("duration")
        else:
            duration_type = data.get('duration_type')
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        ride_search_id = serializer.data.get('id')
        pickup = data.get("pickup_location")
        dropoff = data.get("dropoff_location")
        distance_result = get_distance_duration(pickup, dropoff, self.api_key)
        # pdb.set_trace()

        movers = Mover.objects.filter(is_online=True, is_rider=True).select_related("vehicle", "user")

        vehicle_type = data.get("vehicle_type")
        vehicle_make = data.get("make")
        vehicle_model = data.get("model")

        if vehicle_type:
            vt = VehicleType.objects.filter(name__icontains=vehicle_type).first()
            movers = movers.filter(vehicle__vehicle_type=vt)
        
        if vehicle_make:
            vm = VehicleMake.objects.filter(name__icontains=vehicle_make).first()
            movers = movers.filter(vehicle__make=vm)
        
        if vehicle_model:
            vmd = VehicleModel.objects.filter(name__icontains=vehicle_model).first()
            movers = movers.filter(vehicle__model=vmd)

        search_results = []
        def process_driver(driver):
            """Process single driver and return data dict"""
            driver_data = {
                'ride_search_id': ride_search_id,
                'mover_id': driver.mover_id,
                'driver_name': driver.user.get_full_name(),
                'rating': driver.rating,
                'phone': driver.get_contact,
                'license': driver.driving_licence_number,
                'make': driver.get_vehicle_make,
                'model': driver.get_vehicle_model,
                'color': driver.get_vehicle_color,
                "vehicle_type": driver.get_vehicle_type,
                'capacity': driver.capacity,
                'available': driver.available,
                'image': driver.vehicle.get_hero_image_url() if driver.vehicle else None,
                'duration_type': duration_type,
                'estimated_cost': None
            }

            # Estimate cost
            if booking_type == "reservation" and driver.vehicle:
                driver_data['estimated_cost'] = (
                    driver.vehicle.rate_per_day if duration_type == "DAY"
                    else driver.vehicle.rate_per_hour
                )

            elif booking_type == "single" and driver.vehicle:
                if distance_result:
                    distance_km = distance_result.get('distance_meters', 0) / 1000
                    driver_data['estimated_cost'] = round(
                        driver.vehicle.rate_per_km * Decimal(str(distance_km)), 2
                    )
                else:
                    driver_data['estimated_cost'] = None

            return driver_data
        
        try:
            if booking_type == "single":
                # Use ThreadPoolExecutor to parallelize API calls
                with ThreadPoolExecutor(max_workers=8) as executor:
                    futures = [executor.submit(process_driver, driver) for driver in movers]
                    for future in as_completed(futures):
                        try:
                            search_results.append(future.result())
                        except Exception as e:
                            print(f"Error processing driver: {e}")
            else:
                # reservation booking: no external API, safe to do sequentially
                for driver in movers:
                    try:
                        driver_data = process_driver(driver)
                        search_results.append(driver_data)
                    except Exception as e:
                        print(f"Error processing driver: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")
            
        page = self.paginate_queryset(search_results)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(search_results, status=status.HTTP_200_OK)


class RideRequestToMoverViewSet(viewsets.ModelViewSet):
    queryset = RideRequestToMover.objects.all()
    serializer_class = RideRequestToMoverSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # pdb.set_trace()
        # Optionally filter by user or mover, assuming relationships exist
        user = self.request.user
        role = user.role
        if role == 'CUSTOMER':
            customer = Customer.objects.get(user=user)
            return RideRequestToMover.objects.filter(ride_search__customer=customer)
        elif role == 'MOVER':
            mover = Mover.objects.get(user=user)
            return RideRequestToMover.objects.filter(mover=mover)
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=False, methods=['patch'], url_path='accept')
    def accept_ride_request(self, request):
        # pdb.set_trace()
        data = self.request.data
        id = data.get('booking_request_id')

        try:
            ride_request = RideRequestToMover.objects.get(id=id)
            ride_request.status = 'accepted'
            ride_request.save()

            ride_search = ride_request.ride_search
            ride_search.status = 'accepted'
            ride_search.save()

        except RideRequestToMover.DoesNotExist:
            return Response({"detail": "You are not a registered mover."}, status=404)

        return Response({"status": status.HTTP_202_ACCEPTED})
    
    @action(detail=False, methods=['patch'], url_path='confirm')
    def confirm_ride_request(self, request):
        # pdb.set_trace()
        data = self.request.data
        id = data.get('booking_request_id')

        try:
            ride_request = RideRequestToMover.objects.get(id=id)
            ride_request.status = 'confirmed'
            ride_request.agreed_price = ride_request.proposed_price
            ride_request.save()

            ride_search = ride_request.ride_search
            ride_search.status = 'confirmed'
            ride_search.save()

            Ride.objects.create(
                booking_request_mover=ride_request,
                status='confirmed'
            )

            stall_requests = RideRequestToMover.objects.filter(ride_search=ride_search)
            for req in stall_requests:
                if req.id != id:
                    req.status = 'expired'
                    req.save()


            
        except RideRequestToMover.DoesNotExist:
            return Response({"detail": "You are not a registered mover."}, status=404)

        return Response({"status": status.HTTP_202_ACCEPTED})
        

class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.select_related(
        'booking_request_mover__ride_search',
        'booking_request_mover__mover__user',  # Assuming Mover has OneToOneField to User
        'booking_request_mover__ride_search__vehicle_type',
        'booking_request_mover__ride_search__vehicle_make',
        'booking_request_mover__ride_search__vehicle_model',
    )
    
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # pdb.set_trace()
        # Assuming you want to restrict based on user
        if not self.request.user or not self.request.user.is_authenticated:
            raise NotAuthenticated("Authentication required to access this endpoint.")
        
        rides = Ride.objects.filter(
            booking_request_mover__ride_search__customer__user=self.request.user
        )

        return rides
        # return RideBooking.objects.filter(booking_request_mover__ride_search__user=self.request.user)


class ParcelTypeViewSet(viewsets.ModelViewSet):
    queryset = ParcelType.objects.all()
    serializer_class = ParcelTypeSerializer
    permission_classes = [IsAuthenticated]


class ParcelDeliveryViewSet(viewsets.ModelViewSet):
    queryset = ParcelDelivery.objects.all()
    serializer_class = ParcelDeliverySerializer
    permission_classes = [IsAuthenticated]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='recent', permission_classes=[AllowAny])
    def most_recent(self, request):
        bookings = Booking.objects.all()[:10]  # Optional: limit to recent 10
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
