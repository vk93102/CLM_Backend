#!/usr/bin/env python
"""
QUICK TEST: Semantic Search Fix
"""

import os
import sys
import django
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from repository.models import DocumentChunk
from repository.search_service import SemanticSearchService
from tenants.models import TenantModel

print("\n" + "="*80)
print("  SEMANTIC SEARCH - QUICK FIX TEST")
print("="*80 + "\n")

# Get data
tenant = TenantModel.objects.first()
if not tenant:
    print("❌ No tenant found")
    sys.exit(1)

chunks_count = DocumentChunk.objects.filter(
    document__tenant_id=tenant.id,
    embedding__isnull=False
).count()

print(f"✅ Found {chunks_count} chunks with embeddings")
print(f"✅ Tenant ID: {tenant.id}\n")

# Test service
service = SemanticSearchService()
results = service.semantic_search(
    query="confidentiality clause",
    tenant_id=str(tenant.id),
    top_k=5,
    threshold=0.3
)

print(f"✅ Search completed: {len(results)} results\n")

if results:
    print("✅✅✅ ISSUE FIXED! SEMANTIC SEARCH NOW RETURNING REAL RESULTS!\n")
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Similarity: {result.get('similarity', 0):.4f}")
        print(f"  Text: {result.get('text', '')[:70]}...\n")
else:
    print("❌ Still no results")
    print("Checking chunks directly...")
    chunk = DocumentChunk.objects.filter(
        document__tenant_id=tenant.id,
        embedding__isnull=False
    ).first()
    if chunk:
        print(f"Sample chunk embedding length: {len(chunk.embedding)}")
        print(f"Sample chunk embedding type: {type(chunk.embedding)}")

print("="*80 + "\n")
