# Cloudflare R2 Integration - Contract Upload & Download

## Overview
This document describes the Cloudflare R2 storage integration for the CLM Backend. All contract documents are now automatically uploaded to Cloudflare R2 and downloadable via secure presigned URLs.

## Features Implemented

### ✅ Automatic R2 Upload on Contract Creation
- When contracts are created through the API, they are automatically stored in Cloudflare R2
- Each contract gets a unique R2 key with tenant isolation
- Download URLs are generated automatically

### ✅ Simple Document Upload Endpoint
- Users can upload any document and get a downloadable Cloudflare link
- No contract record needed - just upload and get a link
- Perfect for quick document sharing

### ✅ Contract Document Upload with Record Creation
- Upload a document AND create a Contract record in one request
- Automatically creates ContractVersion for version tracking
- Stores metadata like file size, hash, and timestamps

### ✅ Download URL Generation
- Generate secure presigned URLs for any stored document
- Configurable expiration times (default: 1 hour)
- Works with both contract IDs and R2 keys

---

## API Endpoints

### 1. Simple Document Upload
**Upload any document to Cloudflare R2 and get a downloadable link**

```http
POST /api/contracts/upload-document/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- file: (binary) Document file [REQUIRED]
- filename: (string) Custom filename [OPTIONAL]
```

**Response:**
```json
{
  "success": true,
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "r2_key": "tenant-uuid/contracts/unique-id.pdf",
  "download_url": "https://r2.cloudflare.com/bucket/tenant-uuid/contracts/unique-id.pdf?X-Amz-...",
  "original_filename": "mydocument.pdf",
  "file_size": 245632,
  "uploaded_at": "2026-01-20T12:00:00Z",
  "message": "File uploaded successfully to Cloudflare R2"
}
```

**CURL Example:**
```bash
curl -X POST http://localhost:11000/api/contracts/upload-document/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "filename=MyContract.pdf"
```

---

### 2. Upload Contract Document (with Contract Record)
**Upload a contract document and optionally create a Contract database record**

```http
POST /api/contracts/upload-contract-document/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- file: (binary) Contract document [REQUIRED]
- create_contract: (boolean) Create Contract record [OPTIONAL, default: false]
- title: (string) Contract title [OPTIONAL]
- contract_type: (string) Contract type [OPTIONAL]
- counterparty: (string) Counterparty name [OPTIONAL]
```

**Response (with create_contract=true):**
```json
{
  "success": true,
  "contract_id": "c7a4d9b2-3f21-4e89-b8d1-9c5f6e8a1234",
  "contract_title": "Service Agreement - 2026-01-20",
  "contract_status": "draft",
  "r2_key": "tenant-uuid/contracts/unique-id.pdf",
  "download_url": "https://...",
  "original_filename": "contract.pdf",
  "file_size": 512000,
  "uploaded_at": "2026-01-20T12:00:00Z",
  "message": "Contract uploaded successfully to Cloudflare R2"
}
```

**CURL Example:**
```bash
# Simple upload without contract record
curl -X POST http://localhost:11000/api/contracts/upload-contract-document/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@contract.pdf"

# Upload with contract record creation
curl -X POST http://localhost:11000/api/contracts/upload-contract-document/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@contract.pdf" \
  -F "create_contract=true" \
  -F "title=My Service Agreement" \
  -F "contract_type=service_agreement" \
  -F "counterparty=Acme Corp"
```

---

### 3. Get Download URL for R2 Document
**Generate a downloadable link for any document stored in R2**

```http
GET /api/contracts/document-download-url/?r2_key=<r2_key>&expiration=3600
Authorization: Bearer <token>

Query Parameters:
- r2_key: (string) R2 storage key [REQUIRED]
- expiration: (int) URL expiration in seconds [OPTIONAL, default: 3600]
```

**Response:**
```json
{
  "success": true,
  "r2_key": "tenant-uuid/contracts/unique-id.pdf",
  "download_url": "https://r2.cloudflare.com/...",
  "expiration_seconds": 3600,
  "expires_at": "2026-01-20T13:00:00Z"
}
```

**CURL Example:**
```bash
curl -X GET "http://localhost:11000/api/contracts/document-download-url/?r2_key=tenant-uuid/contracts/unique-id.pdf&expiration=7200" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 4. Get Contract Download URL
**Get a downloadable link for a specific contract by ID**

```http
GET /api/contracts/<contract_id>/download-url/
Authorization: Bearer <token>

Path Parameters:
- contract_id: (UUID) Contract ID [REQUIRED]
```

**Response:**
```json
{
  "success": true,
  "contract_id": "c7a4d9b2-3f21-4e89-b8d1-9c5f6e8a1234",
  "contract_title": "Service Agreement",
  "version_number": 1,
  "r2_key": "tenant-uuid/contracts/unique-id.pdf",
  "download_url": "https://...",
  "file_size": 512000
}
```

**CURL Example:**
```bash
curl -X GET http://localhost:11000/api/contracts/c7a4d9b2-3f21-4e89-b8d1-9c5f6e8a1234/download-url/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 5. Existing Contract Creation (Enhanced with R2)
**Create contract from template - now automatically uploads to R2**

```http
POST /api/contracts/contracts/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- title: (string) Contract title [REQUIRED]
- contract_type: (string) Contract type [REQUIRED]
- file: (binary) Contract document [OPTIONAL]
- status: (string) Contract status [OPTIONAL]
- counterparty: (string) Counterparty [OPTIONAL]
- value: (decimal) Contract value [OPTIONAL]
- start_date: (date) Start date [OPTIONAL]
- end_date: (date) End date [OPTIONAL]
```

**Response:**
```json
{
  "id": "c7a4d9b2-3f21-4e89-b8d1-9c5f6e8a1234",
  "title": "My Contract",
  "contract_type": "service_agreement",
  "status": "draft",
  "counterparty": "Acme Corp",
  "created_at": "2026-01-20T12:00:00Z",
  "updated_at": "2026-01-20T12:00:00Z"
}
```

**Note:** If a file is uploaded, it's automatically stored in R2 and a ContractVersion is created.

---

## Integration Flow

### Workflow: Upload → Store → Download

```
1. USER UPLOADS DOCUMENT
   ↓
2. API VALIDATES FILE
   ↓
3. CLOUDFLARE R2 UPLOAD
   - Tenant isolation: tenant-id/contracts/unique-id.pdf
   - Metadata: tenant_id, original_filename, uploaded_at
   ↓
4. DATABASE RECORD (optional)
   - Contract record
   - ContractVersion with r2_key, file_hash, file_size
   ↓
5. GENERATE PRESIGNED URL
   - Secure temporary download link
   - Configurable expiration (default: 1 hour)
   ↓
6. RETURN DOWNLOAD URL TO USER
```

---

## Technical Details

### Storage Structure
```
Cloudflare R2 Bucket: <bucket-name>
└── <tenant-id>/
    └── contracts/
        ├── <uuid-1>.pdf
        ├── <uuid-2>.docx
        └── <uuid-3>.pdf
```

### Tenant Isolation
- Every file is stored under `<tenant-id>/contracts/` prefix
- Ensures data separation between tenants
- Access control via JWT authentication

### File Metadata
Each uploaded file stores:
- `tenant_id`: Tenant UUID
- `original_filename`: Original file name
- `uploaded_at`: Timestamp
- `file_size`: File size in bytes
- `file_hash`: SHA256 hash for integrity

### Security
- ✅ JWT authentication required for all endpoints
- ✅ Tenant isolation enforced
- ✅ Presigned URLs with expiration
- ✅ HTTPS only
- ✅ File hash verification

---

## Configuration

### Environment Variables Required
```bash
# Cloudflare R2 Configuration
R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=<your-access-key>
R2_SECRET_ACCESS_KEY=<your-secret-key>
R2_BUCKET_NAME=<your-bucket-name>

# AWS S3 Compatible Settings (for R2)
AWS_S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_STORAGE_BUCKET_NAME=<your-bucket-name>
AWS_S3_REGION_NAME=auto
AWS_S3_CUSTOM_DOMAIN=<your-custom-domain>  # Optional
```

---

## Testing

### Test Document Upload
```bash
# 1. Get authentication token
TOKEN=$(curl -X POST http://localhost:11000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# 2. Upload document
curl -X POST http://localhost:11000/api/contracts/upload-document/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.pdf" \
  | jq .

# 3. Upload with contract creation
curl -X POST http://localhost:11000/api/contracts/upload-contract-document/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@contract.pdf" \
  -F "create_contract=true" \
  -F "title=Test Contract" \
  | jq .
```

### Test Download URL Generation
```bash
# Get download URL for contract
curl -X GET http://localhost:11000/api/contracts/<contract-id>/download-url/ \
  -H "Authorization: Bearer $TOKEN" \
  | jq .
```

---

## Code Files Modified/Created

### New Files
- **`/contracts/r2_views.py`**: New upload/download endpoints
  - `upload_document()` - Simple document upload
  - `upload_contract_document()` - Contract upload with record creation
  - `get_document_download_url()` - Generate download URL by R2 key
  - `get_contract_download_url()` - Generate download URL by contract ID

### Modified Files
- **`/contracts/urls.py`**: Added 4 new URL patterns for R2 endpoints
- **`/contracts/generation_views.py`**: Already has R2 integration in `create()` method

### Existing Files Used
- **`/authentication/r2_service.py`**: R2StorageService class
  - `upload_file()` - Upload to R2
  - `generate_presigned_url()` - Generate download URLs
  - `delete_file()` - Delete from R2

---

## Common Use Cases

### Use Case 1: Quick Document Sharing
**Scenario:** User wants to share a PDF document quickly

```bash
curl -X POST http://localhost:11000/api/contracts/upload-document/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf"

# Returns downloadable link immediately
```

### Use Case 2: Contract Upload with Tracking
**Scenario:** User uploads a signed contract and wants to track it

```bash
curl -X POST http://localhost:11000/api/contracts/upload-contract-document/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@signed-contract.pdf" \
  -F "create_contract=true" \
  -F "title=NDA with Acme Corp" \
  -F "contract_type=nda" \
  -F "counterparty=Acme Corp"

# Creates Contract record + ContractVersion + Returns download link
```

### Use Case 3: Generate New Download Link
**Scenario:** Previous download link expired, need new one

```bash
curl -X GET "http://localhost:11000/api/contracts/document-download-url/?r2_key=tenant-id/contracts/uuid.pdf&expiration=86400" \
  -H "Authorization: Bearer $TOKEN"

# Returns new 24-hour download link
```

### Use Case 4: Contract Creation from Template
**Scenario:** Generate contract from template and automatically store in R2

```bash
curl -X POST http://localhost:11000/api/contracts/contracts/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Service Agreement" \
  -F "contract_type=service_agreement" \
  -F "file=@generated-contract.pdf"

# Automatically uploads to R2 and creates version
```

---

## Error Handling

### Common Errors

**1. No file provided**
```json
{
  "success": false,
  "error": "No file provided",
  "message": "Please provide a file in the request"
}
```

**2. Contract not found**
```json
{
  "success": false,
  "error": "Contract not found",
  "message": "No contract found with ID c7a4d9b2-3f21-4e89-b8d1-9c5f6e8a1234"
}
```

**3. No document available**
```json
{
  "success": false,
  "error": "No document available for this contract",
  "message": "This contract does not have an uploaded document"
}
```

**4. R2 upload failed**
```json
{
  "success": false,
  "error": "Failed to upload file to R2: <error details>",
  "message": "Failed to upload file to Cloudflare R2"
}
```

---

## Best Practices

### ✅ DO
- Always use HTTPS in production
- Set appropriate expiration times for download URLs (1-24 hours)
- Use `create_contract=true` when you need database tracking
- Store the `r2_key` if you need to regenerate download URLs later
- Verify file types before upload on the client side

### ❌ DON'T
- Share download URLs publicly (they have authentication)
- Use very long expiration times (> 24 hours) for sensitive documents
- Upload extremely large files without chunking (> 100MB)
- Store download URLs permanently (they expire)

---

## Support & Troubleshooting

### Check R2 Configuration
```python
from authentication.r2_service import R2StorageService

r2 = R2StorageService()
print(f"Endpoint: {r2.client._endpoint.host}")
print(f"Bucket: {r2.bucket_name}")
```

### Verify Upload
```python
# After upload, verify file exists
r2 = R2StorageService()
url = r2.generate_presigned_url("tenant-id/contracts/uuid.pdf")
print(f"Download URL: {url}")
```

### Debug Authentication
- Ensure JWT token is valid
- Check `tenant_id` is set correctly
- Verify user has correct permissions

---

## Changelog

### Version 1.0 (2026-01-20)
- ✅ Initial Cloudflare R2 integration
- ✅ Simple document upload endpoint
- ✅ Contract document upload with record creation
- ✅ Download URL generation endpoints
- ✅ Automatic R2 upload on contract creation
- ✅ Tenant isolation enforced
- ✅ Presigned URL support with expiration

---

## Next Steps

### Planned Enhancements
- [ ] Bulk document upload
- [ ] Document preview generation
- [ ] Advanced search by document metadata
- [ ] Document versioning with diff tracking
- [ ] Automatic document expiry/archival
- [ ] CDN integration for faster downloads
- [ ] Document watermarking
- [ ] OCR for scanned documents

---

**Documentation Last Updated:** January 20, 2026
**API Version:** v1
**Status:** ✅ Production Ready
