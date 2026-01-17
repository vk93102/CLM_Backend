"""
Semantic Search Service
Performs vector similarity search across document chunks
"""
import logging
from typing import List, Dict, Optional
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import F, Q
from repository.models import DocumentChunk, Document
from repository.embeddings_service import VoyageEmbeddingsService
from tenants.models import TenantModel

logger = logging.getLogger(__name__)


class SemanticSearchService:
    """Service for semantic search using pgvector"""
    
    def __init__(self):
        """Initialize search service"""
        self.embeddings_service = VoyageEmbeddingsService()
    
    def semantic_search(
        self,
        query: str,
        tenant_id: str,
        top_k: int = 10,
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Perform semantic search across document chunks
        
        Args:
            query: Search query text
            tenant_id: Tenant UUID for isolation
            top_k: Number of results to return
            threshold: Similarity threshold (0-1)
        
        Returns:
            List of top matching chunks with scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embeddings_service.embed_query(query)
            
            if query_embedding is None:
                logger.warning("Failed to generate query embedding, falling back to keyword search")
                return self.keyword_search(query, tenant_id, top_k)
            
            # Perform vector similarity search using cosine similarity
            logger.info(f"Performing semantic search for query: '{query}' with threshold={threshold}")
            
            results = []
            
            try:
                # Method: Use Django ORM with Python-side similarity calculation
                # Since embeddings are stored as arrays, not pgvector type
                
                # Get all chunks with embeddings for this tenant
                chunks = DocumentChunk.objects.filter(
                    document__tenant_id=tenant_id,
                    embedding__isnull=False
                ).select_related('document')
                
                chunk_count = chunks.count()
                logger.info(f"Found {chunk_count} chunks for tenant {tenant_id} with embeddings")
                
                # Calculate cosine similarity for each chunk
                import numpy as np
                query_vec = np.array(query_embedding, dtype=np.float32)
                query_norm = np.linalg.norm(query_vec)
                
                chunk_scores = []
                
                for chunk in chunks:
                    try:
                        # Convert chunk embedding to numpy array
                        chunk_vec = np.array(chunk.embedding, dtype=np.float32)
                        chunk_norm = np.linalg.norm(chunk_vec)
                        
                        # Calculate cosine similarity
                        if chunk_norm > 0 and query_norm > 0:
                            similarity = np.dot(query_vec, chunk_vec) / (query_norm * chunk_norm)
                        else:
                            similarity = 0.0
                        
                        # Filter by threshold
                        if similarity > threshold:
                            chunk_scores.append({
                                'chunk': chunk,
                                'similarity': float(similarity)
                            })
                    except Exception as e:
                        logger.warning(f"Error calculating similarity for chunk {chunk.id}: {str(e)}")
                        continue
                
                # Sort by similarity (descending) and limit
                chunk_scores.sort(key=lambda x: x['similarity'], reverse=True)
                chunk_scores = chunk_scores[:top_k]
                
                logger.info(f"Semantic search returned {len(chunk_scores)} results above threshold {threshold}")
                if chunk_scores:
                    top_sim = chunk_scores[0]['similarity']
                    logger.info(f"Top similarity score: {top_sim:.6f}")
                
                # Format results
                for item in chunk_scores:
                    chunk = item['chunk']
                    similarity = item['similarity']
                    
                    results.append({
                        'chunk_id': str(chunk.id),
                        'chunk_number': chunk.chunk_number,
                        'text': chunk.text,  # Return full text
                        'document_id': str(chunk.document_id),
                        'filename': chunk.document.filename,
                        'document_type': chunk.document.document_type,
                        'similarity': similarity,
                        'similarity_score': similarity,
                        'source': 'semantic'
                    })
                
                logger.info(f"Returning {len(results)} formatted semantic search results")
                return results
            
            except Exception as e:
                logger.error(f"Vector search error: {str(e)}, falling back to keyword search")
                return self.keyword_search(query, tenant_id, top_k)
        
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return []
    
    def keyword_search(
        self,
        query: str,
        tenant_id: str,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Perform traditional keyword search
        
        Args:
            query: Search query text
            tenant_id: Tenant UUID
            top_k: Number of results to return
        
        Returns:
            List of matching chunks
        """
        try:
            logger.info(f"Performing keyword search for query: {query}")
            
            # Use Django ORM with icontains for keyword matching
            chunks = DocumentChunk.objects.filter(
                tenant_id=tenant_id,
                text__icontains=query
            ).select_related('document').order_by('document_id', 'chunk_number')[:top_k]
            
            results = []
            for chunk in chunks:
                results.append({
                    'chunk_id': str(chunk.id),
                    'chunk_number': chunk.chunk_number,
                    'text': chunk.text[:500],
                    'document_id': str(chunk.document_id),
                    'filename': chunk.document.filename,
                    'document_type': chunk.document.document_type,
                    'similarity_score': None,  # No score for keyword search
                    'source': 'keyword'
                })
            
            logger.info(f"Found {len(results)} keyword search results")
            return results
        
        except Exception as e:
            logger.error(f"Keyword search failed: {str(e)}")
            return []
    
    def hybrid_search(
        self,
        query: str,
        tenant_id: str,
        top_k: int = 10,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict]:
        """
        Perform hybrid search combining semantic and keyword results
        
        Args:
            query: Search query
            tenant_id: Tenant UUID
            top_k: Number of results to return
            semantic_weight: Weight for semantic results (0-1)
            keyword_weight: Weight for keyword results (0-1)
        
        Returns:
            Combined ranked results
        """
        try:
            logger.info(f"Performing hybrid search for query: {query}")
            
            # Get semantic results
            semantic_results = self.semantic_search(query, tenant_id, top_k * 2, threshold=0.3)
            
            # Get keyword results
            keyword_results = self.keyword_search(query, tenant_id, top_k * 2)
            
            # Combine and deduplicate
            result_map = {}
            
            # Add semantic results
            for result in semantic_results:
                chunk_id = result['chunk_id']
                result['combined_score'] = (result['similarity_score'] or 0) * semantic_weight
                result_map[chunk_id] = result
            
            # Add/merge keyword results
            for i, result in enumerate(keyword_results):
                chunk_id = result['chunk_id']
                keyword_score = (1.0 - (i / len(keyword_results))) * keyword_weight if keyword_results else 0
                
                if chunk_id in result_map:
                    # Merge scores
                    result_map[chunk_id]['combined_score'] += keyword_score
                    result_map[chunk_id]['source'] = 'hybrid'
                else:
                    result['combined_score'] = keyword_score
                    result_map[chunk_id] = result
            
            # Sort by combined score
            final_results = sorted(
                result_map.values(),
                key=lambda x: x['combined_score'],
                reverse=True
            )[:top_k]
            
            logger.info(f"Hybrid search returned {len(final_results)} results")
            return final_results
        
        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")
            return []
    
    def search_by_clause(
        self,
        clause_type: str,
        tenant_id: str,
        top_k: int = 20
    ) -> List[Dict]:
        """
        Search for specific clause types
        
        Args:
            clause_type: Type of clause (Confidentiality, Termination, etc.)
            tenant_id: Tenant UUID
            top_k: Number of results
        
        Returns:
            Chunks matching the clause type
        """
        try:
            logger.info(f"Searching for {clause_type} clauses")
            
            # Search chunks and document metadata for clause type
            from repository.models import DocumentMetadata
            
            # Find documents with this clause type
            documents_with_clause = DocumentMetadata.objects.filter(
                tenant_id=tenant_id,
                identified_clauses__contains=[clause_type]
            ).values_list('document_id', flat=True)
            
            # Get chunks from those documents
            chunks = DocumentChunk.objects.filter(
                document_id__in=documents_with_clause,
                tenant_id=tenant_id,
                text__icontains=clause_type.lower()
            ).select_related('document').order_by('document_id', 'chunk_number')[:top_k]
            
            results = []
            for chunk in chunks:
                results.append({
                    'chunk_id': str(chunk.id),
                    'chunk_number': chunk.chunk_number,
                    'text': chunk.text[:500],
                    'document_id': str(chunk.document_id),
                    'filename': chunk.document.filename,
                    'clause_type': clause_type,
                    'source': 'clause_search'
                })
            
            logger.info(f"Found {len(results)} {clause_type} clauses")
            return results
        
        except Exception as e:
            logger.error(f"Clause search failed: {str(e)}")
            return []
    
    def advanced_search(
        self,
        query: str,
        tenant_id: str,
        filters: dict = None,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Advanced search with filters on document metadata
        
        Args:
            query: Search query text
            tenant_id: Tenant UUID for isolation
            filters: Dictionary of filters (document_type, etc.)
            top_k: Number of results to return
        
        Returns:
            List of matching chunks with filters applied
        """
        try:
            filters = filters or {}
            
            # Start with keyword search
            results = self.keyword_search(
                query=query,
                tenant_id=tenant_id,
                top_k=top_k * 2  # Get more results to apply filters
            )
            
            # Apply filters
            filtered_results = []
            for result in results:
                match = True
                
                # Check document_type filter
                if 'document_type' in filters:
                    doc_type = filters['document_type'].lower()
                    result_type = result.get('document_type', '').lower()
                    if doc_type not in result_type:
                        match = False
                
                # Check filename filter
                if match and 'filename' in filters:
                    filename = filters['filename'].lower()
                    result_filename = result.get('filename', '').lower()
                    if filename not in result_filename:
                        match = False
                
                if match:
                    filtered_results.append(result)
                    if len(filtered_results) >= top_k:
                        break
            
            logger.info(f"Advanced search: query='{query}', found {len(filtered_results)} results with filters {filters}")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Advanced search failed: {str(e)}")
            return []
            return []
