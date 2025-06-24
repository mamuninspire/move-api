from rest_framework import serializers
from .models import RideSearch, RideRequestToMover, Ride, ParcelDelivery, ParcelType, Booking
from core.models import Comment  # if your Comment model is located there


class RideSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideSearch
        fields = '__all__'


class RideRequestToMoverSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    def get_comments(self, obj):
        return [str(comment) for comment in obj.comments.all()]  # Customize as needed

    class Meta:
        model = RideRequestToMover
        fields = '__all__'

class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = '__all__'

class RideNestedSerializer(serializers.ModelSerializer):
    booking_request_mover = RideRequestToMoverSerializer()

    class Meta:
        model = Ride
        fields = '__all__'

class ParcelTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelType
        fields = '__all__'

class ParcelDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelDelivery
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


