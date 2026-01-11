from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import RuleModel
from .serializers import RuleSerializer

class RuleViewSet(viewsets.ModelViewSet):
    queryset = RuleModel.objects.all()
    serializer_class = RuleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id)
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        conditions = request.data.get('conditions', {})
        is_valid = len(conditions) > 0
        return Response({'valid': is_valid})
