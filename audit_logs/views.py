from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AuditLogModel
from .serializers import AuditLogSerializer
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLogModel.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    @action(detail=True, methods=['get'])
    def events(self, request, id=None):
        audit_log = self.get_object()
        events = AuditLogModel.objects.filter(entity_id=id).order_by('-created_at')
        return Response(AuditLogSerializer(events, many=True).data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        last_24h = timezone.now() - timedelta(hours=24)
        stats = {
            'total_logs': AuditLogModel.objects.count(),
            'last_24h': AuditLogModel.objects.filter(created_at__gte=last_24h).count(),
            'by_action': dict(AuditLogModel.objects.values('action').annotate(count=Count('id')).values_list('action', 'count')),
            'by_entity': dict(AuditLogModel.objects.values('entity_type').annotate(count=Count('id')).values_list('entity_type', 'count'))
        }
        return Response(stats)
