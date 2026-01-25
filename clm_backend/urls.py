"""
URL configuration for clm_backend project.
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('notifications.urls')),
    path('api/v1/', include('contracts.urls')),
    path('api/v1/', include('workflows.urls')),
    path('api/v1/', include('approvals.urls')),
]
