from rest_framework import serializers
from .models import RideSearch, RideRequestToMover, Ride, ParcelDelivery, ParcelType, Booking
from apps.mover.models import VehicleType, VehicleMake, VehicleModel, Mover
from core.models import Comment  # if your Comment model is located there
from core.serializers import CommentSerializer
import pdb


class RideSearchSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(read_only=True)  # or nested serializer if you want
    vehicle_type = serializers.StringRelatedField()
    vehicle_make = serializers.StringRelatedField()
    vehicle_model = serializers.StringRelatedField()

    class Meta:
        model = RideSearch
        fields = '__all__'
    
    def create(self, validated_data):
        vehicle_preferences = validated_data.get('vehicle_preferences', {})

        # Try to get the objects based on name (StringRelatedField uses __str__, so we assume name)
        vehicle_type = None
        if vehicle_preferences.get('vehicle_type'):
            vehicle_type = VehicleType.objects.filter(name__icontains=vehicle_preferences['vehicle_type']).first()

        vehicle_make = None
        if vehicle_preferences.get('vehicle_make'):
            vehicle_make = VehicleMake.objects.filter(name__icontains=vehicle_preferences['vehicle_make']).first()

        vehicle_model = None
        if vehicle_preferences.get('vehicle_model'):
            vehicle_model = VehicleModel.objects.filter(name__icontains=vehicle_preferences['vehicle_model']).first()

        # Create RideSearch instance
        ride_search = RideSearch.objects.create(
            vehicle_type=vehicle_type,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            **validated_data
        )
        return ride_search


class RideRequestToMoverSerializer(serializers.ModelSerializer):
    ride_search_id = serializers.IntegerField(write_only=True)
    mover_id = serializers.UUIDField(write_only=True)
    comments = serializers.CharField(write_only=True, required=False)

    existing_comments = CommentSerializer(source='comments', many=True, read_only=True)


    class Meta:
        model = RideRequestToMover
        fields = [
            'id',
            'ride_search_id',
            'mover_id',
            'estimated_cost',
            'proposed_price',
            'agreed_price',
            'status',
            'comments',
            'existing_comments',
        ]
        read_only_fields = ['agreed_price', 'status']
    
    def get_comments(self, obj):
        return [str(comment) for comment in obj.comments.all()]  # Customize as needed
    
    def create(self, validated_data):
        ride_search_id = validated_data.pop('ride_search_id')
        mover_id = validated_data.pop('mover_id')
        comments_text = validated_data.pop('comments', None)

        estimated_cost = validated_data.pop('estimated_cost')
        proposed_price = validated_data.get('proposed_price')
        if proposed_price is None:
            validated_data['proposed_price'] = estimated_cost

        ride_search = RideSearch.objects.get(id=ride_search_id)
        mover = Mover.objects.get(mover_id=mover_id)

        # Try to get existing instance
        instance = RideRequestToMover.objects.filter(ride_search=ride_search, mover=mover).first()
        if instance:
            # update fields
            # instance.estimated_cost = validated_data['estimated_cost']
            instance.proposed_price = validated_data['proposed_price']
            instance.save()
        else:
            # create new instance
            instance = RideRequestToMover.objects.create(
                ride_search=ride_search,
                mover=mover,
                **validated_data
            )

        # If comments provided, create new comment
        if comments_text:
            Comment.objects.create(
                content_object=instance,
                text=comments_text,
                user=self.context['request'].user
            )

        return instance

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


