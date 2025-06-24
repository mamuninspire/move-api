from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)


# Swagger/OpenAPI schema
schema_view = get_schema_view(
    openapi.Info(
        title="Ride Booking API",
        default_version='v1',
        description="API documentation for the Ride & Booking system",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


admin.site.site_title = "MOVE Super Admin"
admin.site.site_header = "MOVE Super Admin"

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api-auth/', include('rest_framework.urls')),
    
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # path('api/v1/', include('apps.moveauth.urls')),
    # path('api/v1/', include('apps.mover.urls')),
    
    path('api/v1/', include('apps.moveauth.urls')),
    path('api/v1/movers/', include('apps.mover.urls')),
    path('api/v1/bookings/', include('apps.booking.urls')),
    path('api/v1/customers/', include('apps.customer.urls')),

    # Swagger docs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
