"""
Search API Endpoints
Semantic, keyword, hybrid, and clause-based search
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from repository.search_service import SemanticSearchService
from repository.models import Document, DocumentChunk, DocumentMetadata

logger = logging.getLogger(__name__)


class SearchViewSet(viewsets.ViewSet):
    """Search endpoints for document retrieval"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_service = SemanticSearchService()
    
    @action(detail=False, methods=['get'], url_path='semantic')
    def semantic_search(self, request):
        """
        Semantic search using vector embeddings
        GET /api/search/semantic/?q=liability+clauses&top_k=10&threshold=0.5
        """
        try:
            query = request.query_params.get('q', '')
            if not query:
                return Response({
                    'success': False,
                    'error': 'Query parameter "q" is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            top_k = int(request.query_params.get('top_k', '10'))
            threshold = float(request.query_params.get('threshold', '0.1'))
            
            # Get user's tenant - MUST convert to string UUID
            tenant_id = getattr(request.user, 'tenant_id', None)
            if tenant_id:
                tenant_id = str(tenant_id)
            
            logger.info(f"User: {request.user}, Tenant ID: {tenant_id}")
            
            if not tenant_id:
                logger.error(f"No tenant found for user {request.user}")
                return Response({
                    'success': False,
                    'error': 'No tenant found'
                }, status=status.HTTP_403_FORBIDDEN)
            
            logger.info(f"Semantic search: query='{query}', tenant={tenant_id}, top_k={top_k}")
            
            # Perform search
            results = self.search_service.semantic_search(
                query=query,
                tenant_id=tenant_id,
                top_k=top_k,
                threshold=threshold
            )
            
            return Response({
                'success': True,
                'query': query,
                'search_type': 'semantic',
                'count': len(results),
                'results': results
            }, status=status.HTTP_200_OK)
        
        except ValueError as e:
            logger.error(f"Invalid parameters: {str(e)}")
            return Response({
                'success': False,
                'error': f'Invalid parameter: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='keyword')
    def keyword_search(self, request):
        """
        Keyword search across document chunks
        GET /api/search/keyword/?q=termination+clause&limit=20
        """
        try:
            query = request.query_params.get('q', '')
            if not query:
                return Response({
                    'success': False,
                    'error': 'Query parameter "q" is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            top_k = int(request.query_params.get('limit', '20'))
            
            # Get user's tenant
            tenant_id = getattr(request.user, 'tenant_id', None)
            if not tenant_id:
                return Response({
                    'success': False,
                    'error': 'No tenant found'
                }, status=status.HTTP_403_FORBIDDEN)
            
            logger.info(f"Keyword search: query='{query}', tenant={tenant_id}")
            
            # Perform search
            results = self.search_service.keyword_search(
                query=query,
                tenant_id=tenant_id,
                top_k=top_k
            )
            
            return Response({
                'success': True,
                'query': query,
                'search_type': 'keyword',
                'count': len(results),
                'results': results
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Keyword search error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='hybrid')
    def hybrid_search(self, request):
        """
        Hybrid search combining semantic and keyword search
        GET /api/search/hybrid/?q=liability+clauses&top_k=10&semantic_weight=0.7
        """
        try:
            query = request.query_params.get('q', '')
            if not query:
                return Response({
                    'success': False,
                    'error': 'Query parameter "q" is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            top_k = int(request.query_params.get('top_k', '10'))
            semantic_weight = float(request.query_params.get('semantic_weight', '0.7'))
            keyword_weight = float(request.query_params.get('keyword_weight', '0.3'))
            
            # Validate weights
            if not (0 <= semantic_weight <= 1) or not (0 <= keyword_weight <= 1):
                return Response({
                    'success': False,
                    'error': 'Weights must be between 0 and 1'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user's tenant
            tenant_id = getattr(request.user, 'tenant_id', None)
            if not tenant_id:
                return Response({
                    'success': False,
                    'error': 'No tenant found'
                }, status=status.HTTP_403_FORBIDDEN)
            
            logger.info(f"Hybrid search: query='{query}', tenant={tenant_id}, top_k={top_k}")
            
            # Perform search
            results = self.search_service.hybrid_search(
                query=query,
                tenant_id=tenant_id,
                top_k=top_k,
                semantic_weight=semantic_weight,
                keyword_weight=keyword_weight
            )
            
            return Response({
                'success': True,
                'query': query,
                'search_type': 'hybrid',
                'count': len(results),
                'semantic_weight': semantic_weight,
                'keyword_weight': keyword_weight,
                'results': results
            }, status=status.HTTP_200_OK)
        
        except ValueError as e:
            logger.error(f"Invalid parameters: {str(e)}")
            return Response({
                'success': False,
                'error': f'Invalid parameter: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Hybrid search error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='clauses')
    def search_clauses(self, request):
        """
        Search for specific clause types
        GET /api/search/clauses/?type=Confidentiality&limit=20
        """
        try:
            clause_type = request.query_params.get('type', '')
            if not clause_type:
                return Response({
                    'success': False,
                    'error': 'Query parameter "type" is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            top_k = int(request.query_params.get('limit', '20'))
            
            # Get user's tenant
            tenant_id = getattr(request.user, 'tenant_id', None)
            if not tenant_id:
                return Response({
                    'success': False,
                    'error': 'No tenant found'
                }, status=status.HTTP_403_FORBIDDEN)
            
            logger.info(f"Clause search: type='{clause_type}', tenant={tenant_id}")
            
            # Perform search
            results = self.search_service.search_by_clause(
                clause_type=clause_type,
                tenant_id=tenant_id,
                top_k=top_k
            )
            
            return Response({
                'success': True,
                'clause_type': clause_type,
                'search_type': 'clause',
                'count': len(results),
                'results': results
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Clause search error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='advanced')
    def advanced_search(self, request):
        """
        Advanced search with filters
        POST /api/search/advanced/
        Body: {"query": "confidential", "filters": {"document_type": "contract"}, "top_k": 10}
        """
        try:
            query = request.data.get('query', '')
            if not query:
                return Response({
                    'success': False,
                    'error': 'Query is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            filters = request.data.get('filters', {})
            top_k = int(request.data.get('top_k', '10'))
            
            # Get user's tenant
            tenant_id = getattr(request.user, 'tenant_id', None)
            if not tenant_id:
                return Response({
                    'success': False,
                    'error': 'No tenant found'
                }, status=status.HTTP_403_FORBIDDEN)
            
            logger.info(f"Advanced search: query='{query}', filters={filters}, tenant={tenant_id}")
            
            # Perform search
            results = self.search_service.advanced_search(
                query=query,
                tenant_id=tenant_id,
                filters=filters,
                top_k=top_k
            )
            
            return Response({
                'success': True,
                'query': query,
                'search_type': 'advanced',
                'count': len(results),
                'filters_applied': filters,
                'results': results
            }, status=status.HTTP_200_OK)
        
        except ValueError as e:
            logger.error(f"Invalid parameters: {str(e)}")
            return Response({
                'success': False,
                'error': f'Invalid parameter: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Advanced search error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='stats')
    def search_stats(self, request):
        """
        Get search-related statistics
        GET /api/search/stats/
        """
        try:
            # Get user's tenant
            tenant_id = getattr(request.user, 'tenant_id', None)
            if not tenant_id:
                return Response({
                    'success': False,
                    'error': 'No tenant found'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get stats
            documents = Document.objects.filter(tenant_id=tenant_id).count()
            chunks = DocumentChunk.objects.filter(tenant_id=tenant_id).count()
            chunks_with_embeddings = DocumentChunk.objects.filter(
                tenant_id=tenant_id,
                embedding__isnull=False
            ).count()
            
            # Get clause stats
            try:
                metadata = DocumentMetadata.objects.filter(tenant_id=tenant_id)
                all_clauses = set()
                for m in metadata:
                    all_clauses.update(m.identified_clauses or [])
                
                clause_stats = {}
                for clause in all_clauses:
                    count = sum(1 for m in metadata if clause in (m.identified_clauses or []))
                    clause_stats[clause] = count
            except:
                clause_stats = {}
            
            return Response({
                'success': True,
                'stats': {
                    'total_documents': documents,
                    'total_chunks': chunks,
                    'chunks_with_embeddings': chunks_with_embeddings,
                    'embeddings_percentage': (chunks_with_embeddings / chunks * 100) if chunks > 0 else 0,
                    'clauses_found': clause_stats,
                    'unique_clause_types': len(clause_stats)
                }
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Stats error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
