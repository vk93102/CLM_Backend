#!/usr/bin/env python
"""Generate embeddings for all DocumentChunks without them"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/Users/vishaljha/CLM_Backend')
django.setup()

from repository.models import DocumentChunk
from repository.embeddings_service import VoyageEmbeddingsService

# Initialize the embeddings service
embeddings_service = VoyageEmbeddingsService()

# Get chunks without embeddings
chunks_to_process = list(
    DocumentChunk.objects.filter(embedding__isnull=True) | 
    DocumentChunk.objects.filter(embedding=[])
)

print(f"Processing {len(chunks_to_process)} chunks without embeddings...")

success_count = 0
error_count = 0

for i, chunk in enumerate(chunks_to_process, 1):
    try:
        # Generate embedding for the chunk text
        embedding = embeddings_service.embed_text(chunk.text)
        if embedding and len(embedding) > 0:
            chunk.embedding = embedding
            chunk.is_processed = True
            chunk.save()
            success_count += 1
            print(f"[{i}/{len(chunks_to_process)}] ✓ Processed: {chunk.id}")
        else:
            error_count += 1
            print(f"[{i}/{len(chunks_to_process)}] ✗ No embedding generated for: {chunk.id}")
    except Exception as e:
        error_count += 1
        print(f"[{i}/{len(chunks_to_process)}] ✗ Error: {chunk.id} - {str(e)}")

# Final count
with_embedding = DocumentChunk.objects.exclude(embedding__isnull=True).exclude(embedding=[]).count()

print(f"\n{'='*60}")
print(f"✓ Successfully processed: {success_count}")
print(f"✗ Failed: {error_count}")
print(f"Total chunks WITH embeddings now: {with_embedding}/28")
print(f"{'='*60}")
