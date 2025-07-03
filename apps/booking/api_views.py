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
from apps.mover.models import Mover
from apps.customer.models import Customer
from core.utils import get_distance_duration

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        ride_search_id = serializer.data.get('id')
        booking_type = request.data.get('booking_type')
        duration_type = request.data.get('duration_type')
        pickup = request.data.get("pickup_location")
        dropoff = request.data.get("dropoff_location")

        movers = Mover.objects.filter(is_online=True, is_rider=True).select_related("vehicle")

        search_results = []
        for driver in movers:
            driver_data = {
                'ride_search_id': ride_search_id,
                'mover_id': driver.mover_id,
                'driver_name': driver.user.get_full_name(),
                'rating': driver.rating,
                'phone': driver.get_contact,
                'license': driver.driving_licence_number,
                'make': driver.get_vehicle_make.name if driver.get_vehicle_make else None,
                'model': driver.get_vehicle_model,
                'capacity': driver.capacity,
                'available': driver.available,
                'image': driver.vehicle.get_hero_image_url() if driver.vehicle else None,
                'duration_type': duration_type
            }

            # Calculate estimated cost
            if booking_type == "reservation" and driver.vehicle:
                if duration_type == "DAY":
                    driver_data['estimated_cost'] = driver.vehicle.rate_per_day
                else:
                    driver_data['estimated_cost'] = driver.vehicle.rate_per_hour
            elif booking_type == "single" and driver.vehicle:
                api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
                distance_result = get_distance_duration(pickup, dropoff, api_key)
                if distance_result:
                    distance_km = distance_result.get('distance_meters', 0) / 1000
                    driver_data['estimated_cost'] = round(
                        driver.vehicle.rate_per_km * Decimal(str(distance_km)), 2
                    )
                else:
                    driver_data['estimated_cost'] = None
            else:
                driver_data['estimated_cost'] = None

            search_results.append(driver_data)

        # Paginate the list
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
        

class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Assuming you want to restrict based on user
        if not self.request.user or not self.request.user.is_authenticated:
            raise NotAuthenticated("Authentication required to access this endpoint.")

        return Ride.objects.filter(
            booking_request_mover__ride_search__user=self.request.user
        )
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
