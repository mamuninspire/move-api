from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework import status
from .serializers import UserSerializer, UserRegistrationSerializer, CustomTokenObtainPairSerializer
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from apps.mover.models import Mover
from apps.customer.models import Customer
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'], url_path='signup', permission_classes=[AllowAny])
    def signup(self, request):
        data= request.data
        serializer = UserRegistrationSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            if user.role == "CUSTOMER":
                user.is_customer = True
            elif user.role == "MOVER":
                user.is_mover = True
            
            # Add user to their respective group
            try:
                group = Group.objects.get(name=user.role.capitalize())  # "Customer" or "Mover"
                user.groups.add(group)
            except Group.DoesNotExist:
                group_name = user.role.capitalize()
                group = Group.objects.create(name=group_name)
                user.groups.add(group)
            
            user.save()

            # Create user respective profile Mover/Customer
            try:
                if user.role == "MOVER":
                    new_user = Mover.objects.create(user=user)
                elif user.role == "CUSTOMER":
                    new_user = Customer.objects.create(user=user)
                    new_user.phone_number = data.get("phone")
                new_user.save()
            except Exception as e:
                print(e)

            response_data = {
                'status': 'success',
                'data': self.get_serializer(user).data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer