from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AIInferenceModel
from .serializers import AIInferenceSerializer
from django.utils import timezone

class AIViewSet(viewsets.ModelViewSet):
    queryset = AIInferenceModel.objects.all()
    serializer_class = AIInferenceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    @action(detail=False, methods=['post'])
    def infer(self, request):
        model_name = request.data.get('model_name', 'default-model')
        input_data = request.data.get('input', {})
        inference = AIInferenceModel.objects.create(
            tenant_id=request.user.tenant_id,
            model_name=model_name,
            input_data=input_data,
            status='processing'
        )
        return Response(AIInferenceSerializer(inference).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def status(self, request, id=None):
        inference = self.get_object()
        return Response({'id': str(inference.id), 'status': inference.status})
    
    @action(detail=True, methods=['get'])
    def result(self, request, id=None):
        inference = self.get_object()
        return Response(inference.output)
    
    @action(detail=False, methods=['get'])
    def usage(self, request):
        total = AIInferenceModel.objects.count()
        return Response({'total_inferences': total, 'this_month': total})
