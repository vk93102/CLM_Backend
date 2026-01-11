from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import RedactionJobModel
from .serializers import RedactionJobSerializer

class RedactionViewSet(viewsets.ModelViewSet):
    queryset = RedactionJobModel.objects.all()
    serializer_class = RedactionJobSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    @action(detail=False, methods=['post'])
    def scan(self, request):
        document_id = request.data.get('document_id')
        patterns = request.data.get('patterns', [])
        job = RedactionJobModel.objects.create(
            tenant_id=request.user.tenant_id,
            document_id=document_id,
            patterns=patterns,
            status='processing'
        )
        return Response(RedactionJobSerializer(job).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def redact(self, request):
        document_id = request.data.get('document_id')
        content = request.data.get('content', '')
        job = RedactionJobModel.objects.create(
            tenant_id=request.user.tenant_id,
            document_id=document_id,
            status='completed',
            redacted_content=content
        )
        return Response(RedactionJobSerializer(job).data)
