import os
import sys
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/Users/vishaljha/CLM_Backend')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import TenantModel
from repository.models import DocumentChunk, Document
from repository.search_service import SemanticSearchService

User = get_user_model()

# Check user
user = User.objects.filter(email='test_search@test.com').first()
if user:
    print(f"✓ User found: {user.email}")
    print(f"  Tenant: {user.tenant_id if hasattr(user, 'tenant_id') else 'NO TENANT'}")
    
    # Check if user has tenant
    if hasattr(user, 'tenant_id') and user.tenant_id:
        tenant_id = user.tenant_id
        
        # Check documents for this tenant
        docs = Document.objects.filter(tenant_id=tenant_id)
        print(f"\n✓ Documents for tenant {tenant_id}: {docs.count()}")
        
        # Check chunks for this tenant
        chunks = DocumentChunk.objects.filter(document__tenant_id=tenant_id)
        print(f"✓ Chunks for tenant {tenant_id}: {chunks.count()}")
        
        if chunks.exists():
            chunk = chunks.first()
            print(f"\n✓ Sample chunk:")
            print(f"  ID: {chunk.id}")
            print(f"  Embedding: {len(chunk.embedding) if chunk.embedding else 0} dims")
            print(f"  Text: {chunk.text[:100]}")
        
        # Try direct search
        print(f"\n--- Testing Direct Search Service ---")
        service = SemanticSearchService()
        results = service.semantic_search(
            query="confidentiality",
            tenant_id=str(tenant_id),
            top_k=10,
            threshold=0.5
        )
        print(f"✓ Search results: {len(results)} found")
        if results:
            print(f"  First result: {results[0]}")
    else:
        print("✗ User has NO tenant assigned!")
        print("\nAll tenants:")
        for t in TenantModel.objects.all():
            print(f"  - {t.id}: {t.name}")
else:
    print("✗ User not found")
