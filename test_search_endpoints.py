#!/usr/bin/env python
"""
Test Search Endpoints - Comprehensive Test of Semantic Search, Keyword Search, and Hybrid Search
"""
import os
import sys
import django
import json
import requests
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import TenantModel
from repository.models import Document, DocumentChunk
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def get_token_for_user(user):
    """Get JWT token for a user"""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def test_search_endpoints():
    """Test all search endpoints"""
    print("\n" + "="*80)
    print("TESTING SEARCH ENDPOINTS")
    print("="*80 + "\n")
    
    # Create or get tenant
    print("[1] Creating/Getting Tenant...")
    tenant, created = TenantModel.objects.get_or_create(
        name='Default Tenant',
        defaults={'domain': 'default.local'}
    )
    print(f"    Tenant: {tenant.name} (ID: {tenant.id}) {'[CREATED]' if created else '[EXISTING]'}")
    
    # Create or get user
    print("\n[2] Creating/Getting User...")
    user, created = User.objects.get_or_create(
        email='testadmin@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Admin',
            'is_active': True,
            'tenant': tenant
        }
    )
    user.set_password('TestPassword123!')
    user.save()
    print(f"    User: {user.email} (ID: {user.id}) {'[CREATED]' if created else '[EXISTING]'}")
    print(f"    Tenant: {user.tenant.name}")
    
    # Get JWT token
    print("\n[3] Getting JWT Token...")
    token = get_token_for_user(user)
    print(f"    Token: {token[:50]}...")
    
    # Initialize API client
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Check for documents
    print("\n[4] Checking for Documents in Database...")
    documents = Document.objects.filter(tenant=tenant)
    print(f"    Total documents: {documents.count()}")
    
    chunks = DocumentChunk.objects.filter(document__tenant=tenant)
    print(f"    Total chunks: {chunks.count()}")
    
    chunks_with_embeddings = chunks.exclude(embeddings__isnull=True).exclude(embeddings=[])
    print(f"    Chunks with embeddings: {chunks_with_embeddings.count()}")
    
    # Test 1: Semantic Search
    print("\n[5] Testing Semantic Search Endpoint...")
    print("    GET /api/search/semantic/?q=liability&top_k=5")
    response = client.get('/api/search/semantic/', {'q': 'liability', 'top_k': 5})
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Response: {json.dumps(data, indent=2)[:500]}...")
    else:
        print(f"    Error: {response.text[:200]}")
    
    # Test 2: Keyword Search
    print("\n[6] Testing Keyword Search Endpoint...")
    print("    GET /api/search/keyword/?q=confidentiality&limit=10")
    response = client.get('/api/search/keyword/', {'q': 'confidentiality', 'limit': 10})
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Response: {json.dumps(data, indent=2)[:500]}...")
    else:
        print(f"    Error: {response.text[:200]}")
    
    # Test 3: Hybrid Search
    print("\n[7] Testing Hybrid Search Endpoint...")
    print("    GET /api/search/hybrid/?q=termination&top_k=10&semantic_weight=0.7&keyword_weight=0.3")
    response = client.get('/api/search/hybrid/', {
        'q': 'termination',
        'top_k': 10,
        'semantic_weight': 0.7,
        'keyword_weight': 0.3
    })
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Response: {json.dumps(data, indent=2)[:500]}...")
    else:
        print(f"    Error: {response.text[:200]}")
    
    # Test 4: Clause Search
    print("\n[8] Testing Clause Search Endpoint...")
    print("    GET /api/search/clauses/?type=Confidentiality&limit=10")
    response = client.get('/api/search/clauses/', {'type': 'Confidentiality', 'limit': 10})
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Response: {json.dumps(data, indent=2)[:500]}...")
    else:
        print(f"    Error: {response.text[:200]}")
    
    # Test 5: Search Stats
    print("\n[9] Testing Search Stats Endpoint...")
    print("    GET /api/search/stats/")
    response = client.get('/api/search/stats/')
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Response: {json.dumps(data, indent=2)}")
    else:
        print(f"    Error: {response.text[:200]}")
    
    print("\n" + "="*80)
    print("SEARCH ENDPOINT TESTS COMPLETE")
    print("="*80 + "\n")

if __name__ == '__main__':
    test_search_endpoints()
