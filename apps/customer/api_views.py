from rest_framework import viewsets
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from .models import Customer
from .serializers import CustomerSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=False, methods=['get'], url_path='stats', permission_classes=[AllowAny])
    def stats(self, request):
        data = {
            "status": "Success"
        }
        return Response(data, status=status.HTTP_200_OK)
