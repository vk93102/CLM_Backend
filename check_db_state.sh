#!/bin/bash
cd /Users/vishaljha/CLM_Backend

python manage.py shell 2>&1 <<'PYEOF'
from repository.models import DocumentChunk, Document
from tenants.models import TenantModel
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== DATABASE STATE ===")

# Check tenant
print("\nTenants:")
for t in TenantModel.objects.all()[:5]:
    print(f"  - {t.id}: {t.name}")

# Check user
print("\nTest User:")
user = User.objects.filter(email='test_search@test.com').first()
if user:
    print(f"  Email: {user.email}")
    print(f"  Tenant ID: {getattr(user, 'tenant_id', 'NO TENANT')}")
else:
    print("  Not found!")

# Check documents
print("\nDocuments:")
docs = Document.objects.all()
print(f"  Total: {docs.count()}")
if docs.exists():
    doc = docs.first()
    print(f"  First doc ID: {doc.id}")
    print(f"  First doc Tenant: {doc.tenant_id}")

# Check chunks
print("\nDocumentChunks:")
chunks = DocumentChunk.objects.all()
print(f"  Total: {chunks.count()}")
if chunks.exists():
    chunk = chunks.first()
    print(f"  First chunk ID: {chunk.id}")
    print(f"  First chunk Doc: {chunk.document_id}")
    if chunk.document:
        print(f"  First chunk Doc Tenant: {chunk.document.tenant_id}")
    print(f"  Has Embedding: {bool(chunk.embedding)}")

# Check if chunks match test user's tenant
if user and hasattr(user, 'tenant_id') and user.tenant_id:
    tenant_id = user.tenant_id
    print(f"\n=== CHECKING TENANT {tenant_id} ===")
    chunks_for_tenant = DocumentChunk.objects.filter(document__tenant_id=tenant_id)
    print(f"Chunks for this tenant: {chunks_for_tenant.count()}")
    
    if chunks_for_tenant.exists():
        chunk = chunks_for_tenant.first()
        print(f"  First chunk: {chunk.id}")
        print(f"  Has embedding: {bool(chunk.embedding)}")
        print(f"  Text: {chunk.text[:100]}")
PYEOF
