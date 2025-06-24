from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CustomerViewSet

router = DefaultRouter()
router.register('', CustomerViewSet, basename='customers')

urlpatterns = router.urls