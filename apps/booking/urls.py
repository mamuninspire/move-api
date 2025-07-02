from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    RideSearchViewSet,
    RideRequestToMoverViewSet,
    RideViewSet,
    ParcelTypeViewSet,
    ParcelDeliveryViewSet,
    BookingViewSet
)

router = DefaultRouter()

router.register(r'rides', RideViewSet)
router.register(r'ride-searches', RideSearchViewSet)
router.register(r'ride-requests', RideRequestToMoverViewSet)
router.register(r'parcel-types', ParcelTypeViewSet)
router.register(r'parcel-deliveries', ParcelDeliveryViewSet)
router.register(r'', BookingViewSet)


urlpatterns = [
    path('', include(router.urls)),  # 👈 Adds the prefix
]