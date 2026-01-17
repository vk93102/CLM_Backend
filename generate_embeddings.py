#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/Users/vishaljha/CLM_Backend')
django.setup()

from repository.models import DocumentChunk
from repository.services.semantic_search import SemanticSearchService

# Initialize the service
service = SemanticSearchService()

# Get chunks without embeddings
chunks_to_process = DocumentChunk.objects.filter(embedding__isnull=True) | DocumentChunk.objects.filter(embedding=[])

print(f"Processing {chunks_to_process.count()} chunks without embeddings...")

success_count = 0
error_count = 0

for chunk in chunks_to_process:
    try:
        # Generate embedding for the chunk text
        embedding = service.generate_embedding(chunk.text)
        if embedding:
            chunk.embedding = embedding
            chunk.is_processed = True
            chunk.save()
            success_count += 1
            print(f"✓ Processed chunk {success_count}: {chunk.id}")
        else:
            error_count += 1
            print(f"✗ Failed to generate embedding for chunk {chunk.id}")
    except Exception as e:
        error_count += 1
        print(f"✗ Error processing chunk {chunk.id}: {str(e)}")

print(f"\n✓ Successfully processed: {success_count}")
print(f"✗ Failed: {error_count}")

# Final count
with_embedding = DocumentChunk.objects.exclude(embedding__isnull=True).exclude(embedding=[]).count()
print(f"\nTotal chunks WITH embeddings now: {with_embedding}/28")
