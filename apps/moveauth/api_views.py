from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework import status
from .serializers import UserSerializer, UserRegistrationSerializer
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from apps.mover.models import Mover, Driver
from apps.customer.models import Customer

User = get_user_model()

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'], url_path='signup', permission_classes=[AllowAny])
    def signup(self, request):
        # import pdb; pdb.set_trace()
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user.account_type == "CUSTOMER":
                user.is_customer = True
            elif user.account_type == "MOVER":
                user.is_mover = True
            
            # Add user to their respective group
            try:
                group = Group.objects.get(name=user.account_type.capitalize())  # "Customer" or "Mover"
                user.groups.add(group)
            except Group.DoesNotExist:
                group_name = user.account_type.capitalize()
                group = Group.objects.create(name=group_name)
                user.groups.add(group)
            
            user.save()

            # Create user respective profile Mover/Customer
            try:
                if user.account_type == "MOVER":
                    driver = Driver.objects.create(user=user)
                    Mover.objects.create(driver=driver)
                elif user.account_type == "CUSTOMER":
                    Customer.objects.create(user=user)
            except Exception as e:
                print(e)

            response_data = {
                'status': 'success',
                'data': self.get_serializer(user).data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
