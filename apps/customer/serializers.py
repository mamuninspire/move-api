from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Customer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']  # Add more fields if needed

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(source='user', queryset=User.objects.all(), write_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'user', 'user_id', 'bio', 'address']
