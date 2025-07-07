from rest_framework import serializers
from .models import RideSearch, RideRequestToMover, Ride, ParcelDelivery, ParcelType, Booking
from apps.mover.models import VehicleType, VehicleMake, VehicleModel, Mover
from apps.mover.serializers import MoverSerializer
from core.models import Comment  # if your Comment model is located there
from core.serializers import CommentSerializer
import pdb


class RideSearchSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(read_only=True)  # or nested serializer if you want
    vehicle_type = serializers.StringRelatedField()
    vehicle_make = serializers.StringRelatedField()
    vehicle_model = serializers.StringRelatedField()
    pickup_date = serializers.DateField(required=False, allow_null=True)
    pickup_time = serializers.TimeField(required=False, allow_null=True)
    duration = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = RideSearch
        fields = '__all__'
    
    def validate_pickup_date(self, value):
        if value == '':
            return None
        return value

    def validate_pickup_time(self, value):
        if value == '':
            return None
        return value

    def validate_duration(self, value):
        if value == '':
            return None
        return value
    
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
    
    def to_representation(self, instance):
        # Start with default representation
        representation = super().to_representation(instance)

        # Add full nested mover data
        # representation['mover'] = MoverSerializer(instance.mover).data if instance.mover else None

        # # Add full nested ride_search data
        # representation['ride_search'] = RideSearchSerializer(instance.ride_search).data if instance.ride_search else None

        representation['createdAt'] = instance.created_at
        representation['type'] = 'ride'
        representation['driverName'] = instance.mover.driver_name
        representation['customerName'] = instance.ride_search.customer_name
        representation['estimatedPrice'] = instance.estimated_cost
        representation['proposedPrice'] = instance.proposed_price
        representation['pickup'] = instance.ride_search.pickup_location
        representation['dropoff'] = instance.ride_search.dropoff_location
        representation['to'] = instance.ride_search.dropoff_location_name
        representation['from'] = instance.ride_search.pickup_location_name
        representation['bookingTime'] = instance.ride_search.booking_time
        representation['ride_datetime'] = instance.ride_search.ride_datetime        


        return representation
    
    def create(self, validated_data):
        # pdb.set_trace()
        ride_search_id = validated_data.pop('ride_search_id')
        mover_id = validated_data.pop('mover_id')
        comments_text = validated_data.pop('comments', None)

        estimated_cost = validated_data.get('estimated_cost')
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
    booking_request_mover = RideRequestToMoverSerializer()
    status = serializers.CharField()

    class Meta:
        model = Ride
        fields = [
            'ride_id',
            'status',
            'rating',
            'booking_request_mover',
        ]
    
    def to_representation(self, instance):
        # Start with default representation
        representation = super().to_representation(instance)
        representation['type'] = 'ride'
        representation['from'] = instance.booking_request_mover.ride_search.pickup_location_name
        representation['to'] = instance.booking_request_mover.ride_search.dropoff_location_name
        representation['MOVER'] = instance.booking_request_mover.mover.driver_name
        representation['ride_datetime'] = instance.booking_request_mover.ride_search.booking_time

        return representation


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


