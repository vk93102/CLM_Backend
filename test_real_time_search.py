#!/usr/bin/env python
"""
Real-Time Semantic Search System Test
Tests complete pipeline with actual Voyage AI embeddings and pgvector searches
Production-level verification with comprehensive error handling
"""
import os
import sys
import django
import json
import time
from io import BytesIO
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import TenantModel
from repository.models import Document, DocumentChunk, DocumentMetadata
from repository.embeddings_service import VoyageEmbeddingsService
from repository.search_service import SemanticSearchService
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import connection

User = get_user_model()

# Sample contract with diverse content for testing
SAMPLE_CONTRACT = """
SERVICE AGREEMENT - CONFIDENTIALITY AND LIABILITY TERMS

This Service Agreement ("Agreement") is entered into as of January 17, 2026, between ABC Corporation 
("Client") and XYZ Solutions Inc. ("Provider").

1. CONFIDENTIAL INFORMATION
Both parties agree to maintain strict confidentiality of proprietary information including:
- Technical specifications and architecture
- Customer lists and contact information
- Pricing models and financial data
- Business strategies and expansion plans
- Source code and algorithms
- Trade secrets and intellectual property

Confidential information shall not be disclosed to third parties without written consent. 
Violations will result in immediate termination and legal action.

2. LIABILITY LIMITATIONS
Neither party shall be liable for:
- Indirect damages or lost profits
- Incidental or consequential damages
- Data loss exceeding the service fee
- Performance interruptions beyond reasonable control

Maximum liability is limited to fees paid in the preceding 12 months.
Provider assumes no liability for user misuse or unauthorized access.

3. PAYMENT TERMS
- Monthly service fee: $50,000
- Payment due within 15 days of invoice
- Late payments accrue 1.5% monthly interest
- Automatic renewal unless 30-day notice provided
- Penalties for non-payment: 10% additional charges

4. SERVICE TERMINATION
Either party may terminate with 30 days written notice.
Upon termination:
- All services cease immediately
- Client must return proprietary materials
- Outstanding invoices become due
- Confidentiality obligations continue

5. INTELLECTUAL PROPERTY RIGHTS
All deliverables created shall be:
- Work product and property of Client
- Subject to Client's exclusive ownership
- Free from third-party encumbrances
- Covered by 12-month warranty period

6. DISPUTE RESOLUTION
Disputes shall be resolved through:
1. Good faith negotiation (15 days)
2. Binding arbitration if negotiation fails
3. American Arbitration Association rules apply
4. Prevailing party recovers attorney fees

7. GENERAL PROVISIONS
- Agreement constitutes entire understanding
- Modifications require written signature
- Severability: invalid provisions don't void agreement
- Governing law: State law applies
- Effective date: January 17, 2026

Signatures:
Client: _________________ Date: _________
Provider: _________________ Date: _________
"""

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def get_token_for_user(user):
    """Generate JWT token for user"""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def test_voyage_ai_connection():
    """Test direct connection to Voyage AI"""
    print_header("TEST 1: VOYAGE AI CONNECTION")
    
    service = VoyageEmbeddingsService()
    
    if not service.is_available():
        print_error("Voyage AI not configured")
        return False
    
    print_success("Voyage AI API configured")
    
    # Test embedding generation
    test_text = "This is a test of liability clauses in service agreements"
    try:
        embedding = service.embed_text(test_text)
        if embedding and len(embedding) == 1024:
            print_success(f"Embedding generated: {len(embedding)} dimensions")
            print_info(f"First 5 values: {[f'{v:.6f}' for v in embedding[:5]]}")
            print_info(f"Last 5 values: {[f'{v:.6f}' for v in embedding[-5:]]}")
            return True
        else:
            print_error(f"Invalid embedding dimensions: {len(embedding) if embedding else 'None'}")
            if embedding:
                print_info(f"Received {len(embedding)} dimensions instead of 1024")
            return False
    except Exception as e:
        print_error(f"Embedding failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_embeddings():
    """Test batch embedding generation"""
    print_header("TEST 2: BATCH EMBEDDING GENERATION")
    
    service = VoyageEmbeddingsService()
    
    texts = [
        "Confidentiality clause: Both parties agree to maintain confidentiality",
        "Liability limitation: Neither party shall be liable for indirect damages",
        "Payment terms: Monthly fee of $50,000 due within 15 days",
        "Termination clause: Either party may terminate with 30 days notice",
        "Intellectual property: All deliverables are exclusive property of client"
    ]
    
    try:
        embeddings = service.embed_batch(texts)
        if embeddings and len(embeddings) == len(texts):
            print_success(f"Batch embedding completed: {len(embeddings)} chunks")
            for i, emb in enumerate(embeddings):
                if emb:
                    print_info(f"  Chunk {i+1}: {len(emb)} dimensions")
                else:
                    print_error(f"  Chunk {i+1}: Failed")
            return True
        else:
            print_error(f"Batch embedding mismatch: expected {len(texts)}, got {len(embeddings)}")
            return False
    except Exception as e:
        print_error(f"Batch embedding failed: {str(e)}")
        return False

def test_database_connection():
    """Test database and pgvector"""
    print_header("TEST 3: DATABASE & PGVECTOR VERIFICATION")
    
    try:
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
        print_success("Database connection working")
        
        # Check pgvector extension
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
            result = cursor.fetchone()
            if result:
                print_success("pgvector extension enabled")
            else:
                print_error("pgvector extension not found")
                return False
        
        # Check DocumentChunk table
        chunks = DocumentChunk.objects.all().count()
        print_success(f"DocumentChunk table accessible ({chunks} records)")
        
        return True
    except Exception as e:
        print_error(f"Database test failed: {str(e)}")
        return False

def test_document_lifecycle():
    """Test complete document upload and processing"""
    print_header("TEST 4: DOCUMENT LIFECYCLE")
    
    try:
        # Create tenant
        tenant, _ = TenantModel.objects.get_or_create(
            name='Test Tenant Real-Time',
            defaults={'domain': 'test-realtime.local'}
        )
        print_success(f"Tenant created/retrieved: {tenant.name}")
        
        # Create user
        user, _ = User.objects.get_or_create(
            email='realtime-test@example.com',
            defaults={
                'first_name': 'RealTime',
                'last_name': 'Test',
                'is_active': True,
                'tenant_id': tenant.id
            }
        )
        user.set_password('RealTimeTest123!')
        user.save()
        print_success(f"User created/retrieved: {user.email}")
        
        # Initialize API client
        client = APIClient()
        token = get_token_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        print_success("API client authenticated")
        
        # Upload document
        contract_file = BytesIO(SAMPLE_CONTRACT.encode('utf-8'))
        contract_file.name = 'test_agreement.txt'
        
        print_info("Uploading contract document...")
        response = client.post('/api/documents/ingest/', {
            'file': contract_file,
            'document_type': 'Service Agreement'
        }, format='multipart')
        
        if response.status_code in [200, 201]:
            data = response.json()
            doc_id = data.get('document_id') or data.get('id')
            print_success(f"Document uploaded: {doc_id}")
            print_info(f"Response: {json.dumps({k: v for k, v in data.items() if k != 'file_url'}, indent=2)}")
            
            # Check document creation
            doc = Document.objects.get(id=doc_id)
            print_success(f"Document stored in database")
            
            # Check chunks creation
            chunks = DocumentChunk.objects.filter(document_id=doc_id)
            print_success(f"Chunks created: {chunks.count()}")
            
            # Check embeddings
            chunks_with_emb = chunks.exclude(embedding__isnull=True)
            print_success(f"Chunks with embeddings: {chunks_with_emb.count()}/{chunks.count()}")
            
            if chunks_with_emb.count() > 0:
                sample = chunks_with_emb.first()
                if sample.embedding:
                    print_info(f"Sample embedding dimension: {len(sample.embedding)}")
            
            # Check metadata
            metadata = DocumentMetadata.objects.filter(document_id=doc_id).first()
            if metadata:
                print_success(f"Metadata extracted")
                print_info(f"  Parties: {metadata.parties}")
                print_info(f"  Values: {metadata.contract_value}")
                print_info(f"  Clauses: {metadata.identified_clauses}")
            
            return {
                'success': True,
                'doc_id': doc_id,
                'user_id': user.user_id,
                'tenant_id': tenant.id,
                'chunks': chunks.count(),
                'chunks_with_embeddings': chunks_with_emb.count(),
                'token': token,
                'client': client
            }
        else:
            print_error(f"Document upload failed: {response.status_code}")
            print_error(f"Response: {response.text[:500]}")
            return {'success': False}
    
    except Exception as e:
        print_error(f"Document lifecycle failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False}

def test_semantic_search(context):
    """Test semantic search with real embeddings"""
    print_header("TEST 5: SEMANTIC SEARCH (REAL-TIME)")
    
    if not context['success']:
        print_error("Skipping - document not created")
        return False
    
    try:
        client = context['client']
        
        queries = [
            "liability and damages",
            "confidentiality obligations",
            "payment terms and invoicing",
            "termination provisions"
        ]
        
        all_results = []
        for query in queries:
            print_info(f"Searching for: '{query}'")
            response = client.get('/api/search/semantic/', {
                'q': query,
                'top_k': 5,
                'threshold': 0.5
            })
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                print_success(f"  Found {count} results")
                
                if count > 0:
                    for i, result in enumerate(data.get('results', [])[:2], 1):
                        print_info(f"    Result {i} (similarity: {result.get('similarity_score', 0):.3f})")
                        print_info(f"      Text: {result.get('text', '')[:80]}...")
                        all_results.append(result)
            else:
                print_error(f"  Search failed: {response.status_code}")
                print_error(f"  {response.text[:200]}")
        
        return len(all_results) > 0
    
    except Exception as e:
        print_error(f"Semantic search failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_keyword_search(context):
    """Test keyword search"""
    print_header("TEST 6: KEYWORD SEARCH (REAL-TIME)")
    
    if not context['success']:
        print_error("Skipping - document not created")
        return False
    
    try:
        client = context['client']
        
        queries = [
            "confidentiality",
            "liability",
            "payment",
            "termination"
        ]
        
        all_results = []
        for query in queries:
            print_info(f"Searching for: '{query}'")
            response = client.get('/api/search/keyword/', {
                'q': query,
                'limit': 5
            })
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                print_success(f"  Found {count} results")
                
                if count > 0:
                    for i, result in enumerate(data.get('results', [])[:1], 1):
                        print_info(f"    Text: {result.get('text', '')[:80]}...")
                        all_results.append(result)
            else:
                print_error(f"  Search failed: {response.status_code}")
        
        return len(all_results) > 0
    
    except Exception as e:
        print_error(f"Keyword search failed: {str(e)}")
        return False

def test_hybrid_search(context):
    """Test hybrid search combining semantic and keyword"""
    print_header("TEST 7: HYBRID SEARCH (REAL-TIME)")
    
    if not context['success']:
        print_error("Skipping - document not created")
        return False
    
    try:
        client = context['client']
        
        print_info("Running hybrid search: 'liability and damages'")
        response = client.get('/api/search/hybrid/', {
            'q': 'liability and damages',
            'top_k': 10,
            'semantic_weight': 0.7,
            'keyword_weight': 0.3
        })
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print_success(f"Found {count} hybrid results")
            
            if count > 0:
                for i, result in enumerate(data.get('results', [])[:3], 1):
                    similarity = result.get('similarity_score', result.get('score', 0))
                    print_info(f"  Result {i} (score: {similarity:.3f}): {result.get('text', '')[:60]}...")
            
            return True
        else:
            print_error(f"Hybrid search failed: {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Hybrid search failed: {str(e)}")
        return False

def test_statistics(context):
    """Test statistics endpoint"""
    print_header("TEST 8: SEARCH STATISTICS")
    
    if not context['success']:
        print_error("Skipping - no data created")
        return False
    
    try:
        client = context['client']
        
        response = client.get('/api/search/stats/')
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            
            print_success("Statistics retrieved:")
            print_info(f"  Total Documents: {stats.get('total_documents', 0)}")
            print_info(f"  Total Chunks: {stats.get('total_chunks', 0)}")
            print_info(f"  Chunks with Embeddings: {stats.get('chunks_with_embeddings', 0)}")
            
            clause_stats = stats.get('clause_statistics', {})
            if clause_stats:
                print_info(f"  Clause Types Found: {len(clause_stats)}")
                for clause_type, count in list(clause_stats.items())[:3]:
                    print_info(f"    - {clause_type}: {count}")
            
            return True
        else:
            print_error(f"Statistics failed: {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Statistics test failed: {str(e)}")
        return False

def main():
    """Run all real-time tests"""
    print_header("REAL-TIME SEMANTIC SEARCH SYSTEM TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {
        'voyage_ai': False,
        'batch_embeddings': False,
        'database': False,
        'document_lifecycle': False,
        'semantic_search': False,
        'keyword_search': False,
        'hybrid_search': False,
        'statistics': False
    }
    
    # Run tests
    results['voyage_ai'] = test_voyage_ai_connection()
    results['batch_embeddings'] = test_batch_embeddings()
    results['database'] = test_database_connection()
    
    context = test_document_lifecycle()
    results['document_lifecycle'] = context.get('success', False)
    
    if context.get('success'):
        results['semantic_search'] = test_semantic_search(context)
        results['keyword_search'] = test_keyword_search(context)
        results['hybrid_search'] = test_hybrid_search(context)
        results['statistics'] = test_statistics(context)
    
    # Print summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}")
    
    print(f"\n{'='*80}")
    print(f"OVERALL: {passed}/{total} tests passed")
    print(f"Status: {'🎉 ALL SYSTEMS OPERATIONAL' if passed == total else '⚠️  SOME TESTS FAILED'}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
