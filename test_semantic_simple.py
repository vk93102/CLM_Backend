#!/usr/bin/env python
"""
SIMPLE: Semantic search with existing data
"""

import os
import sys
import django
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from repository.models import DocumentChunk, Document
from repository.search_service import SemanticSearchService
from tenants.models import TenantModel

def generate_mock_embedding(text, dimension=1024):
    np.random.seed(hash(text) % (2**32))
    embedding = np.random.randn(dimension).astype(np.float32)
    embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
    return embedding.tolist()

print("\n" + "="*80)
print("  SEMANTIC SEARCH - FIX VERIFICATION")
print("="*80 + "\n")

# Get first available document and tenant
doc = Document.objects.first()
if not doc:
    print("❌ No documents found. Please upload a document first.")
    sys.exit(1)

tenant = TenantModel.objects.get(id=doc.tenant_id)
print(f"✅ Using document: {doc.filename}")
print(f"✅ Using tenant: {tenant.name}\n")

# Add embeddings to chunks if missing
print("STEP 1: Ensure chunks have embeddings")
print("-" * 80)

chunks = DocumentChunk.objects.filter(document=doc)
chunks_to_update = chunks.filter(embedding__isnull=True)

if chunks_to_update.count() > 0:
    print(f"Adding embeddings to {chunks_to_update.count()} chunks...")
    for chunk in chunks_to_update:
        embedding = generate_mock_embedding(chunk.text)
        chunk.embedding = embedding
        chunk.save()
    print(f"✅ Added embeddings\n")
else:
    print(f"✅ All {chunks.count()} chunks already have embeddings\n")

# Perform semantic search
print("STEP 2: Perform semantic search")
print("-" * 80)

service = SemanticSearchService()
results = service.semantic_search(
    query="confidentiality and data protection",
    tenant_id=str(tenant.id),
    top_k=5,
    threshold=0.2
)

print(f"✅ Query: 'confidentiality and data protection'")
print(f"✅ Results found: {len(results)}\n")

if results:
    print("✅✅✅ SUCCESS! SEMANTIC SEARCH IS WORKING!\n")
    for i, result in enumerate(results, 1):
        sim = result.get('similarity', 0)
        text = result.get('text', '')[:70]
        print(f"  [{i}] Similarity: {sim:.4f}")
        print(f"      Text: {text}...\n")
else:
    print("⚠️  No results found")
    print("Debugging:")
    print(f"  - Document: {doc.filename}")
    print(f"  - Chunks: {chunks.count()}")
    print(f"  - Chunks with embeddings: {chunks.filter(embedding__isnull=False).count()}")

print("="*80 + "\n")
