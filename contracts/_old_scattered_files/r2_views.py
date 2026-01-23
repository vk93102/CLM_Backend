"""
Cloudflare R2 Document Upload Views
Simple endpoints for uploading documents and getting downloadable links
"""
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import uuid

from authentication.r2_service import R2StorageService
from .models import Contract, ContractVersion
import hashlib


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_document(request):
    """
    POST /api/contracts/upload-document/
    
    Upload any document to Cloudflare R2 and get a downloadable link.
    
    Request (multipart/form-data):
        - file: The document file to upload (required)
        - filename: Optional custom filename
    
    Response:
    {
        "success": true,
        "file_id": "uuid",
        "r2_key": "tenant_id/contracts/uuid.pdf",
        "download_url": "https://...",
        "original_filename": "document.pdf",
        "file_size": 123456,
        "uploaded_at": "2026-01-20T12:00:00Z"
    }
    """
    uploaded_file = request.FILES.get('file')
    
    if not uploaded_file:
        return Response(
            {
                'success': False,
                'error': 'No file provided',
                'message': 'Please provide a file in the request'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get tenant ID from authenticated user
        tenant_id = str(request.user.tenant_id)
        
        # Get custom filename if provided, otherwise use original
        custom_filename = request.data.get('filename') or uploaded_file.name
        
        # Upload to R2
        r2_service = R2StorageService()
        r2_key = r2_service.upload_file(uploaded_file, tenant_id, custom_filename)
        
        # Generate download URL
        download_url = r2_service.generate_presigned_url(r2_key, expiration=3600)  # 1 hour
        
        # Get file size
        file_size = uploaded_file.size
        
        return Response({
            'success': True,
            'file_id': str(uuid.uuid4()),
            'r2_key': r2_key,
            'download_url': download_url,
            'original_filename': uploaded_file.name,
            'file_size': file_size,
            'uploaded_at': timezone.now().isoformat(),
            'message': 'File uploaded successfully to Cloudflare R2'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'message': 'Failed to upload file to Cloudflare R2'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_contract_document(request):
    """
    POST /api/contracts/upload-contract-document/
    
    Upload a contract document to Cloudflare R2 and optionally create a Contract record.
    
    Request (multipart/form-data):
        - file: The contract PDF/document to upload (required)
        - title: Contract title (optional)
        - contract_type: Type of contract (optional)
        - counterparty: Counterparty name (optional)
        - create_contract: Boolean - whether to create a Contract record (default: false)
    
    Response:
    {
        "success": true,
        "contract_id": "uuid",  // Only if create_contract=true
        "r2_key": "tenant_id/contracts/uuid.pdf",
        "download_url": "https://...",
        "original_filename": "contract.pdf",
        "file_size": 123456,
        "uploaded_at": "2026-01-20T12:00:00Z"
    }
    """
    uploaded_file = request.FILES.get('file')
    
    if not uploaded_file:
        return Response(
            {
                'success': False,
                'error': 'No file provided',
                'message': 'Please provide a file in the request'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get tenant and user info
        tenant_id = str(request.user.tenant_id)
        user_id = str(request.user.user_id)
        
        # Get optional parameters
        title = request.data.get('title') or f'Uploaded Contract - {timezone.now().strftime("%Y-%m-%d")}'
        contract_type = request.data.get('contract_type')
        counterparty = request.data.get('counterparty')
        create_contract = request.data.get('create_contract', 'false').lower() in ['true', '1', 'yes']
        
        # Upload to R2
        r2_service = R2StorageService()
        r2_key = r2_service.upload_file(uploaded_file, tenant_id, uploaded_file.name)
        
        # Generate download URL
        download_url = r2_service.generate_presigned_url(r2_key, expiration=86400)  # 24 hours
        
        # Get file info
        file_size = uploaded_file.size
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)  # Reset for potential re-read
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        
        response_data = {
            'success': True,
            'r2_key': r2_key,
            'download_url': download_url,
            'original_filename': uploaded_file.name,
            'file_size': file_size,
            'uploaded_at': timezone.now().isoformat(),
            'message': 'Contract uploaded successfully to Cloudflare R2'
        }
        
        # Optionally create Contract record
        if create_contract:
            contract = Contract.objects.create(
                tenant_id=uuid.UUID(tenant_id),
                title=title,
                contract_type=contract_type or 'other',
                counterparty=counterparty,
                status='draft',
                created_by=uuid.UUID(user_id),
                document_r2_key=r2_key,
            )
            
            # Create first version
            ContractVersion.objects.create(
                contract=contract,
                version_number=1,
                r2_key=r2_key,
                template_id=uuid.uuid4(),  # Placeholder
                template_version=1,
                change_summary='Initial upload',
                created_by=uuid.UUID(user_id),
                file_size=file_size,
                file_hash=file_hash,
            )
            
            response_data['contract_id'] = str(contract.id)
            response_data['contract_title'] = contract.title
            response_data['contract_status'] = contract.status
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        import traceback
        return Response(
            {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'message': 'Failed to upload contract document'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_download_url(request):
    """
    GET /api/contracts/document-download-url/?r2_key=<r2_key>
    
    Get a downloadable link for a document stored in Cloudflare R2.
    
    Query Parameters:
        - r2_key: The R2 key of the document
        - expiration: Optional expiration time in seconds (default: 3600)
    
    Response:
    {
        "success": true,
        "r2_key": "tenant_id/contracts/uuid.pdf",
        "download_url": "https://...",
        "expiration_seconds": 3600
    }
    """
    r2_key = request.query_params.get('r2_key')
    
    if not r2_key:
        return Response(
            {
                'success': False,
                'error': 'r2_key parameter is required',
                'message': 'Please provide an r2_key query parameter'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get expiration time (default: 1 hour)
        expiration = int(request.query_params.get('expiration', 3600))
        
        # Generate download URL
        r2_service = R2StorageService()
        download_url = r2_service.generate_presigned_url(r2_key, expiration=expiration)
        
        return Response({
            'success': True,
            'r2_key': r2_key,
            'download_url': download_url,
            'expiration_seconds': expiration,
            'expires_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'message': 'Failed to generate download URL'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_contract_download_url(request, contract_id):
    """
    GET /api/contracts/{contract_id}/download-url/
    
    Get a downloadable link for a specific contract.
    
    Path Parameters:
        - contract_id: UUID of the contract
    
    Response:
    {
        "success": true,
        "contract_id": "uuid",
        "contract_title": "My Contract",
        "version_number": 1,
        "r2_key": "tenant_id/contracts/uuid.pdf",
        "download_url": "https://...",
        "file_size": 123456
    }
    """
    try:
        # Get contract
        contract = Contract.objects.get(
            id=contract_id,
            tenant_id=request.user.tenant_id
        )
        
        # Get latest version
        try:
            latest_version = contract.versions.latest('version_number')
            r2_key = latest_version.r2_key
            version_number = latest_version.version_number
            file_size = latest_version.file_size
        except ContractVersion.DoesNotExist:
            # Fallback to document_r2_key if no versions exist
            if contract.document_r2_key:
                r2_key = contract.document_r2_key
                version_number = contract.current_version
                file_size = None
            else:
                return Response(
                    {
                        'success': False,
                        'error': 'No document available for this contract',
                        'message': 'This contract does not have an uploaded document'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Generate download URL
        r2_service = R2StorageService()
        download_url = r2_service.generate_presigned_url(r2_key, expiration=3600)
        
        return Response({
            'success': True,
            'contract_id': str(contract.id),
            'contract_title': contract.title,
            'version_number': version_number,
            'r2_key': r2_key,
            'download_url': download_url,
            'file_size': file_size
        })
        
    except Contract.DoesNotExist:
        return Response(
            {
                'success': False,
                'error': 'Contract not found',
                'message': f'No contract found with ID {contract_id}'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'message': 'Failed to get contract download URL'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
