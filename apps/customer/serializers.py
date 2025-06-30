from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Customer
from apps.moveauth.serializers import UserSerializer

User = get_user_model()




class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'customer_id',
            'user',
            'bio',
            'address',
            'mobile',
            'is_mobile_verified',
            'is_whatsapp_verified',
        ]
