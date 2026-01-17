#!/usr/bin/env python
"""
Comprehensive Document Upload and Search Test
Tests the complete pipeline: Upload → Process → Embed → Search
"""
import os
import sys
import django
import json
from io import BytesIO
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import TenantModel
from repository.models import Document, DocumentChunk, DocumentMetadata
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# Sample contract text
SAMPLE_CONTRACT = """
CONTRACT AGREEMENT

This Service Agreement ("Agreement") is entered into as of January 17, 2026, between ABC Corporation 
("Company") and XYZ Services Inc. ("Service Provider").

ARTICLE 1: SERVICES
Service Provider agrees to provide software development and maintenance services as described in Exhibit A.

ARTICLE 2: CONFIDENTIALITY
Each party agrees to maintain the confidentiality of any proprietary information disclosed during the 
performance of services. Confidential information includes but is not limited to: technical specifications, 
customer lists, pricing information, and business strategies.

ARTICLE 3: TERM AND TERMINATION
This Agreement shall commence on the Effective Date and continue for one (1) year, unless earlier 
terminated by either party upon thirty (30) days written notice. Upon termination, Service Provider shall 
return all confidential materials and cease all work activities immediately.

ARTICLE 4: COMPENSATION
Company shall pay Service Provider a monthly fee of $50,000 for services rendered, due within fifteen 
(15) days of invoice receipt. Late payments shall accrue interest at 1.5% per month.

ARTICLE 5: LIABILITY AND INDEMNIFICATION
Neither party shall be liable for indirect, incidental, or consequential damages. Company indemnifies 
Service Provider from any third-party claims arising from misuse of provided services.

ARTICLE 6: INTELLECTUAL PROPERTY
All work product and deliverables created by Service Provider shall be considered work for hire and shall 
be the exclusive property of Company. Service Provider retains no rights to such materials.

ARTICLE 7: DISPUTE RESOLUTION
Any disputes shall be resolved through binding arbitration in accordance with American Arbitration 
Association rules. The prevailing party shall recover reasonable attorneys' fees.

ARTICLE 8: GENERAL PROVISIONS
- This Agreement constitutes the entire agreement between the parties
- No modification shall be valid unless in writing and signed by both parties
- If any provision is found invalid, remaining provisions shall continue in effect

Signed this 17th day of January, 2026

For ABC Corporation:
__________________________
Jane Smith, CEO

For XYZ Services Inc.:
__________________________
John Doe, President
"""

def get_token_for_user(user):
    """Get JWT token for a user"""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def main():
    print("\n" + "="*80)
    print("COMPREHENSIVE DOCUMENT UPLOAD AND SEARCH TEST")
    print("="*80 + "\n")
    
    # Step 1: Setup Tenant
    print("[Step 1] Creating Tenant...")
    tenant, created = TenantModel.objects.get_or_create(
        name='Test Tenant',
        defaults={'domain': 'test.local'}
    )
    print(f"  ✓ Tenant: {tenant.name} (ID: {tenant.id})")
    
    # Step 2: Setup User
    print("\n[Step 2] Creating User...")
    user, created = User.objects.get_or_create(
        email='testuser@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True,
            'tenant_id': tenant.id
        }
    )
    user.set_password('TestPassword123!')
    user.save()
    print(f"  ✓ User: {user.email} (ID: {user.user_id})")
    
    # Step 3: Get Token
    print("\n[Step 3] Generating JWT Token...")
    token = get_token_for_user(user)
    print(f"  ✓ Token: {token[:50]}...")
    
    # Step 4: Initialize API Client
    print("\n[Step 4] Initializing API Client...")
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    print(f"  ✓ Client ready with authentication")
    
    # Step 5: Upload Document
    print("\n[Step 5] Uploading Sample Contract...")
    contract_file = BytesIO(SAMPLE_CONTRACT.encode('utf-8'))
    contract_file.name = 'sample_contract.txt'
    
    response = client.post('/api/documents/ingest/', {
        'file': contract_file,
        'document_type': 'Service Agreement'
    }, format='multipart')
    
    print(f"  Status: {response.status_code}")
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"  ✓ Document Response: {json.dumps(data, indent=2)}")
        doc_id = data.get('id')
    else:
        print(f"  ✗ Error: {response.text[:300]}")
        return
    
    # Step 6: Check Document Processing
    print("\n[Step 6] Checking Document Processing...")
    response = client.get(f'/api/documents/{doc_id}/')
    if response.status_code == 200:
        data = response.json()
        print(f"  Document: {data.get('filename')}")
        print(f"  Type: {data.get('document_type')}")
        print(f"  Size: {data.get('file_size')} bytes")
        print(f"  Chunks: {data.get('chunks_count')}")
    
    # Step 7: Check if Chunks have Embeddings
    print("\n[Step 7] Checking Chunks and Embeddings...")
    chunks = DocumentChunk.objects.filter(document_id=doc_id)
    print(f"  Total chunks: {chunks.count()}")
    
    chunks_with_embeddings = 0
    for chunk in chunks:
        if chunk.embeddings and len(chunk.embeddings) > 0:
            chunks_with_embeddings += 1
    
    print(f"  Chunks with embeddings: {chunks_with_embeddings}")
    
    if chunks.count() > 0:
        sample_chunk = chunks.first()
        print(f"\n  Sample Chunk:")
        print(f"    Text: {sample_chunk.text[:100]}...")
        print(f"    Has embeddings: {sample_chunk.embeddings is not None and len(sample_chunk.embeddings) > 0}")
        if sample_chunk.embeddings and len(sample_chunk.embeddings) > 0:
            print(f"    Embedding dimension: {len(sample_chunk.embeddings)}")
    
    # Step 8: Check Metadata
    print("\n[Step 8] Checking Document Metadata...")
    metadata = DocumentMetadata.objects.filter(document_id=doc_id).first()
    if metadata:
        print(f"  Parties: {metadata.parties}")
        print(f"  Contract Values: {metadata.contract_value}")
        print(f"  Dates: {metadata.key_dates}")
        print(f"  Clauses: {metadata.extracted_clauses}")
    
    # Step 9: Test Semantic Search
    print("\n[Step 9] Testing Semantic Search...")
    response = client.get('/api/search/semantic/', {'q': 'confidentiality', 'top_k': 5})
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Results found: {data.get('count')}")
        if data.get('count') > 0:
            for i, result in enumerate(data.get('results', [])[:2], 1):
                print(f"\n  Result {i}:")
                print(f"    Similarity: {result.get('similarity_score'):.3f}")
                print(f"    Text: {result.get('text', '')[:100]}...")
    else:
        print(f"  Error: {response.text[:200]}")
    
    # Step 10: Test Keyword Search
    print("\n[Step 10] Testing Keyword Search...")
    response = client.get('/api/search/keyword/', {'q': 'termination', 'limit': 5})
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Results found: {data.get('count')}")
        if data.get('count') > 0:
            for i, result in enumerate(data.get('results', [])[:2], 1):
                print(f"\n  Result {i}:")
                print(f"    Text: {result.get('text', '')[:100]}...")
    
    # Step 11: Test Hybrid Search
    print("\n[Step 11] Testing Hybrid Search...")
    response = client.get('/api/search/hybrid/', {
        'q': 'liability',
        'top_k': 5,
        'semantic_weight': 0.7,
        'keyword_weight': 0.3
    })
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Results found: {data.get('count')}")
    
    # Step 12: Test Search Stats
    print("\n[Step 12] Testing Search Statistics...")
    response = client.get('/api/search/stats/')
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Total Documents: {data.get('stats', {}).get('total_documents')}")
        print(f"  Total Chunks: {data.get('stats', {}).get('total_chunks')}")
        print(f"  Chunks with Embeddings: {data.get('stats', {}).get('chunks_with_embeddings')}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
