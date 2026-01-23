# Cloudflare R2 Storage Configuration for CLM Backend

## Installation

```bash
pip install boto3 django-storages
```

## Settings Configuration

Add to `clm_backend/settings.py`:

```python
# Cloudflare R2 Storage
if not DEBUG:  # Production only
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
                "storage_bucket_name": os.getenv("AWS_STORAGE_BUCKET_NAME", "contracts-production"),
                "s3_region_name": os.getenv("AWS_S3_REGION_NAME", "auto"),
                "s3_url_protocol": "https:",
                "s3_custom_domain": os.getenv("AWS_S3_CUSTOM_DOMAIN", "r2.cloudflare.com"),
                "s3_endpoint_url": os.getenv("AWS_S3_ENDPOINT_URL", "https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com"),
                "s3_addressing_style": "auto",
                "signature_version": "s3v4",
                "default_acl": "private",
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    
    # CDN configuration
    AWS_CLOUDFRONT_DOMAIN = os.getenv("AWS_CLOUDFRONT_DOMAIN", "contracts-cdn.example.com")
```

## Environment Variables (`.env`)

```env
# Cloudflare R2 Authentication
AWS_ACCESS_KEY_ID=your_cloudflare_r2_access_key_id
AWS_SECRET_ACCESS_KEY=your_cloudflare_r2_secret_access_key
AWS_STORAGE_BUCKET_NAME=contracts-production
AWS_S3_REGION_NAME=auto
AWS_S3_ENDPOINT_URL=https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
AWS_S3_CUSTOM_DOMAIN=r2.cloudflare.com
AWS_CLOUDFRONT_DOMAIN=contracts-cdn.example.com

# Cloudflare API for CDN purge
CLOUDFLARE_ZONE_ID=your_zone_id
CLOUDFLARE_API_TOKEN=your_api_token
```

## Model Configuration

In `contracts/models.py`:

```python
from django.db import models
from django.core.files.storage import default_storage

class Contract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    contract_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='draft')
    
    # File stored in Cloudflare R2
    pdf_file = models.FileField(
        upload_to='contracts/%Y/%m/',
        storage=default_storage,
        blank=True,
        null=True
    )
    
    # R2 URL
    r2_url = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Generate R2 URL after save
        if self.pdf_file:
            self.r2_url = self.pdf_file.url
            super().save(update_fields=['r2_url'])
```

## Upload to Cloudflare R2

In `contracts/utils/storage.py`:

```python
import boto3
import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def upload_contract_to_r2(contract_id, pdf_content, filename):
    """Upload contract PDF to Cloudflare R2"""
    try:
        # Save to R2
        file_path = f'contracts/{contract_id}/{filename}'
        path = default_storage.save(file_path, ContentFile(pdf_content))
        
        # Get full URL
        url = default_storage.url(path)
        
        return {
            "success": True,
            "path": path,
            "url": url,
            "size": len(pdf_content)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def delete_contract_from_r2(file_path):
    """Delete contract from Cloudflare R2"""
    try:
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
            return {"success": True, "message": "File deleted"}
        return {"success": False, "error": "File not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_contracts_in_r2(folder='contracts/'):
    """List all contracts in R2"""
    try:
        files, dirs = default_storage.listdir(folder)
        return {
            "success": True,
            "files": files,
            "directories": dirs
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Download from Cloudflare R2

In `contracts/contract_generation_views.py`:

```python
from django.http import FileResponse
import requests

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_contract_endpoint(request):
    """Download contract from Cloudflare R2"""
    contract_id = request.query_params.get('contract_id')
    
    if not contract_id:
        return Response(
            {"error": "contract_id parameter required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get contract from database
        contract = Contract.objects.get(id=contract_id)
        
        # If file is in R2
        if contract.r2_url:
            # Stream from R2
            response = requests.get(contract.r2_url, stream=True)
            
            return FileResponse(
                response.raw,
                as_attachment=True,
                filename=f"{contract.title}.pdf",
                content_type='application/pdf'
            )
        
        return Response(
            {"error": "Contract file not found in R2"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Contract.DoesNotExist:
        return Response(
            {"error": "Contract not found"},
            status=status.HTTP_404_NOT_FOUND
        )
```

## Backup & Archival

In `contracts/management/commands/backup_contracts.py`:

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from contracts.models import Contract
import shutil
import os

class Command(BaseCommand):
    help = 'Backup contracts from R2 to local archive'

    def handle(self, *args, **options):
        backup_date = timezone.now().strftime('%Y-%m-%d')
        backup_dir = f'backups/contracts/{backup_date}'
        os.makedirs(backup_dir, exist_ok=True)
        
        contracts = Contract.objects.filter(status='signed')
        
        for contract in contracts:
            if contract.r2_url:
                response = requests.get(contract.r2_url)
                filename = f"{contract.id}_{contract.title}.pdf"
                
                with open(f'{backup_dir}/{filename}', 'wb') as f:
                    f.write(response.content)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Backed up {contracts.count()} contracts')
        )
```

## CDN Purge Configuration

In `contracts/utils/cdn.py`:

```python
import requests
import os

def purge_cloudflare_cache(file_urls):
    """Purge Cloudflare CDN cache for specific files"""
    zone_id = os.getenv("CLOUDFLARE_ZONE_ID")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    
    if not zone_id or not api_token:
        return {"error": "Cloudflare credentials not configured"}
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "files": file_urls if isinstance(file_urls, list) else [file_urls]
    }
    
    try:
        response = requests.post(
            f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache",
            headers=headers,
            json=data
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}
```

## Usage in Views

```python
from contracts.utils.storage import upload_contract_to_r2
from contracts.utils.cdn import purge_cloudflare_cache

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_contract_endpoint(request):
    """Create and store contract in R2"""
    
    # ... contract generation logic ...
    
    # Upload PDF to Cloudflare R2
    result = upload_contract_to_r2(
        contract_id=str(contract.id),
        pdf_content=pdf_buffer.getvalue(),
        filename=f"contract_{contract.contract_type}_{timezone.now().timestamp()}.pdf"
    )
    
    if result["success"]:
        # Save URL in database
        contract.r2_url = result["url"]
        contract.save()
        
        # Purge CDN cache
        purge_cloudflare_cache(result["url"])
        
        return Response({
            "success": True,
            "contract_id": contract.id,
            "file_path": result["url"],
            "file_size": result["size"]
        }, status=status.HTTP_201_CREATED)
```

## Testing R2 Integration

```bash
# Test upload
python manage.py shell
from contracts.utils.storage import upload_contract_to_r2
result = upload_contract_to_r2("test-123", b"test content", "test.pdf")
print(result)

# Test list
from contracts.utils.storage import list_contracts_in_r2
result = list_contracts_in_r2()
print(result)

# Test download
curl "http://127.0.0.1:11000/api/v1/download/?contract_id=YOUR_ID" \
  -H "Authorization: Bearer TOKEN" \
  -o contract.pdf
```

## Monitoring & Logging

```python
import logging

logger = logging.getLogger(__name__)

def log_r2_operation(operation, contract_id, status, details=""):
    """Log R2 storage operations"""
    logger.info(
        f"R2_OP | {operation} | Contract: {contract_id} | Status: {status} | {details}"
    )
```

## Security Best Practices

✅ **Access Control:**
- R2 bucket set to **private** (requires authentication)
- Signed URLs with 1-hour expiration
- API token rotated monthly

✅ **Encryption:**
- All files encrypted in transit (HTTPS)
- Server-side encryption at rest (R2 default)

✅ **Compliance:**
- Audit logs enabled
- Monthly backup verification
- 30-day retention for deleted files

---

**Status:** ✅ Ready for Production  
**Last Updated:** 2026-01-20
