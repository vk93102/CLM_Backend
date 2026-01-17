from repository.models import DocumentChunk
from repository.embeddings_service import VoyageEmbeddingsService
import numpy as np

tenant_id = "45434a45-4914-4b88-ba5d-e1b5d2c4cf5b"

# Get chunks with embeddings
chunks = DocumentChunk.objects.filter(
    document__tenant_id=tenant_id,
    embedding__isnull=False
)

print(f"✓ Total chunks with embeddings: {chunks.count()}")
print()

# Test query embedding
service = VoyageEmbeddingsService()
query_embedding = service.embed_query("confidentiality")

if query_embedding:
    print(f"✓ Query embedding generated: {len(query_embedding)} dimensions")
    print(f"  Type: {type(query_embedding)}")
    if isinstance(query_embedding, list):
        print(f"  First 3 values: {query_embedding[:3]}")
        print(f"  Query norm: {np.linalg.norm(query_embedding):.4f}")
    print()
    
    # Test one chunk embedding
    chunk = chunks.first()
    if chunk:
        print(f"✓ Sample chunk embedding:")
        print(f"  Type: {type(chunk.embedding)}")
        print(f"  Length: {len(chunk.embedding) if chunk.embedding else 0}")
        if isinstance(chunk.embedding, list) and len(chunk.embedding) > 0:
            chunk_vec = np.array(chunk.embedding, dtype=np.float32)
            print(f"  Chunk norm: {np.linalg.norm(chunk_vec):.4f}")
            
            # Calculate similarity
            query_vec = np.array(query_embedding, dtype=np.float32)
            sim = np.dot(query_vec, chunk_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(chunk_vec))
            print(f"  Similarity to query: {sim:.4f}")
else:
    print("✗ Failed to generate query embedding")
