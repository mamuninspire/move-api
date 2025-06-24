from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    DriverViewSet, VehicleViewSet, MoverViewSet,
    VehicleImagesViewSet, DocumentTypeViewSet,
    DocumentsViewSet, VehicleTypeViewSet,
    VehicleMakeViewSet, VehicleModelViewSet, ServiceTypeViewSet
)

router = DefaultRouter()
router.register('drivers', DriverViewSet)
router.register('vehicles', VehicleViewSet)
router.register('movers', MoverViewSet)
router.register('vehicle-images', VehicleImagesViewSet)
router.register('document-types', DocumentTypeViewSet)
router.register('documents', DocumentsViewSet)
router.register('vehicle-types', VehicleTypeViewSet)
router.register('vehicle-makes', VehicleMakeViewSet)
router.register('vehicle-models', VehicleModelViewSet)
router.register('service-types', ServiceTypeViewSet)


urlpatterns = [
    path('movers/', include(router.urls)),
]
