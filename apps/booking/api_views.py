from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from .models import RideSearch, RideRequestToMover, Ride, ParcelDelivery, ParcelType, Booking
from .serializers import (
    RideSearchSerializer,
    RideRequestToMoverSerializer,
    RideSerializer,
    ParcelDeliverySerializer,
    ParcelTypeSerializer,
    BookingSerializer
)


class RideSearchViewSet(viewsets.ModelViewSet):
    queryset = RideSearch.objects.all()
    serializer_class = RideSearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return RideSearch.objects.filter(user=self.request.user)


class RideRequestToMoverViewSet(viewsets.ModelViewSet):
    queryset = RideRequestToMover.objects.all()
    serializer_class = RideRequestToMoverSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optionally filter by user or mover, assuming relationships exist
        user = self.request.user
        return RideRequestToMover.objects.filter(ride_search__user=user)
    
    @action(detail=False, methods=['post'], url_path='send-ride-request', permission_classes=[AllowAny])
    def send_request(self, request):
        data = {"message": "Success"}
        return Response(data, status=status.HTTP_200_OK)
        


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]

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

class ParcelDeliveryViewSet(viewsets.ModelViewSet):
    queryset = ParcelDelivery.objects.all()
    serializer_class = ParcelDeliverySerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    @action(detail=False, methods=['get'], url_path='recent', permission_classes=[AllowAny])
    def most_recent(self, request):
        bookings = Booking.objects.all()[:10]  # Optional: limit to recent 10
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
