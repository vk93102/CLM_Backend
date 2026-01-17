#!/usr/bin/env python
"""Debug semantic search in detail"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from repository.models import DocumentChunk
from repository.embeddings_service import VoyageEmbeddingsService
import numpy as np

# Initialize service
service = VoyageEmbeddingsService()

# Test tenant
tenant_id = "45434a45-4914-4b88-ba5d-e1b5d2c4cf5b"

# Get chunks
print("=" * 60)
print("SEMANTIC SEARCH DEBUG")
print("=" * 60)
print()

chunks = DocumentChunk.objects.filter(
    document__tenant_id=tenant_id,
    embedding__isnull=False
).select_related('document')

print(f"✓ Found {chunks.count()} chunks with embeddings")
print()

# Generate query embedding
query = "confidentiality"
print(f"Query: {query}")
query_embedding = service.embed_query(query)

if query_embedding:
    print(f"✓ Query embedding generated: {len(query_embedding)} dimensions")
    print(f"  First 5 values: {query_embedding[:5]}")
    print()
else:
    print("✗ Failed to generate query embedding!")
    sys.exit(1)

# Calculate similarities
query_vec = np.array(query_embedding, dtype=np.float32)
query_norm = np.linalg.norm(query_vec)

print(f"Query norm: {query_norm}")
print()

threshold = 0.2
print(f"Threshold: {threshold}")
print()

results = []
for chunk in chunks:
    try:
        chunk_vec = np.array(chunk.embedding, dtype=np.float32)
        chunk_norm = np.linalg.norm(chunk_vec)
        
        if chunk_norm > 0 and query_norm > 0:
            similarity = np.dot(query_vec, chunk_vec) / (query_norm * chunk_norm)
        else:
            similarity = 0.0
        
        print(f"Chunk {chunk.chunk_number} ({chunk.document.filename}):")
        print(f"  Similarity: {similarity:.4f}", end="")
        
        if similarity > threshold:
            print(" ✓ MATCH")
            results.append((chunk, similarity))
        else:
            print(" ✗ below threshold")
        
        # Show first few words
        print(f"  Text: {chunk.text[:50]}...")
        print()
        
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        print()

print("=" * 60)
print(f"RESULTS: {len(results)} matches above threshold {threshold}")
print("=" * 60)

for chunk, sim in sorted(results, key=lambda x: x[1], reverse=True):
    print(f"• {chunk.document.filename} (chunk {chunk.chunk_number}): {sim:.4f}")
