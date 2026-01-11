"""
URL configuration for clm_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from health_views import HealthView, HealthDatabaseView, HealthCacheView, HealthMetricsView
from misc_views import AnalysisView, DocumentView, GenerationView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('contracts.urls')),
    path('api/', include('workflows.urls')),
    path('api/', include('notifications.urls')),
    path('api/', include('audit_logs.urls')),
    path('api/', include('search.urls')),
    path('api/', include('repository.urls')),
    path('api/', include('metadata.urls')),
    path('api/', include('ocr.urls')),
    path('api/', include('redaction.urls')),
    path('api/', include('ai.urls')),
    path('api/', include('rules.urls')),
    path('api/', include('approvals.urls')),
    path('api/', include('tenants.urls')),
    path('api/health/', HealthView.as_view(), name='health'),
    path('api/health/database/', HealthDatabaseView.as_view(), name='health-database'),
    path('api/health/cache/', HealthCacheView.as_view(), name='health-cache'),
    path('api/health/metrics/', HealthMetricsView.as_view(), name='health-metrics'),
    path('api/analysis/', AnalysisView.as_view(), name='analysis'),
    path('api/documents/', DocumentView.as_view(), name='documents'),
    path('api/generation/', GenerationView.as_view(), name='generation'),
]
