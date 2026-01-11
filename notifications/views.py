from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import NotificationModel
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = NotificationModel.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id)
