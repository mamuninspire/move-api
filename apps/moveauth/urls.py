from rest_framework import routers
from .api_views import UserViewSet

router = routers.DefaultRouter()
router.register('auth', UserViewSet)


urlpatterns = router.urls
