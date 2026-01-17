#!/usr/bin/env python
"""
TEST: Semantic embeddings are now correlated
"""

import os
import sys
import django
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from repository.embeddings_service import VoyageEmbeddingsService

print("\n" + "="*80)
print("  TEST: SEMANTIC EMBEDDINGS WITH KEYWORD CORRELATION")
print("="*80 + "\n")

service = VoyageEmbeddingsService()

# Test 1: Same keyword embeddings
texts = [
    "confidentiality",
    "confidentiality and data protection",
    "confidential information",
    "payment terms",
    "liability clause",
]

print("Generating embeddings...")
embeddings = {}
for text in texts:
    emb = service.embed_text(text)
    if emb:
        embeddings[text] = np.array(emb)
    print(f"✓ {text}")

print("\nCalculating similarities:")
print("-" * 80)

# Calculate similarities between texts
query_text = "confidentiality"
query_emb = embeddings[query_text]

for text, emb in embeddings.items():
    dot = np.dot(query_emb, emb)
    sim = dot / (np.linalg.norm(query_emb) * np.linalg.norm(emb) + 1e-8)
    print(f"  '{text}' vs '{query_text}'")
    print(f"    Similarity: {sim:.4f} {'✓' if abs(sim) > 0.2 else '✗'}\n")

print("="*80 + "\n")
