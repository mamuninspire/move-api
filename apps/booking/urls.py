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
router.register('', BookingViewSet)
router.register('rides', RideViewSet)
router.register('ride-searches', RideSearchViewSet)
router.register('ride-requests', RideRequestToMoverViewSet)
router.register('parcel-types', ParcelTypeViewSet)
router.register('parcel-deliveries', ParcelDeliveryViewSet)


urlpatterns = [
    path('', include(router.urls)),  # 👈 Adds the prefix
]