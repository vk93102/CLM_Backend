"""
Search Views - Production Implementation
Real Voyage AI Integration + PostgreSQL FTS
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import time
import logging

from .services import (
    FullTextSearchService,
    SemanticSearchService,
    HybridSearchService,
    FilteringService,
    FacetedSearchService,
    SearchIndexingService,
    EmbeddingService,
    ModelConfig
)
from .serializers import SearchIndexSerializer
from .models import SearchIndexModel, SearchAnalyticsModel

logger = logging.getLogger(__name__)


class SearchKeywordView(APIView):
    """
    Full-Text Keyword Search
    Endpoint: GET /api/search/?q=query
    
    Strategy: PostgreSQL FTS + GIN Index
    Performance: O(log n) lookup
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Perform full-text keyword search
        
        Query Parameters:
            q (str): Search query
            limit (int, default=20): Results limit
            
        Response: Real results with metadata
        """
        start_time = time.time()
        
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 20))
        
        if not query or len(query) < 2:
            return Response({
                'error': 'Query must be at least 2 characters',
                'results': [],
                'count': 0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tenant_id = str(request.user.tenant_id)
        
        # Perform real full-text search
        results = FullTextSearchService.search(query, tenant_id, limit=limit)
        
        # Get formatted results with real data
        search_results = FullTextSearchService.get_search_metadata(results)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log analytics
        try:
            SearchAnalyticsModel.objects.create(
                tenant_id=tenant_id,
                user_id=str(request.user.id),
                query=query,
                query_type='full_text',
                results_count=len(search_results),
                response_time_ms=response_time_ms
            )
        except Exception as e:
            logger.warning(f"Analytics logging failed: {str(e)}")
        
        return Response({
            'query': query,
            'search_type': 'full_text',
            'results': search_results,
            'count': len(search_results),
            'response_time_ms': response_time_ms,
            'strategy': ModelConfig.FTS_STRATEGY,
            'success': True
        })


class SearchSemanticView(APIView):
    """
    Semantic Search using Voyage AI Embeddings
    Endpoint: GET /api/search/semantic/?q=query
    
    Model: voyage-law-2 (Legal documents specialist)
    Dimension: 1024
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Perform semantic search with real Voyage AI embeddings
        
        Query Parameters:
            q (str): Search query
            similarity_threshold (float, default=0.6): Min similarity
            limit (int, default=20): Results limit
            
        Response: Real results with Voyage AI embeddings
        """
        start_time = time.time()
        
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 20))
        threshold = float(request.query_params.get('similarity_threshold', 0.6))
        
        if not query:
            return Response({
                'error': 'Query parameter "q" is required',
                'results': [],
                'count': 0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tenant_id = str(request.user.tenant_id)
        
        try:
            # Step 1: Generate real query embedding using Voyage AI
            logger.info(f"Generating Voyage AI embedding for query: '{query}'")
            query_embedding = EmbeddingService.generate(query, input_type="query")
            
            if not query_embedding:
                logger.warning(f"Voyage AI embedding failed, falling back to keyword search")
                # Fallback to keyword search
                results = FullTextSearchService.search(query, tenant_id, limit=limit)
                search_results = FullTextSearchService.get_search_metadata(results)
            else:
                # Step 2: Perform semantic search
                logger.info(f"Performing semantic search with threshold={threshold}")
                results = SemanticSearchService.search(
                    query=query,
                    tenant_id=tenant_id,
                    similarity_threshold=threshold,
                    limit=limit
                )
                
                # Get formatted results with real embedding metadata
                search_results = SemanticSearchService.get_semantic_metadata(results)
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Log analytics
            try:
                SearchAnalyticsModel.objects.create(
                    tenant_id=tenant_id,
                    user_id=str(request.user.id),
                    query=query,
                    query_type='semantic',
                    results_count=len(search_results),
                    response_time_ms=response_time_ms
                )
            except Exception as e:
                logger.warning(f"Analytics logging failed: {str(e)}")
            
            return Response({
                'query': query,
                'search_type': 'semantic',
                'results': search_results,
                'count': len(search_results),
                'response_time_ms': response_time_ms,
                'strategy': ModelConfig.SEMANTIC_STRATEGY,
                'embedding_model': ModelConfig.VOYAGE_MODEL,
                'embedding_dimension': ModelConfig.VOYAGE_EMBEDDING_DIMENSION,
                'threshold': threshold,
                'success': True
            })
        
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return Response({
                'error': f'Semantic search failed: {str(e)}',
                'query': query,
                'results': [],
                'count': 0,
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchHybridView(APIView):
    """
    Hybrid Search combining FTS + Semantic
    Endpoint: POST /api/search/hybrid/
    
    Formula: 60% semantic + 30% FTS + 10% recency
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Perform hybrid search with real data
        
        Request Body:
            {
                'query': str,
                'limit': int (default=20)
            }
            
        Response: Real results from both strategies
        """
        start_time = time.time()
        
        query = request.data.get('query', '').strip()
        limit = request.data.get('limit', 20)
        
        if not query:
            return Response({
                'error': 'Query is required',
                'results': [],
                'count': 0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tenant_id = str(request.user.tenant_id)
        
        try:
            # Perform real hybrid search
            results = HybridSearchService.search(
                query=query,
                tenant_id=tenant_id,
                limit=limit
            )
            
            # Get formatted results
            search_results = HybridSearchService.get_hybrid_metadata(results)
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Log analytics
            try:
                SearchAnalyticsModel.objects.create(
                    tenant_id=tenant_id,
                    user_id=str(request.user.id),
                    query=query,
                    query_type='hybrid',
                    results_count=len(search_results),
                    response_time_ms=response_time_ms
                )
            except Exception as e:
                logger.warning(f"Analytics logging failed: {str(e)}")
            
            return Response({
                'query': query,
                'search_type': 'hybrid',
                'results': search_results,
                'count': len(search_results),
                'response_time_ms': response_time_ms,
                'strategy': ModelConfig.HYBRID_STRATEGY,
                'embedding_model': ModelConfig.VOYAGE_MODEL,
                'success': True
            })
        
        except Exception as e:
            logger.error(f"Hybrid search error: {str(e)}")
            return Response({
                'error': f'Hybrid search failed: {str(e)}',
                'results': [],
                'count': 0,
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchAdvancedView(APIView):
    """
    Advanced Search with Filters
    Endpoint: POST /api/search/advanced/
    
    Supports: Query + Multiple Filters
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Perform advanced filtered search with real data
        
        Request Body:
            {
                'query': str,
                'filters': {
                    'entity_type': str,
                    'keywords': List[str],
                    'status': str
                },
                'limit': int (default=20)
            }
        """
        try:
            query = request.data.get('query', '').strip()
            filters = request.data.get('filters', {})
            limit = request.data.get('limit', 20)
            
            tenant_id = str(request.user.tenant_id)
            
            # Get base search results
            if query:
                results = FullTextSearchService.search(query, tenant_id, limit=limit*2)
            else:
                results = list(SearchIndexModel.objects.filter(tenant_id=tenant_id))
            
            # Apply filters if provided
            if filters:
                filtered_results = FilteringService.apply_filters(results, filters)
                results = filtered_results[:limit]
            else:
                results = results[:limit]
            
            search_results = FullTextSearchService.get_search_metadata(results)
            
            return Response({
                'query': query,
                'search_type': 'advanced',
                'results': search_results,
                'count': len(search_results),
                'filters_applied': filters,
                'strategy': 'SQL WHERE + FTS',
                'success': True
            })
        
        except Exception as e:
            logger.error(f"Advanced search error: {str(e)}")
            return Response({
                'error': f'Advanced search failed: {str(e)}',
                'results': [],
                'count': 0,
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchFacetsView(APIView):
    """
    Faceted Search Navigation
    Endpoint: GET /api/search/facets/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get available search facets with real data"""
        tenant_id = str(request.user.tenant_id)
        
        facets = FacetedSearchService.get_facets(tenant_id)
        
        return Response({
            'facets': facets,
            'strategy': 'Aggregated SQL counts',
            'success': True
        })


class SearchFacetedView(APIView):
    """
    Faceted Search with Applied Facets
    Endpoint: POST /api/search/faceted/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Perform faceted search with real filtering"""
        try:
            query = request.data.get('query', '').strip()
            facet_filters = request.data.get('facet_filters', {})
            limit = request.data.get('limit', 20)
            
            tenant_id = str(request.user.tenant_id)
            
            # Start with search results
            if query:
                results = FullTextSearchService.search(query, tenant_id, limit=limit*2)
            else:
                results = list(SearchIndexModel.objects.filter(tenant_id=tenant_id))
            
            # Apply facet filters
            results = FacetedSearchService.apply_facet_filters(results, facet_filters)
            results = results[:limit]
            
            search_results = FullTextSearchService.get_search_metadata(results)
            
            # Get available facets
            available_facets = FacetedSearchService.get_facets(tenant_id)
            
            return Response({
                'results': search_results,
                'count': len(search_results),
                'applied_facets': facet_filters,
                'available_facets': available_facets,
                'strategy': 'Faceted Navigation',
                'success': True
            })
        
        except Exception as e:
            logger.error(f"Faceted search error: {str(e)}")
            return Response({
                'error': f'Faceted search failed: {str(e)}',
                'results': [],
                'count': 0,
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchSuggestionsView(APIView):
    """
    Search Suggestions and Autocomplete
    Endpoint: GET /api/search/suggestions/?q=query
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get real search suggestions based on indexed content"""
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 5))
        
        tenant_id = str(request.user.tenant_id)
        
        if not query or len(query) < 2:
            return Response({'suggestions': [], 'count': 0})
        
        # Get real matching suggestions
        suggestions = SearchIndexModel.objects.filter(
            tenant_id=tenant_id,
            title__istartswith=query
        ).values_list('title', flat=True).distinct()[:limit]
        
        return Response({
            'query': query,
            'suggestions': list(suggestions),
            'count': len(suggestions),
            'success': True
        })


class SearchIndexingView(APIView):
    """
    Search Index Management
    Endpoints:
        POST /api/search/index/ - Create/update index
        DELETE /api/search/index/{entity_id}/ - Delete index
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Create or update search index with real data
        
        Request Body:
            {
                'entity_type': str,
                'entity_id': UUID,
                'title': str,
                'content': str,
                'keywords': List[str] (optional)
            }
        """
        data = request.data
        tenant_id = str(request.user.tenant_id)
        
        required_fields = ['entity_type', 'entity_id', 'title', 'content']
        if not all(field in data for field in required_fields):
            return Response({
                'success': False,
                'message': f'Missing required fields: {required_fields}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            index_entry, created = SearchIndexingService.create_index(
                entity_type=data['entity_type'],
                entity_id=data['entity_id'],
                title=data['title'],
                content=data['content'],
                tenant_id=tenant_id,
                keywords=data.get('keywords', [])
            )
            
            return Response({
                'success': True,
                'message': 'Index created' if created else 'Index updated',
                'index_id': str(index_entry.id)
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Index creation error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchAnalyticsView(APIView):
    """
    Search Analytics and Metrics
    Endpoint: GET /api/search/analytics/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get real search analytics with actual data"""
        tenant_id = str(request.user.tenant_id)
        
        try:
            analytics = SearchAnalyticsModel.objects.filter(tenant_id=tenant_id)
            
            # Group by query type with real data
            by_type = {}
            for query_type in ['full_text', 'semantic', 'hybrid', 'advanced']:
                type_analytics = analytics.filter(query_type=query_type)
                count = type_analytics.count()
                if count > 0:
                    from django.db.models import Avg
                    avg_time = type_analytics.aggregate(avg=Avg('response_time_ms'))['avg'] or 0
                    by_type[query_type] = {
                        'count': count,
                        'avg_response_time_ms': float(avg_time)
                    }
            
            from django.db.models import Avg
            total_avg = analytics.aggregate(avg=Avg('response_time_ms'))['avg'] or 0
            
            return Response({
                'total_searches': analytics.count(),
                'by_type': by_type,
                'avg_response_time_ms': float(total_avg),
                'success': True
            })
        
        except Exception as e:
            logger.error(f"Analytics error: {str(e)}")
            return Response({
                'error': str(e),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    permission_classes = [IsAuthenticated]
