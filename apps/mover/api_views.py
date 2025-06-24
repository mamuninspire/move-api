from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from .models import (
    Driver, Vehicle, Mover, VehicleImages, DocumentType,
    Documents, VehicleType, VehicleMake, VehicleModel, ServiceType
)
from .serializers import (
    DriverSerializer, VehicleSerializer, MoverSerializer,
    VehicleImagesSerializer, DocumentTypeSerializer,
    DocumentsSerializer, VehicleTypeSerializer,
    VehicleMakeSerializer, VehicleModelSerializer, ServiceTypeSerializer
)


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


class MoverViewSet(viewsets.ModelViewSet):
    queryset = Mover.objects.all()
    serializer_class = MoverSerializer

    @action(detail=False, methods=['post'], url_path='search-available-rides', permission_classes=[AllowAny])
    def search_available_rides(self, request):
        """
        Custom POST action to filter movers based on input criteria.
        Example body:
        {
            "location": "Doha",
            "date": "2025-06-20"
        }
        """
        
        location = request.data.get('location')
        date = request.data.get('date')

        movers = Mover.objects.all()

        # if location:
        #     movers = movers.filter(address__icontains=location)  # Adjust field name if needed
        # if date:
        #     movers = movers.filter(available_date=date)  # Adjust field name if needed

        serializer = self.get_serializer(movers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VehicleImagesViewSet(viewsets.ModelViewSet):
    queryset = VehicleImages.objects.all()
    serializer_class = VehicleImagesSerializer


class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer


class DocumentsViewSet(viewsets.ModelViewSet):
    queryset = Documents.objects.all()
    serializer_class = DocumentsSerializer


class VehicleTypeViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer


class VehicleMakeViewSet(viewsets.ModelViewSet):
    queryset = VehicleMake.objects.all()
    serializer_class = VehicleMakeSerializer


class VehicleModelViewSet(viewsets.ModelViewSet):
    queryset = VehicleModel.objects.all()
    serializer_class = VehicleModelSerializer


class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
