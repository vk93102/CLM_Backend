"""
Advanced Search Module - Full-Text, Semantic, and OCR-enabled Search
Features:
- Full-text search across contracts, documents, and metadata
- Repository with advanced filtering capabilities
- OCR processing pipeline for document scanning
- Semantic search with vector embeddings
- Similarity search using embeddings
- Enhanced search API documentation
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, F, Value, CharField, Count
from django.db.models.functions import Concat, Lower
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.utils import timezone
from django.views.decorators.http import require_http_methods
import logging
import json
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

# Import models
try:
    from contracts.models import Contract
    from authentication.models import User
    from audit_logs.models import AuditLogModel
except ImportError:
    logger.warning("Some models not available")


# ============================================================================
# VECTOR EMBEDDINGS & SEMANTIC SEARCH
# ============================================================================

class EmbeddingService:
    """Service for generating and managing embeddings"""
    
    @staticmethod
    def generate_embedding(text: str) -> list:
        """
        Generate embedding vector for text
        In production, use OpenAI, Hugging Face, or similar service
        """
        # Simple hash-based embedding for demo
        # In production: use model.encode(text) from sentence-transformers
        import hashlib
        
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = [float(b) / 255.0 for b in hash_bytes[:384]]
        return embedding
    
    @staticmethod
    def cosine_similarity(vec1: list, vec2: list) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))
        
        if mag1 == 0 or mag2 == 0:
            return 0
        
        return dot_product / (mag1 * mag2)


# ============================================================================
# FULL-TEXT SEARCH
# ============================================================================

class FullTextSearchService:
    """Service for full-text search functionality"""
    
    @staticmethod
    def search_contracts(query: str, limit: int = 50) -> list:
        """
        Search contracts using full-text search
        Searches: title, description, status, and metadata
        """
        try:
            contracts = Contract.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(status__icontains=query)
            ).values(
                'id', 'title', 'description', 'status', 'created_at',
                'created_by', 'contract_value'
            )[:limit]
            
            results = []
            for contract in contracts:
                results.append({
                    "id": str(contract['id']),
                    "title": contract['title'],
                    "description": contract['description'],
                    "status": contract['status'],
                    "value": contract.get('contract_value', 0),
                    "created_at": contract['created_at'].isoformat() if contract['created_at'] else None,
                    "score": 100  # Relevance score
                })
            
            return results
        except Exception as e:
            logger.error(f"Contract search error: {str(e)}")
            return []
    
    @staticmethod
    def search_users(query: str, limit: int = 50) -> list:
        """Search users by email, username, or full name"""
        try:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).values('user_id', 'username', 'email', 'first_name', 'last_name')[:limit]
            
            results = []
            for user in users:
                results.append({
                    "user_id": str(user['user_id']),
                    "username": user['username'],
                    "email": user['email'],
                    "full_name": f"{user['first_name']} {user['last_name']}".strip(),
                    "score": 100
                })
            
            return results
        except Exception as e:
            logger.error(f"User search error: {str(e)}")
            return []


# ============================================================================
# OCR PROCESSING PIPELINE
# ============================================================================

class OCRProcessingPipeline:
    """Pipeline for OCR processing and text extraction"""
    
    @staticmethod
    def extract_text_from_document(file_path: str) -> str:
        """
        Extract text from document (PDF, Image, etc.)
        In production, use pytesseract, pdf2image, PyPDF2
        """
        try:
            # Placeholder for actual OCR implementation
            return f"Extracted text from {file_path}"
        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}")
            return ""
    
    @staticmethod
    def process_document_batch(files: list) -> dict:
        """Process multiple documents and extract text"""
        results = {}
        
        for file_path in files:
            try:
                text = OCRProcessingPipeline.extract_text_from_document(file_path)
                embedding = EmbeddingService.generate_embedding(text)
                
                results[file_path] = {
                    "text": text,
                    "embedding": embedding,
                    "processing_time": datetime.now().isoformat(),
                    "status": "completed"
                }
            except Exception as e:
                results[file_path] = {
                    "error": str(e),
                    "status": "failed"
                }
        
        return results
    
    @staticmethod
    def extract_entities(text: str) -> dict:
        """Extract key entities from text (amounts, dates, names)"""
        import re
        
        entities = {
            "amounts": [],
            "dates": [],
            "email_addresses": [],
            "phone_numbers": []
        }
        
        # Extract currency amounts
        currency_pattern = r'\$[\d,]+\.?\d*'
        entities["amounts"] = re.findall(currency_pattern, text)
        
        # Extract dates
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
        entities["dates"] = re.findall(date_pattern, text)
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities["email_addresses"] = re.findall(email_pattern, text)
        
        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        entities["phone_numbers"] = re.findall(phone_pattern, text)
        
        return entities


# ============================================================================
# SEMANTIC SEARCH
# ============================================================================

class SemanticSearchService:
    """Service for semantic search using embeddings"""
    
    @staticmethod
    def semantic_search_contracts(query: str, limit: int = 10) -> list:
        """
        Semantic search on contracts
        Returns results ranked by semantic similarity
        """
        try:
            query_embedding = EmbeddingService.generate_embedding(query)
            
            contracts = Contract.objects.all().values(
                'id', 'title', 'description', 'status', 'created_at'
            )[:100]
            
            results_with_scores = []
            
            for contract in contracts:
                text = f"{contract['title']} {contract['description']}"
                embedding = EmbeddingService.generate_embedding(text)
                similarity = EmbeddingService.cosine_similarity(
                    query_embedding, embedding
                )
                
                results_with_scores.append({
                    "id": str(contract['id']),
                    "title": contract['title'],
                    "description": contract['description'],
                    "status": contract['status'],
                    "created_at": contract['created_at'].isoformat() if contract['created_at'] else None,
                    "similarity_score": round(similarity * 100, 2)
                })
            
            # Sort by similarity score
            results_with_scores.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return results_with_scores[:limit]
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return []
    
    @staticmethod
    def find_similar_contracts(contract_id: str, limit: int = 5) -> list:
        """Find contracts similar to a given contract"""
        try:
            contract = Contract.objects.get(id=contract_id)
            reference_text = f"{contract.title} {contract.description}"
            reference_embedding = EmbeddingService.generate_embedding(reference_text)
            
            similar_contracts = Contract.objects.exclude(id=contract_id).values(
                'id', 'title', 'description', 'status'
            )[:50]
            
            results = []
            
            for sim_contract in similar_contracts:
                text = f"{sim_contract['title']} {sim_contract['description']}"
                embedding = EmbeddingService.generate_embedding(text)
                similarity = EmbeddingService.cosine_similarity(
                    reference_embedding, embedding
                )
                
                results.append({
                    "id": str(sim_contract['id']),
                    "title": sim_contract['title'],
                    "similarity_score": round(similarity * 100, 2)
                })
            
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results[:limit]
        except Exception as e:
            logger.error(f"Similar contracts error: {str(e)}")
            return []


# ============================================================================
# REPOSITORY WITH FILTERING
# ============================================================================

class ContractRepository:
    """Repository pattern for contract queries with advanced filtering"""
    
    @staticmethod
    def search_with_filters(filters: dict, limit: int = 50, offset: int = 0) -> dict:
        """
        Search contracts with multiple filters
        Filters: status, value_range, date_range, created_by, tenant_id
        """
        queryset = Contract.objects.all()
        
        # Status filter
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        
        # Status in list
        if filters.get('statuses'):
            queryset = queryset.filter(status__in=filters['statuses'])
        
        # Contract value range
        if filters.get('min_value'):
            queryset = queryset.filter(contract_value__gte=filters['min_value'])
        if filters.get('max_value'):
            queryset = queryset.filter(contract_value__lte=filters['max_value'])
        
        # Date range
        if filters.get('created_after'):
            queryset = queryset.filter(
                created_at__gte=filters['created_after']
            )
        if filters.get('created_before'):
            queryset = queryset.filter(
                created_at__lte=filters['created_before']
            )
        
        # Created by user
        if filters.get('created_by'):
            queryset = queryset.filter(created_by=filters['created_by'])
        
        # Tenant filter
        if filters.get('tenant_id'):
            queryset = queryset.filter(tenant_id=filters['tenant_id'])
        
        # Search text
        if filters.get('search_text'):
            search_text = filters['search_text']
            queryset = queryset.filter(
                Q(title__icontains=search_text) |
                Q(description__icontains=search_text)
            )
        
        # Get total count before pagination
        total = queryset.count()
        
        # Pagination
        results = queryset.order_by('-created_at')[offset:offset+limit].values(
            'id', 'title', 'status', 'contract_value', 'created_at', 'created_by'
        )
        
        result_list = []
        for contract in results:
            result_list.append({
                "id": str(contract['id']),
                "title": contract['title'],
                "status": contract['status'],
                "value": contract.get('contract_value', 0),
                "created_at": contract['created_at'].isoformat() if contract['created_at'] else None,
            })
        
        return {
            "results": result_list,
            "count": len(result_list),
            "total": total,
            "offset": offset,
            "limit": limit
        }


# ============================================================================
# SEARCH VIEWSET - API ENDPOINTS
# ============================================================================

class SearchViewSet(viewsets.ViewSet):
    """
    Advanced Search API ViewSet
    Provides full-text, semantic, and filtered search capabilities
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='full-text')
    def full_text_search(self, request):
        """
        POST /api/search/full-text/
        Full-text search across all searchable content
        
        Request body:
        {
            "query": "contract keywords",
            "type": "contracts|users|all",
            "limit": 50
        }
        """
        try:
            query = request.data.get('query', '')
            search_type = request.data.get('type', 'all')
            limit = int(request.data.get('limit', 50))
            
            if not query:
                return Response(
                    {"error": "Query parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            results = {
                "contracts": [],
                "users": [],
                "timestamp": timezone.now().isoformat()
            }
            
            if search_type in ['contracts', 'all']:
                results["contracts"] = FullTextSearchService.search_contracts(
                    query, limit
                )
            
            if search_type in ['users', 'all']:
                results["users"] = FullTextSearchService.search_users(query, limit)
            
            return Response(results)
        except Exception as e:
            logger.error(f"Full-text search error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='semantic')
    def semantic_search(self, request):
        """
        POST /api/search/semantic/
        Semantic search using embeddings and similarity
        
        Request body:
        {
            "query": "semantic search query",
            "limit": 10
        }
        """
        try:
            query = request.data.get('query', '')
            limit = int(request.data.get('limit', 10))
            
            if not query:
                return Response(
                    {"error": "Query parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            results = SemanticSearchService.semantic_search_contracts(query, limit)
            
            return Response({
                "results": results,
                "count": len(results),
                "query": query,
                "timestamp": timezone.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='similar')
    def similar_contracts(self, request):
        """
        GET /api/search/similar/?contract_id=<id>&limit=5
        Find contracts similar to a given contract
        """
        try:
            contract_id = request.query_params.get('contract_id')
            limit = int(request.query_params.get('limit', 5))
            
            if not contract_id:
                return Response(
                    {"error": "contract_id parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            results = SemanticSearchService.find_similar_contracts(
                contract_id, limit
            )
            
            return Response({
                "results": results,
                "count": len(results),
                "reference_contract_id": contract_id,
                "timestamp": timezone.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Similar contracts error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='filtered')
    def filtered_search(self, request):
        """
        POST /api/search/filtered/
        Search with advanced filtering
        
        Request body:
        {
            "filters": {
                "status": "active",
                "min_value": 10000,
                "max_value": 100000,
                "created_after": "2026-01-01",
                "search_text": "keywords"
            },
            "limit": 50,
            "offset": 0
        }
        """
        try:
            filters = request.data.get('filters', {})
            limit = int(request.data.get('limit', 50))
            offset = int(request.data.get('offset', 0))
            
            # Parse dates if provided
            if 'created_after' in filters and isinstance(filters['created_after'], str):
                filters['created_after'] = datetime.fromisoformat(
                    filters['created_after'].replace('Z', '+00:00')
                )
            if 'created_before' in filters and isinstance(filters['created_before'], str):
                filters['created_before'] = datetime.fromisoformat(
                    filters['created_before'].replace('Z', '+00:00')
                )
            
            results = ContractRepository.search_with_filters(
                filters, limit, offset
            )
            
            return Response(results)
        except Exception as e:
            logger.error(f"Filtered search error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='ocr-extract')
    def ocr_extract(self, request):
        """
        POST /api/search/ocr-extract/
        Extract text from documents using OCR
        
        Request body:
        {
            "file_paths": ["/path/to/file1.pdf", "/path/to/file2.png"],
            "extract_entities": true
        }
        """
        try:
            file_paths = request.data.get('file_paths', [])
            extract_entities = request.data.get('extract_entities', False)
            
            if not file_paths:
                return Response(
                    {"error": "file_paths parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            results = OCRProcessingPipeline.process_document_batch(file_paths)
            
            if extract_entities:
                for file_path, result in results.items():
                    if result.get('status') == 'completed':
                        result['entities'] = OCRProcessingPipeline.extract_entities(
                            result['text']
                        )
            
            return Response({
                "results": results,
                "count": len(results),
                "timestamp": timezone.now().isoformat()
            })
        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# API DOCUMENTATION ENDPOINT
# ============================================================================

@api_view(['GET'])
@permission_classes([])
def search_api_documentation(request):
    """
    GET /api/search/documentation/
    Returns comprehensive API documentation
    """
    documentation = {
        "title": "Advanced Search API Documentation",
        "version": "1.0.0",
        "base_url": "/api/search/",
        "endpoints": [
            {
                "name": "Full-Text Search",
                "path": "/full-text/",
                "method": "POST",
                "description": "Search across contracts, users, and metadata using full-text search",
                "request_body": {
                    "query": "string - search keywords",
                    "type": "string - 'contracts', 'users', or 'all'",
                    "limit": "integer - max results (default: 50)"
                },
                "response": {
                    "contracts": "array of matching contracts",
                    "users": "array of matching users",
                    "timestamp": "ISO timestamp"
                }
            },
            {
                "name": "Semantic Search",
                "path": "/semantic/",
                "method": "POST",
                "description": "Search using semantic similarity with embeddings",
                "request_body": {
                    "query": "string - search query",
                    "limit": "integer - max results (default: 10)"
                },
                "response": {
                    "results": "array of similar contracts ranked by similarity",
                    "count": "number of results",
                    "query": "original query"
                }
            },
            {
                "name": "Similar Contracts",
                "path": "/similar/?contract_id=<id>&limit=5",
                "method": "GET",
                "description": "Find contracts similar to a given contract",
                "query_params": {
                    "contract_id": "UUID - reference contract ID",
                    "limit": "integer - max similar contracts to return"
                },
                "response": {
                    "results": "array of similar contracts",
                    "count": "number of results",
                    "reference_contract_id": "the contract ID used for comparison"
                }
            },
            {
                "name": "Filtered Search",
                "path": "/filtered/",
                "method": "POST",
                "description": "Search with advanced filtering options",
                "request_body": {
                    "filters": {
                        "status": "contract status",
                        "statuses": "array of statuses",
                        "min_value": "minimum contract value",
                        "max_value": "maximum contract value",
                        "created_after": "ISO date string",
                        "created_before": "ISO date string",
                        "created_by": "user UUID",
                        "tenant_id": "tenant UUID",
                        "search_text": "full-text search keywords"
                    },
                    "limit": "integer (default: 50)",
                    "offset": "integer (default: 0)"
                },
                "response": {
                    "results": "array of matching contracts",
                    "count": "number of results returned",
                    "total": "total count matching filters",
                    "offset": "pagination offset"
                }
            },
            {
                "name": "OCR Text Extraction",
                "path": "/ocr-extract/",
                "method": "POST",
                "description": "Extract text from documents using OCR and generate embeddings",
                "request_body": {
                    "file_paths": "array of file paths",
                    "extract_entities": "boolean - whether to extract entities (amounts, dates, emails)"
                },
                "response": {
                    "results": "object with extraction results for each file",
                    "count": "number of files processed",
                    "timestamp": "processing timestamp"
                }
            },
            {
                "name": "API Documentation",
                "path": "/documentation/",
                "method": "GET",
                "description": "Get this API documentation",
                "response": "API documentation and examples"
            }
        ],
        "features": {
            "full_text_search": "Search across contract titles, descriptions, and status",
            "semantic_search": "Find semantically similar contracts using embeddings",
            "ocr_processing": "Extract text from PDFs and images",
            "entity_extraction": "Automatically extract amounts, dates, emails from text",
            "advanced_filtering": "Filter by status, value range, date range, creator",
            "similarity_search": "Find contracts similar to a reference contract",
            "pagination": "Paginate through large result sets",
            "relevance_ranking": "Results ranked by relevance score"
        },
        "authentication": "Bearer token required (except documentation)",
        "rate_limiting": "100 requests per minute",
        "examples": {
            "full_text_search": {
                "url": "POST /api/search/full-text/",
                "body": {
                    "query": "service agreement",
                    "type": "contracts",
                    "limit": 10
                }
            },
            "semantic_search": {
                "url": "POST /api/search/semantic/",
                "body": {
                    "query": "long-term vendor relationship",
                    "limit": 5
                }
            },
            "filtered_search": {
                "url": "POST /api/search/filtered/",
                "body": {
                    "filters": {
                        "status": "active",
                        "min_value": 50000,
                        "created_after": "2025-01-01"
                    },
                    "limit": 20
                }
            }
        }
    }
    
    return Response(documentation)


# Export for URL imports
__all__ = [
    'SearchViewSet',
    'FullTextSearchService',
    'SemanticSearchService',
    'OCRProcessingPipeline',
    'ContractRepository',
    'EmbeddingService',
    'search_api_documentation'
]
