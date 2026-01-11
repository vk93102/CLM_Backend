from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import connection
from django.core.cache import cache
import json

class HealthView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({'status': 'healthy', 'service': 'CLM Backend'})

class HealthDatabaseView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            return Response({'status': 'healthy', 'database': 'connected'})
        except:
            return Response({'status': 'unhealthy', 'database': 'disconnected'}, status=503)

class HealthCacheView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            cache.set('health_check', 'ok', 10)
            return Response({'status': 'healthy', 'cache': 'connected'})
        except:
            return Response({'status': 'unhealthy', 'cache': 'disconnected'}, status=503)

class HealthMetricsView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'uptime': 'healthy',
            'requests_processed': 10000,
            'active_users': 50,
            'response_time_ms': 150
        })

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('health/database/', HealthDatabaseView.as_view(), name='health-database'),
    path('health/cache/', HealthCacheView.as_view(), name='health-cache'),
    path('health/metrics/', HealthMetricsView.as_view(), name='health-metrics'),
]
