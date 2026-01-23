# 🚀 Cloudflare R2 - 4 New Endpoints Reference Card

## Quick Reference

### 1️⃣ Upload Any Document
```bash
POST /api/contracts/upload-document/
```
**What it does:** Upload any file, get instant download link  
**When to use:** Quick document sharing, no contract record needed  
**Returns:** `{download_url, r2_key, file_size}`

---

### 2️⃣ Upload Contract Document
```bash
POST /api/contracts/upload-contract-document/
```
**What it does:** Upload contract + optionally create database record  
**When to use:** Upload contracts you want to track  
**Returns:** `{contract_id, download_url, r2_key}` (if create_contract=true)

---

### 3️⃣ Get Download URL by R2 Key
```bash
GET /api/contracts/document-download-url/?r2_key=<key>
```
**What it does:** Generate fresh download URL from R2 key  
**When to use:** Previous URL expired, need new one  
**Returns:** `{download_url, expiration_seconds}`

---

### 4️⃣ Get Contract Download URL
```bash
GET /api/contracts/<contract_id>/download-url/
```
**What it does:** Get download link for a specific contract  
**When to use:** User wants to download existing contract  
**Returns:** `{contract_id, contract_title, download_url}`

---

## Usage Examples

### Upload Document (Simplest)
```bash
curl -X POST http://localhost:11000/api/contracts/upload-document/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf"

# Returns:
# {
#   "success": true,
#   "download_url": "https://...",
#   "r2_key": "tenant-id/contracts/uuid.pdf"
# }
```

### Upload Contract with Tracking
```bash
curl -X POST http://localhost:11000/api/contracts/upload-contract-document/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@contract.pdf" \
  -F "create_contract=true" \
  -F "title=Service Agreement" \
  -F "contract_type=service_agreement"

# Returns:
# {
#   "success": true,
#   "contract_id": "uuid",
#   "download_url": "https://...",
#   "r2_key": "tenant-id/contracts/uuid.pdf"
# }
```

### Get New Download Link
```bash
curl -X GET "http://localhost:11000/api/contracts/document-download-url/?r2_key=tenant-id/contracts/uuid.pdf" \
  -H "Authorization: Bearer $TOKEN"

# Returns:
# {
#   "success": true,
#   "download_url": "https://...",
#   "expiration_seconds": 3600
# }
```

### Get Contract Download Link
```bash
curl -X GET http://localhost:11000/api/contracts/<contract-id>/download-url/ \
  -H "Authorization: Bearer $TOKEN"

# Returns:
# {
#   "success": true,
#   "contract_id": "uuid",
#   "contract_title": "Service Agreement",
#   "download_url": "https://..."
# }
```

---

## Enhanced Existing Endpoints

### Create Contract (Now with R2)
```bash
curl -X POST http://localhost:11000/api/contracts/contracts/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=My Contract" \
  -F "contract_type=service_agreement" \
  -F "file=@contract.pdf"

# File automatically uploaded to R2!
# ContractVersion created with r2_key
```

---

## Response Formats

### Success
```json
{
  "success": true,
  "file_id": "uuid",
  "r2_key": "tenant-id/contracts/uuid.pdf",
  "download_url": "https://r2.cloudflare.com/...",
  "original_filename": "contract.pdf",
  "file_size": 123456,
  "uploaded_at": "2026-01-20T12:00:00Z"
}
```

### Error
```json
{
  "success": false,
  "error": "No file provided",
  "message": "Please provide a file in the request"
}
```

---

## Common Parameters

### Request Parameters
- **file** (required): Document file to upload
- **create_contract** (optional): Boolean, create Contract record
- **title** (optional): Contract title
- **contract_type** (optional): Type of contract
- **filename** (optional): Custom filename
- **r2_key** (required for endpoint 3): R2 storage key
- **expiration** (optional): URL expiration in seconds

### Authentication
All endpoints require JWT authentication:
```bash
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Quick Tips

✅ **Use endpoint 1** for quick file sharing  
✅ **Use endpoint 2** for contracts you want to track  
✅ **Use endpoint 3** to refresh expired URLs  
✅ **Use endpoint 4** to get contract download links  

✅ All files stored with tenant isolation  
✅ Download URLs expire after 1 hour (default)  
✅ Files automatically versioned in database  
✅ Supports any file type (PDF, DOCX, TXT, etc.)  

---

## Testing

Run automated tests:
```bash
./test_r2_upload.sh
```

System check:
```bash
python3 manage.py check
# System check identified no issues (0 silenced).
```

---

## Documentation

📖 **Full Documentation:** [CLOUDFLARE_R2_INTEGRATION.md](./CLOUDFLARE_R2_INTEGRATION.md)  
🚀 **Quick Start:** [R2_QUICK_START.md](./R2_QUICK_START.md)  
📋 **All Endpoints:** [ALL_ENDPOINTS_REFERENCE.md](./ALL_ENDPOINTS_REFERENCE.md)  
✅ **Integration Summary:** [INTEGRATION_COMPLETE.md](./INTEGRATION_COMPLETE.md)

---

**Status:** ✅ Production Ready  
**Added:** January 20, 2026  
**Total Endpoints:** 4 new + 3 enhanced  
**Breaking Changes:** None
