#!/usr/bin/env python
"""
DEBUG: SEMANTIC SEARCH - Real Response Test
Tests the actual pgvector query and shows what's in the database
"""

import os
import sys
import django
import json
import numpy as np
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.db import connection
from repository.models import Document, DocumentChunk, DocumentMetadata
from rest_framework.test import APIClient
from authentication.models import User
from tenants.models import TenantModel
from rest_framework_simplejwt.tokens import RefreshToken


def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def print_section(text):
    print(f"\n{'-'*80}")
    print(f"  {text}")
    print(f"{'-'*80}\n")


def print_success(text):
    print(f"✅ {text}")


def print_error(text):
    print(f"❌ {text}")


def print_info(text):
    print(f"ℹ️  {text}")


def generate_mock_embedding(text, dimension=1024):
    """Generate deterministic mock embedding"""
    np.random.seed(hash(text) % (2**32))
    embedding = np.random.randn(dimension).astype(np.float32)
    embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
    return embedding.tolist()


# ============================================================================
# DEBUG TEST 1: Check Database Schema
# ============================================================================

def debug_database_schema():
    """Check if embedding column exists and is correct type"""
    print_section("DEBUG 1: DATABASE SCHEMA CHECK")
    
    try:
        with connection.cursor() as cursor:
            # Check DocumentChunk table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'repository_documentchunk'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print_success(f"Found {len(columns)} columns in repository_documentchunk")
            
            embedding_found = False
            for col_name, data_type, nullable in columns:
                if 'embed' in col_name.lower():
                    print_success(f"  {col_name}: {data_type} (nullable: {nullable})")
                    embedding_found = True
            
            if not embedding_found:
                print_error("  ❌ No embedding column found!")
                return False
            
            # Check if column is vector type
            cursor.execute("""
                SELECT column_name, udt_name
                FROM information_schema.columns
                WHERE table_name = 'repository_documentchunk'
                AND column_name = 'embedding';
            """)
            
            result = cursor.fetchone()
            if result:
                col_name, udt_type = result
                print_info(f"Column type: {udt_type}")
                if 'vector' in udt_type.lower():
                    print_success("✅ Column is vector type (pgvector)")
                else:
                    print_warning(f"Column type is {udt_type}, not vector")
            
        return True
        
    except Exception as e:
        print_error(f"Schema check error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# DEBUG TEST 2: Check Data in Database
# ============================================================================

def debug_database_content():
    """Check what's actually in the database"""
    print_section("DEBUG 2: DATABASE CONTENT CHECK")
    
    try:
        # Count documents
        doc_count = Document.objects.count()
        print_info(f"Total documents: {doc_count}")
        
        # Count chunks
        chunk_count = DocumentChunk.objects.count()
        print_info(f"Total chunks: {chunk_count}")
        
        # Count chunks with embeddings
        chunks_with_embed = DocumentChunk.objects.exclude(embedding__isnull=True).count()
        print_info(f"Chunks with embeddings: {chunks_with_embed}")
        
        if chunks_with_embed == 0:
            print_error("❌ No chunks have embeddings!")
            return False
        
        # Show sample chunk
        sample_chunk = DocumentChunk.objects.filter(embedding__isnull=False).first()
        if sample_chunk:
            print_success(f"Sample chunk found: {sample_chunk.id}")
            print_info(f"  Text: {sample_chunk.text[:80]}...")
            print_info(f"  Embedding type: {type(sample_chunk.embedding)}")
            if isinstance(sample_chunk.embedding, list):
                print_info(f"  Embedding length: {len(sample_chunk.embedding)}")
                print_info(f"  First 5 values: {sample_chunk.embedding[:5]}")
        
        return True
        
    except Exception as e:
        print_error(f"Content check error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# DEBUG TEST 3: Test Raw pgvector Query
# ============================================================================

def debug_pgvector_query():
    """Test the raw pgvector query directly"""
    print_section("DEBUG 3: PGVECTOR QUERY TEST")
    
    try:
        # Generate a test embedding
        query_text = "confidentiality and data protection"
        query_embedding = generate_mock_embedding(query_text)
        
        print_info(f"Query: {query_text}")
        print_info(f"Embedding dimensions: {len(query_embedding)}")
        
        # Convert to pgvector string format
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        print_info(f"Vector string length: {len(embedding_str)} chars")
        
        # Get a sample tenant
        tenant = TenantModel.objects.first()
        if not tenant:
            print_error("No tenant found in database")
            return False
        
        tenant_id = str(tenant.id)
        print_info(f"Using tenant: {tenant_id}")
        
        with connection.cursor() as cursor:
            # Test 1: Simple count query
            print_info("\n1. Testing chunk count with non-null embeddings...")
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM repository_documentchunk
                WHERE embedding IS NOT NULL
            """)
            count = cursor.fetchone()[0]
            print_info(f"   Chunks with embeddings: {count}")
            
            # Test 2: Try vector casting
            print_info("\n2. Testing vector type casting...")
            try:
                cursor.execute("""
                    SELECT '[-0.1, 0.2, 0.3]'::vector as test_vector
                """)
                result = cursor.fetchone()
                print_success(f"   Vector casting works: {result}")
            except Exception as e:
                print_error(f"   Vector casting failed: {str(e)}")
            
            # Test 3: Simple similarity query (no threshold)
            print_info("\n3. Testing similarity calculation...")
            try:
                query_sql = """
                SELECT 
                    id,
                    text,
                    embedding <=> %s::vector as distance,
                    1 - (embedding <=> %s::vector) as similarity
                FROM repository_documentchunk
                WHERE embedding IS NOT NULL
                LIMIT 5
                """
                
                cursor.execute(query_sql, [embedding_str, embedding_str])
                rows = cursor.fetchall()
                
                if rows:
                    print_success(f"   Query returned {len(rows)} results")
                    for i, row in enumerate(rows, 1):
                        chunk_id, text, distance, similarity = row
                        print_info(f"   Result {i}:")
                        print_info(f"     ID: {chunk_id}")
                        print_info(f"     Text: {text[:60]}...")
                        print_info(f"     Distance: {distance:.6f}")
                        print_info(f"     Similarity: {similarity:.6f}")
                else:
                    print_error("   Query returned no results")
                    
            except Exception as e:
                print_error(f"   Similarity query failed: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Test 4: Full semantic search query
            print_info("\n4. Testing full semantic search query...")
            try:
                query_sql = """
                SELECT 
                    dc.id,
                    dc.chunk_number,
                    dc.text,
                    d.filename,
                    1 - (dc.embedding <=> %s::vector) as similarity_score
                FROM repository_documentchunk dc
                JOIN repository_document d ON dc.document_id = d.id
                WHERE dc.tenant_id = %s 
                    AND dc.embedding IS NOT NULL
                ORDER BY similarity_score DESC
                LIMIT 10
                """
                
                cursor.execute(query_sql, [embedding_str, tenant_id])
                rows = cursor.fetchall()
                
                if rows:
                    print_success(f"   ✅ RESULTS FOUND: {len(rows)} chunks returned!")
                    for i, row in enumerate(rows, 1):
                        chunk_id, chunk_num, text, filename, similarity = row
                        print_success(f"   Result {i} (similarity: {similarity:.4f})")
                        print_info(f"     File: {filename}")
                        print_info(f"     Text: {text[:60]}...")
                else:
                    print_error("   ❌ No results returned from semantic search")
                
            except Exception as e:
                print_error(f"   Full query failed: {str(e)}")
                import traceback
                traceback.print_exc()
        
        return True
        
    except Exception as e:
        print_error(f"pgvector query error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# DEBUG TEST 4: Test via Service
# ============================================================================

def debug_search_service():
    """Test search service directly"""
    print_section("DEBUG 4: SEARCH SERVICE TEST")
    
    try:
        from repository.search_service import SemanticSearchService
        
        service = SemanticSearchService()
        print_success("SemanticSearchService initialized")
        
        # Get a tenant
        tenant = TenantModel.objects.first()
        if not tenant:
            print_error("No tenant found")
            return False
        
        tenant_id = str(tenant.id)
        
        # Perform search
        query = "confidentiality and data protection"
        print_info(f"Searching for: '{query}'")
        print_info(f"Tenant: {tenant_id}")
        
        results = service.semantic_search(
            query=query,
            tenant_id=tenant_id,
            top_k=5,
            threshold=0.3  # Lower threshold
        )
        
        print_info(f"Results returned: {len(results)}")
        
        if results:
            print_success(f"✅ SERVICE RETURNED {len(results)} RESULTS!")
            for i, result in enumerate(results, 1):
                print_success(f"  Result {i}:")
                print_info(f"    Similarity: {result.get('similarity_score', 'N/A'):.4f}")
                print_info(f"    Text: {result.get('text', '')[:60]}...")
        else:
            print_error("❌ Service returned no results")
        
        return len(results) > 0
        
    except Exception as e:
        print_error(f"Service test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# DEBUG TEST 5: Test via API
# ============================================================================

def debug_search_api():
    """Test search via REST API"""
    print_section("DEBUG 5: REST API TEST")
    
    try:
        # Get a user and token
        user = User.objects.first()
        if not user:
            print_error("No user found in database")
            return False
        
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        print_success(f"Created JWT token for user: {user.email}")
        
        # Create API client
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Call semantic search endpoint
        query = "confidentiality"
        response = client.get(f'/api/search/semantic/?q={query}&top_k=10&threshold=0.3')
        
        print_info(f"API Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            
            print_info(f"API returned: {count} results")
            
            if count > 0:
                print_success(f"✅ API RETURNED {count} RESULTS!")
                results = data.get('results', [])
                for i, result in enumerate(results[:3], 1):
                    print_success(f"  Result {i}:")
                    print_info(f"    Similarity: {result.get('similarity', 'N/A')}")
                    print_info(f"    Text: {result.get('text', '')[:60]}...")
                return True
            else:
                print_error("❌ API returned no results")
                return False
        else:
            print_error(f"API call failed with status {response.status_code}")
            print_info(f"Response: {response.json()}")
            return False
        
    except Exception as e:
        print_error(f"API test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    print_header("SEMANTIC SEARCH - DEBUG & FIX")
    print_info("Analyzing why semantic search returns 0 results")
    
    results = {}
    
    results['schema'] = debug_database_schema()
    results['content'] = debug_database_content()
    results['pgvector'] = debug_pgvector_query()
    results['service'] = debug_search_service()
    results['api'] = debug_search_api()
    
    print_header("DEBUG SUMMARY")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    if results['api']:
        print("\n" + "="*80)
        print("✅ ISSUE FIXED - SEMANTIC SEARCH NOW RETURNING REAL RESULTS!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("⚠️  ISSUE STILL EXISTS - See debug output above for next steps")
        print("="*80)


if __name__ == '__main__':
    main()
