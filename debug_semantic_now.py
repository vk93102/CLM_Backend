#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from repository.models import DocumentChunk
from repository.embeddings_service import VoyageEmbeddingsService
import numpy as np

tenant_id = "45434a45-4914-4b88-ba5d-e1b5d2c4cf5b"

# Get all chunks
chunks = DocumentChunk.objects.filter(
    document__tenant_id=tenant_id,
    embedding__isnull=False
).select_related('document')

print(f"Total chunks: {chunks.count()}")
print()

# Generate query embedding
service = VoyageEmbeddingsService()
query_embedding = service.embed_query("confidentiality")

if not query_embedding:
    print("ERROR: Failed to generate query embedding!")
    exit(1)

print(f"✓ Query embedding generated: {len(query_embedding)} dimensions")
query_vec = np.array(query_embedding, dtype=np.float32)
query_norm = np.linalg.norm(query_vec)
print(f"✓ Query norm: {query_norm:.6f}")
print()

print("=" * 70)
print("SIMILARITY SCORES FOR ALL CHUNKS")
print("=" * 70)
print()

results = []
for i, chunk in enumerate(chunks, 1):
    try:
        chunk_vec = np.array(chunk.embedding, dtype=np.float32)
        chunk_norm = np.linalg.norm(chunk_vec)
        
        if chunk_norm > 0 and query_norm > 0:
            similarity = np.dot(query_vec, chunk_vec) / (query_norm * chunk_norm)
        else:
            similarity = 0.0
        
        results.append((chunk, similarity))
        
        status = "✓ MATCH" if similarity > 0.2 else "✗ Below 0.2"
        print(f"Chunk {i}:")
        print(f"  File: {chunk.document.filename}")
        print(f"  Similarity: {similarity:.6f} {status}")
        print(f"  Text: {chunk.text[:70]}...")
        print()
    except Exception as e:
        print(f"Chunk {i}: ERROR - {str(e)}")
        print()

# Show results sorted
print("=" * 70)
print("SORTED BY SIMILARITY (TOP 5)")
print("=" * 70)
print()

results.sort(key=lambda x: x[1], reverse=True)
for i, (chunk, sim) in enumerate(results[:5], 1):
    print(f"{i}. {chunk.document.filename} - {sim:.6f}")

# Count above different thresholds
print()
print("=" * 70)
print("THRESHOLD ANALYSIS")
print("=" * 70)
for threshold in [0.1, 0.2, 0.3, 0.4, 0.5]:
    count = len([s for c, s in results if s > threshold])
    print(f"  > {threshold}: {count} results")
