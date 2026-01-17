from rest_framework.routers import SimpleRouter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from authentication.r2_service import R2StorageService
import uuid

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
        """Retrieve document: returns a presigned URL if key is provided."""
        r2 = R2StorageService()
        r2_key = request.query_params.get('key')

        if not r2_key:
            return Response({
                'success': False,
                'error': 'Missing required query param: key',
            }, status=status.HTTP_400_BAD_REQUEST)

        exists = r2.file_exists(r2_key)
        if not exists:
            return Response({
                'success': False,
                'exists': False,
                'error': 'File not found in R2',
                'key': r2_key,
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            url = r2.generate_presigned_url(r2_key, expiration=3600)
            return Response({
                'success': True,
                'exists': True,
                'key': r2_key,
                'url': url,
                'expires_in': 3600,
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'key': r2_key,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Upload a document to Cloudflare R2 and return its key and URL."""
        r2 = R2StorageService()

        file_obj = request.FILES.get('file') or request.FILES.get('document')
        if not file_obj:
            return Response({
                'success': False,
                'error': 'Missing file in request. Use form field name "file".',
            }, status=status.HTTP_400_BAD_REQUEST)

        # Use authenticated user's tenant_id for isolation
        tenant_id = getattr(request.user, 'tenant_id', None)
        if not tenant_id:
            tenant_id = uuid.uuid4()

        try:
            r2_key = r2.upload_file(file_obj, tenant_id=str(tenant_id), filename=file_obj.name)
            url = r2.generate_presigned_url(r2_key, expiration=3600)
            return Response({
                'success': True,
                'key': r2_key,
                'url': url,
                'expires_in': 3600,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'generations': []})
