#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
sys.path.insert(0, '/Users/vishaljha/CLM_Backend')
django.setup()

from repository.models import DocumentChunk, Document
from django.contrib.auth import get_user_model

User = get_user_model()

# Get test user's tenant
user = User.objects.filter(email='test_search@test.com').first()
if not user:
    print("✗ Test user not found")
    sys.exit(1)

user_tenant_id = user.tenant_id
if not user_tenant_id:
    print("✗ Test user has no tenant")
    sys.exit(1)

print(f"✓ Test user tenant: {user_tenant_id}")

# Update all documents to this tenant
doc_count = Document.objects.update(tenant_id=user_tenant_id)
print(f"✓ Updated {doc_count} documents to tenant {user_tenant_id}")

# Verify chunks are now accessible
chunks_in_tenant = DocumentChunk.objects.filter(document__tenant_id=user_tenant_id).count()
print(f"✓ Chunks for test user's tenant: {chunks_in_tenant}")

print("\nAll documents now assigned to test user's tenant!")
