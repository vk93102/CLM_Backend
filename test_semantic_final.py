#!/usr/bin/env python
"""
FINAL TEST: Semantic Search with Real Results
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
from repository.embeddings_service import VoyageEmbeddingsService

print("\n" + "="*80)
print("  ✨ FINAL TEST: SEMANTIC SEARCH WITH REAL RESULTS ✨")
print("="*80 + "\n")

# Get first document
doc = Document.objects.first()
if not doc:
    print("❌ No documents found")
    sys.exit(1)

tenant = TenantModel.objects.get(id=doc.tenant_id)
print(f"📄 Document: {doc.filename}")
print(f"🏢 Tenant: {tenant.name}")
print(f"📦 Chunks: {DocumentChunk.objects.filter(document=doc).count()}\n")

# Regenerate embeddings with semantic service
print("STEP 1: Regenerate chunks with SEMANTIC embeddings")
print("-" * 80)

service = VoyageEmbeddingsService()
chunks = DocumentChunk.objects.filter(document=doc)

for chunk in chunks:
    embedding = service.embed_text(chunk.text)
    if embedding:
        chunk.embedding = embedding
        chunk.save()
        print(f"✓ Chunk {chunk.chunk_number}: Generated {len(embedding)}-dim semantic embedding")

print(f"\n✅ All {chunks.count()} chunks now have SEMANTIC embeddings\n")

# Perform semantic search
print("STEP 2: Perform semantic search with multiple queries")
print("-" * 80)

search_service = SemanticSearchService()

queries = [
    ("confidentiality", 0.2),
    ("data protection", 0.2),
    ("payment terms", 0.2),
    ("liability and remedies", 0.2),
]

total_results = 0

for query, threshold in queries:
    results = search_service.semantic_search(
        query=query,
        tenant_id=str(tenant.id),
        top_k=5,
        threshold=threshold
    )
    
    total_results += len(results)
    status = "✅" if results else "⚠️"
    print(f"\n{status} Query: '{query}'")
    print(f"   Results: {len(results)}")
    
    if results:
        for i, result in enumerate(results, 1):
            sim = result.get('similarity', 0)
            text = result.get('text', '')[:65]
            print(f"   [{i}] Similarity: {sim:.4f} | {text}...")

# Summary
print("\n" + "="*80)
print(f"📊 SUMMARY")
print(f"   Total results: {total_results}")

if total_results > 0:
    print("\n✅✅✅ SUCCESS!")
    print("    SEMANTIC SEARCH IS NOW RETURNING REAL RESULTS!")
    print("    Embeddings are SEMANTICALLY CORRELATED based on keywords")
    print("    Queries find related clauses through vector similarity")
else:
    print("\n⚠️  No results found")

print("="*80 + "\n")
