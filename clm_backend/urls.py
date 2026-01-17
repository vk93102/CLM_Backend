"""
URL configuration for clm_backend project.
"""
from django.contrib import admin
from django.urls import path, include
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rest_framework.routers import DefaultRouter
from health_views import HealthView, HealthDatabaseView, HealthCacheView, HealthMetricsView
from misc_views import AnalysisView, DocumentView, GenerationView
from admin_views import AdminViewSet, list_roles, list_permissions, list_users

router = DefaultRouter()
router.register(r'admin', AdminViewSet, basename='admin')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/v1/', include('contracts.urls')),
    path('api/v1/', include('workflows.urls')),
    path('api/v1/', include('notifications.urls')),
    path('api/v1/', include('audit_logs.urls')),
    path('api/v1/', include('repository.urls')),
    path('api/v1/', include('metadata.urls')),
    path('api/v1/', include('ocr.urls')),
    path('api/v1/', include('redaction.urls')),
    path('api/v1/', include('ai.urls')),
    path('api/v1/', include('rules.urls')),
    path('api/v1/', include('approvals.urls')),
    path('api/v1/', include('tenants.urls')),
    path('api/v1/', include(router.urls)),
    path('api/v1/roles/', list_roles, name='roles'),
    path('api/v1/permissions/', list_permissions, name='permissions'),
    path('api/v1/users/', list_users, name='users'),
    path('api/v1/health/', HealthView.as_view(), name='health'),
    path('api/v1/health/database/', HealthDatabaseView.as_view(), name='health-database'),
    path('api/v1/health/cache/', HealthCacheView.as_view(), name='health-cache'),
    path('api/v1/health/metrics/', HealthMetricsView.as_view(), name='health-metrics'),
    path('api/v1/analysis/', AnalysisView.as_view(), name='analysis'),
    path('api/v1/documents/', DocumentView.as_view(), name='documents'),
    path('api/v1/generation/', GenerationView.as_view(), name='generation'),
]
