from rest_framework import viewsets
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from .models import Customer
from .serializers import CustomerSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        customer_id = self.kwargs.get('pk')

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check: only owner can retrieve
        if customer.user != request.user:
            return Response({"detail": "You do not have permission to view this customer."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats', permission_classes=[AllowAny])
    def stats(self, request):
        data = {
            "status": "Success"
        }
        return Response(data, status=status.HTTP_200_OK)
