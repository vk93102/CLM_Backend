from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import MetadataFieldModel
from .serializers import MetadataFieldSerializer

class MetadataFieldViewSet(viewsets.ModelViewSet):
    queryset = MetadataFieldModel.objects.all()
    serializer_class = MetadataFieldSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id)
