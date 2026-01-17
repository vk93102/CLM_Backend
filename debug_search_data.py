#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/Users/vishaljha/CLM_Backend')
django.setup()

from repository.models import DocumentChunk, Document
from tenants.models import TenantModel
from django.contrib.auth import get_user_model

# Check documents and tenants
docs = Document.objects.all()
print(f"Total documents: {docs.count()}")

if docs.exists():
    doc = docs.first()
    print(f"\nFirst document:")
    print(f"  ID: {doc.id}")
    print(f"  Tenant: {doc.tenant_id}")

# Check chunks
chunks = DocumentChunk.objects.all()
print(f"\nTotal chunks: {chunks.count()}")

if chunks.exists():
    chunk = chunks.first()
    print(f"\nFirst chunk:")
    print(f"  ID: {chunk.id}")
    print(f"  Document ID: {chunk.document_id}")
    print(f"  Document tenant: {chunk.document.tenant_id if chunk.document else 'N/A'}")
    print(f"  Embedding length: {len(chunk.embedding) if chunk.embedding else 0}")

# Check tenants
tenants = TenantModel.objects.all()
print(f"\nTotal tenants: {tenants.count()}")
if tenants.exists():
    for t in tenants[:3]:
        chunk_count = DocumentChunk.objects.filter(document__tenant_id=t.id).count()
        print(f"  Tenant {t.id}: {chunk_count} chunks")

# Check test user
User = get_user_model()
test_user = User.objects.filter(email='test_search@test.com').first()
if test_user:
    print(f"\nTest user: {test_user.email}")
    print(f"  Tenant: {test_user.tenant_id if hasattr(test_user, 'tenant_id') else 'N/A'}")
