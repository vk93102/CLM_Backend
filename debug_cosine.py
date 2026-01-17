#!/usr/bin/env python
"""
DEBUG: Cosine similarity calculation
"""

import os
import sys
import django
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from repository.models import DocumentChunk
from repository.embeddings_service import VoyageEmbeddingsService

def generate_mock_embedding(text, dimension=1024):
    np.random.seed(hash(text) % (2**32))
    embedding = np.random.randn(dimension).astype(np.float32)
    embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
    return embedding.tolist()

print("\n" + "="*80)
print("  DEBUG: COSINE SIMILARITY CALCULATION")
print("="*80 + "\n")

# Get a chunk with embedding
chunk = DocumentChunk.objects.filter(embedding__isnull=False).first()
if not chunk:
    print("❌ No chunks with embeddings found")
    sys.exit(1)

print(f"✅ Found chunk: {chunk.id}")
print(f"   Text: {chunk.text[:60]}...")
print(f"   Embedding length: {len(chunk.embedding)}\n")

# Generate query embedding
service = VoyageEmbeddingsService()
query = "confidentiality"
query_embedding = service.embed_query(query)

if query_embedding:
    print(f"✅ Generated query embedding for: '{query}'")
    print(f"   Length: {len(query_embedding)}\n")
    query_vec = np.array(query_embedding, dtype=np.float32)
else:
    print(f"Using mock embedding for: '{query}'")
    query_embedding = generate_mock_embedding(query)
    query_vec = np.array(query_embedding, dtype=np.float32)
    print(f"   Length: {len(query_embedding)}\n")

# Calculate similarity
chunk_vec = np.array(chunk.embedding, dtype=np.float32)

print("CALCULATION STEPS:")
print("-" * 80)

# Norms
chunk_norm = np.linalg.norm(chunk_vec)
query_norm = np.linalg.norm(query_vec)
print(f"1. Chunk embedding norm: {chunk_norm:.6f}")
print(f"2. Query embedding norm: {query_norm:.6f}")

# Dot product
dot_product = np.dot(query_vec, chunk_vec)
print(f"3. Dot product: {dot_product:.6f}")

# Cosine similarity
if chunk_norm > 0 and query_norm > 0:
    similarity = dot_product / (query_norm * chunk_norm)
else:
    similarity = 0.0

print(f"4. Cosine similarity: {similarity:.6f}")
print(f"5. Threshold comparison: {similarity:.6f} > 0.2 = {similarity > 0.2}\n")

# Sample similarities
print("SAMPLE SIMILARITIES:")
print("-" * 80)

texts = [
    chunk.text,
    "This is a confidentiality clause stating the obligations",
    "Payment terms and conditions",
    "Data protection and privacy",
]

for text in texts:
    text_emb = generate_mock_embedding(text)
    text_vec = np.array(text_emb, dtype=np.float32)
    text_norm = np.linalg.norm(text_vec)
    dot = np.dot(query_vec, text_vec)
    sim = dot / (query_norm * text_norm) if query_norm * text_norm > 0 else 0
    print(f"Text: '{text[:40]}...'")
    print(f"  Similarity: {sim:.6f} (passes threshold {0.2}: {sim > 0.2})\n")

print("="*80 + "\n")
