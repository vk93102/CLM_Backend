from rest_framework.routers import SimpleRouter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class AnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'contracts_analyzed': 150,
            'clauses_extracted': 2500,
            'completion_rate': 95.5
        })

class DocumentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'documents': []})

class GenerationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'generations': []})
