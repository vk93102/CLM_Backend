#!/usr/bin/env python
"""Test semantic search API directly"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from repository.search_service import SemanticSearchService
from authentication.models import User

# Get the test user
user = User.objects.get(email="test_search@test.com")
tenant_id = str(user.tenant_id)

print(f"User: {user.email}")
print(f"Tenant ID: {tenant_id}")
print()

# Initialize service
service = SemanticSearchService()

# Test semantic search
print("=" * 60)
print("TESTING SEMANTIC SEARCH")
print("=" * 60)

query = "confidentiality"
results = service.semantic_search(
    query=query,
    tenant_id=tenant_id,
    top_k=10,
    threshold=0.2
)

print(f"\nQuery: {query}")
print(f"Threshold: 0.2")
print(f"Results: {len(results)}")
print()

for i, result in enumerate(results, 1):
    print(f"{i}. {result['filename']} (chunk {result['chunk_number']})")
    print(f"   Similarity: {result.get('similarity', 0):.4f}")
    print(f"   Text: {result['text'][:100]}...")
    print()
