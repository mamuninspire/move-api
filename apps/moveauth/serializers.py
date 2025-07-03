from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_mover',
            'is_customer',
            'profile_image',
            'gender',
            'dob',
            'is_active',
            'is_staff',
            'date_joined',
        ]
        read_only_fields = ['id', 'is_active', 'is_staff', 'date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'role', 'is_mover', 'is_customer', 'first_name', 'last_name')

    def create(self, validated_data):
        password = validated_data.pop('password')
        print(f"validated_data: {validated_data}")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer that adds user data to the token response
    """
    @classmethod
    def get_token(cls, user):
        # add custom claims if you want
        token = super().get_token(user)
        # token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # add serialized user data
        user = self.user
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'name': user.get_full_name(),
            'role': user.role,
            'is_mover': user.is_mover,
            'is_customer': user.is_customer,
            'profile_image': user.profile_image.url if user.profile_image else None,
            'gender': user.gender,
            'dob': user.dob,
        }
        return data