from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import *

router = DefaultRouter()

# Register viewsets
router.register(r'vehicle-types', VehicleTypeViewSet)
router.register(r'vehicle-makes', VehicleMakeViewSet)
router.register(r'vehicle-models', VehicleModelViewSet)
router.register(r'vehicle-body-styles', VehicleBodyStyleViewSet)
router.register(r'service-types', ServiceTypeViewSet)
router.register(r'vehicles', VehicleViewSet)
router.register(r'vehicle-images', VehicleImagesViewSet)
router.register(r'document-types', DocumentTypeViewSet)
router.register(r'documents', DocumentsViewSet)
router.register(r'', MoverViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
