"""
Production-level Document Management API Endpoints
Implements complete document lifecycle: upload, processing, search, extraction
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.db.models import Q
from authentication.r2_service import R2StorageService
from repository.models import Document, DocumentChunk, DocumentMetadata
from repository.document_service import (
    DocumentProcessingService,
    DocumentChunkingService,
    TextExtractionService,
    MetadataExtractionService,
    PIIRedactionService
)
from tenants.models import TenantModel
import logging
import uuid

logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    """Production-level document management API"""
    
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        """Filter documents by tenant"""
        user = self.request.user
        tenant = getattr(user, 'tenant_id', None)
        
        if tenant:
            try:
                tenant_obj = TenantModel.objects.get(id=tenant)
                return Document.objects.filter(tenant=tenant_obj).order_by('-uploaded_at')
            except TenantModel.DoesNotExist:
                return Document.objects.none()
        
        return Document.objects.none()
    
    # ==================== UPLOAD & INGEST ====================
    
    @action(detail=False, methods=['post'], url_path='ingest')
    def ingest_document(self, request):
        """
        POST /api/documents/ingest/
        Upload and process document: extract text, chunk, extract metadata
        """
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({
                'success': False,
                'error': 'No file provided. Use form field name "file".',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get document type if provided
        doc_type = request.data.get('document_type', 'other')
        
        try:
            user = request.user
            tenant = getattr(user, 'tenant_id', None)
            if not tenant:
                return Response({
                    'success': False,
                    'error': 'User has no associated tenant'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                tenant_obj = TenantModel.objects.get(id=tenant)
            except TenantModel.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Tenant {tenant} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Step 1: Store file in R2
            logger.info(f"Uploading file to R2: {file_obj.name}")
            r2_service = R2StorageService()
            r2_key = r2_service.upload_file(file_obj, tenant_id=str(tenant), filename=file_obj.name)
            
            # Step 2: Create Document record
            file_type = file_obj.name.split('.')[-1].lower() if '.' in file_obj.name else 'unknown'
            
            document = Document.objects.create(
                tenant=tenant_obj,
                uploaded_by=user,
                filename=file_obj.name,
                file_type=file_type,
                file_size=file_obj.size,
                r2_key=r2_key,
                document_type=doc_type,
                status='processing'
            )
            
            logger.info(f"Created document record: {document.id}")
            
            # Step 3: Process document (text extraction, chunking, metadata)
            file_obj.seek(0)  # Reset file pointer
            processing_service = DocumentProcessingService()
            result = processing_service.process_document(file_obj, document, r2_service)
            
            if not result['success']:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Processing failed')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Step 4: Create document chunks
            chunks_created = 0
            for chunk_num, chunk in enumerate(result['chunks'], 1):
                DocumentChunk.objects.create(
                    document=document,
                    tenant=tenant_obj,
                    chunk_number=chunk_num,
                    text=chunk['text'],
                    start_char_index=chunk['start_char_index'],
                    end_char_index=chunk['end_char_index'],
                    is_processed=False  # Will be processed with embeddings in next step
                )
                chunks_created += 1
            
            # Step 5: Create metadata record
            DocumentMetadata.objects.create(
                document=document,
                tenant=tenant_obj,
                parties=result['metadata'].get('parties', []),
                contract_value=result['metadata'].get('contract_value'),
                currency=result['metadata'].get('currency'),
                summary=result['metadata'].get('summary'),
                identified_clauses=result['metadata'].get('identified_clauses', []),
                risk_score=result['metadata'].get('risk_score')
            )
            
            logger.info(f"Document processed successfully: {document.id} ({chunks_created} chunks)")
            
            return Response({
                'success': True,
                'document_id': str(document.id),
                'filename': document.filename,
                'status': document.status,
                'r2_key': r2_key,
                'chunks_created': chunks_created,
                'extracted_metadata': document.extracted_metadata,
                'message': 'Document uploaded and processed successfully'
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Document ingestion error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # ==================== RETRIEVE & DOWNLOAD ====================
    
    @action(detail=False, methods=['get'], url_path='download')
    def download_document(self, request):
        """
        GET /api/documents/download/?key=<r2_key>
        Get presigned URL for document download
        """
        r2_key = request.query_params.get('key')
        if not r2_key:
            return Response({
                'success': False,
                'error': 'Missing required query param: key'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify document exists and user has access
            document = Document.objects.get(r2_key=r2_key)
            user = request.user
            user_tenant = getattr(user, 'tenant_id', None)
            
            if user_tenant and document.tenant.id != user_tenant:
                return Response({
                    'success': False,
                    'error': 'Access denied: Document belongs to different tenant'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Generate presigned URL
            r2_service = R2StorageService()
            url = r2_service.generate_presigned_url(r2_key, expiration=3600)
            
            return Response({
                'success': True,
                'key': r2_key,
                'filename': document.filename,
                'url': url,
                'expires_in': 3600
            })
        
        except Document.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Document not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # ==================== LIST & SEARCH ====================
    
    @action(detail=False, methods=['get'], url_path='list')
    def list_documents(self, request):
        """
        GET /api/documents/list/?status=processed&limit=20&offset=0
        List documents for current tenant with filtering
        """
        documents = self.get_queryset()
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            documents = documents.filter(status=status_filter)
        
        # Filter by document type
        doc_type = request.query_params.get('type')
        if doc_type:
            documents = documents.filter(document_type=doc_type)
        
        # Pagination
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))
        
        total = documents.count()
        paginated = documents[offset:offset+limit]
        
        docs_data = []
        for doc in paginated:
            metadata = getattr(doc, 'metadata', None)
            docs_data.append({
                'id': str(doc.id),
                'filename': doc.filename,
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'status': doc.status,
                'document_type': doc.document_type,
                'uploaded_at': doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                'processed_at': doc.processed_at.isoformat() if doc.processed_at else None,
                'chunk_count': doc.chunks.count(),
                'metadata': {
                    'parties': metadata.parties if metadata else [],
                    'contract_value': float(metadata.contract_value) if metadata and metadata.contract_value else None,
                    'currency': metadata.currency if metadata else None,
                    'summary': metadata.summary if metadata else None,
                } if metadata else None
            })
        
        return Response({
            'success': True,
            'documents': docs_data,
            'count': len(docs_data),
            'total': total,
            'offset': offset,
            'limit': limit
        })
    
    # ==================== METADATA EXTRACTION ====================
    
    @action(detail=False, methods=['post'], url_path='extract-metadata')
    def extract_metadata(self, request):
        """
        POST /api/documents/extract-metadata/
        Extract or re-extract metadata from a document
        """
        document_id = request.data.get('document_id')
        if not document_id:
            return Response({
                'success': False,
                'error': 'Missing document_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            document = Document.objects.get(id=document_id)
            user = request.user
            user_tenant = getattr(user, 'tenant_id', None)
            
            if user_tenant and document.tenant.id != user_tenant:
                return Response({
                    'success': False,
                    'error': 'Access denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if not document.full_text:
                return Response({
                    'success': False,
                    'error': 'Document has no extracted text'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract metadata
            metadata_service = MetadataExtractionService()
            metadata = metadata_service.extract_metadata(document.full_text[:3000])
            
            # Update or create metadata record
            doc_metadata, created = DocumentMetadata.objects.get_or_create(
                document=document,
                defaults={'tenant': document.tenant}
            )
            
            doc_metadata.parties = metadata.get('parties', [])
            doc_metadata.contract_value = metadata.get('contract_value')
            doc_metadata.currency = metadata.get('currency')
            doc_metadata.effective_date = metadata.get('effective_date')
            doc_metadata.expiration_date = metadata.get('expiration_date')
            doc_metadata.identified_clauses = metadata.get('identified_clauses', [])
            doc_metadata.summary = metadata.get('summary')
            doc_metadata.risk_score = metadata.get('risk_score')
            doc_metadata.save()
            
            logger.info(f"Metadata extracted for document {document_id}")
            
            return Response({
                'success': True,
                'metadata': metadata
            })
        
        except Document.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Document not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Metadata extraction error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # ==================== DELETE ====================
    
    @action(detail=False, methods=['delete'], url_path='delete')
    def delete_document(self, request):
        """
        DELETE /api/documents/delete/?id=<document_id>
        Delete document and clean up R2 storage
        """
        document_id = request.query_params.get('id')
        if not document_id:
            return Response({
                'success': False,
                'error': 'Missing document id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            document = Document.objects.get(id=document_id)
            user = request.user
            user_tenant = getattr(user, 'tenant_id', None)
            
            if user_tenant and document.tenant.id != user_tenant:
                return Response({
                    'success': False,
                    'error': 'Access denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Delete from R2
            r2_service = R2StorageService()
            try:
                r2_service.delete_file(document.r2_key)
            except Exception as e:
                logger.warning(f"Failed to delete R2 file {document.r2_key}: {str(e)}")
            
            # Delete document and related records
            filename = document.filename
            document.delete()
            
            logger.info(f"Document deleted: {filename}")
            
            return Response({
                'success': True,
                'message': f'Document {filename} deleted successfully'
            })
        
        except Document.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Document not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Delete error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
