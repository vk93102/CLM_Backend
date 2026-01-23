# 🚀 Quick Start - Cloudflare R2 Upload Integration

## TL;DR - What You Need to Know

✅ **Contracts are now automatically stored in Cloudflare R2**  
✅ **Every uploaded document gets a downloadable link**  
✅ **4 new endpoints for document uploads and downloads**  
✅ **All existing contract creation flows updated**

---

## 🎯 Quick Examples

### 1. Upload Any Document (Simplest)
```bash
curl -X POST http://localhost:11000/api/contracts/upload-document/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```
**Returns:** Downloadable Cloudflare R2 link immediately

---

### 2. Upload Contract Document
```bash
curl -X POST http://localhost:11000/api/contracts/upload-contract-document/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@contract.pdf" \
  -F "create_contract=true" \
  -F "title=My Contract" \
  -F "contract_type=service_agreement"
```
**Returns:** Contract ID + Downloadable link

---

### 3. Get Download Link for Contract
```bash
curl -X GET http://localhost:11000/api/contracts/<CONTRACT_ID>/download-url/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```
**Returns:** Fresh download URL for the contract

---

### 4. Create Contract with File Upload (Existing Enhanced)
```bash
curl -X POST http://localhost:11000/api/contracts/contracts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Service Agreement" \
  -F "contract_type=service_agreement" \
  -F "file=@generated.pdf"
```
**Returns:** Contract created + Automatically stored in R2

---

## 📋 New API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/contracts/upload-document/` | Upload any document → Get download link |
| POST | `/api/contracts/upload-contract-document/` | Upload contract → Create record + Get link |
| GET | `/api/contracts/document-download-url/?r2_key=<key>` | Get download link by R2 key |
| GET | `/api/contracts/<id>/download-url/` | Get download link by contract ID |

---

## 🔧 Setup Required

### Environment Variables (Already Configured)
```bash
R2_ENDPOINT_URL=https://<account>.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=<your-access-key>
R2_SECRET_ACCESS_KEY=<your-secret-key>
R2_BUCKET_NAME=<your-bucket>
```

---

## 🧪 Testing

### Run Automated Tests
```bash
./test_r2_upload.sh
```

### Manual Test
```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:11000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# 2. Upload document
curl -X POST http://localhost:11000/api/contracts/upload-document/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.pdf" \
  | jq .
```

---

## 📦 Files Created/Modified

### ✅ New Files
- **`contracts/r2_views.py`** - Upload/download view endpoints
- **`CLOUDFLARE_R2_INTEGRATION.md`** - Full documentation
- **`test_r2_upload.sh`** - Automated test script
- **`R2_QUICK_START.md`** - This file

### ✅ Modified Files
- **`contracts/urls.py`** - Added 4 new URL patterns
- **`contracts/generation_views.py`** - Already had R2 integration

---

## 💡 Common Use Cases

### Use Case 1: Share a Document Quickly
**Need:** Upload PDF and share download link
```bash
POST /api/contracts/upload-document/
→ Returns: {"download_url": "https://..."}
```

### Use Case 2: Track Uploaded Contracts
**Need:** Upload contract + Create database record
```bash
POST /api/contracts/upload-contract-document/
  + create_contract=true
→ Creates Contract + ContractVersion + Returns download link
```

### Use Case 3: Regenerate Expired Download Link
**Need:** Get new download URL for existing contract
```bash
GET /api/contracts/<contract-id>/download-url/
→ Returns fresh presigned URL (valid 1 hour)
```

---

## 🔐 Security Features

✅ JWT authentication required  
✅ Tenant isolation (files stored per tenant)  
✅ Presigned URLs with expiration  
✅ File hash verification (SHA256)  
✅ Metadata tracking (tenant_id, filename, timestamps)

---

## 📊 Response Format

### Success Response
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

### Error Response
```json
{
  "success": false,
  "error": "No file provided",
  "message": "Please provide a file in the request"
}
```

---

## 🚨 Common Issues & Solutions

### Issue: "No file provided"
**Solution:** Ensure you're using `multipart/form-data` and field name is `file`
```bash
-F "file=@document.pdf"  # ✅ Correct
-d "file=..."            # ❌ Wrong
```

### Issue: "Contract not found"
**Solution:** Verify contract ID is valid UUID and belongs to your tenant
```bash
GET /api/contracts/<valid-uuid>/download-url/
```

### Issue: "Download URL expired"
**Solution:** Generate new presigned URL
```bash
GET /api/contracts/<id>/download-url/
# Returns fresh URL valid for 1 hour
```

---

## 🎓 How It Works

```
USER UPLOAD
    ↓
VALIDATE FILE
    ↓
UPLOAD TO R2
  → tenant-id/contracts/unique-id.pdf
    ↓
CREATE DB RECORDS (optional)
  → Contract + ContractVersion
    ↓
GENERATE PRESIGNED URL
  → Secure temporary download link
    ↓
RETURN TO USER
  → {"download_url": "https://..."}
```

---

## 📚 Full Documentation

For complete API reference, error codes, and advanced usage:
→ See **[CLOUDFLARE_R2_INTEGRATION.md](./CLOUDFLARE_R2_INTEGRATION.md)**

---

## ✅ Checklist for Frontend Integration

- [ ] Update upload forms to use new endpoints
- [ ] Handle `multipart/form-data` encoding
- [ ] Display download links to users
- [ ] Implement download link refresh (when expired)
- [ ] Show upload progress indicators
- [ ] Handle error responses gracefully
- [ ] Store `r2_key` if you need to regenerate URLs
- [ ] Use HTTPS in production

---

## 🎉 What's Next?

The integration is **production-ready**! Your contracts are now:
- ✅ Automatically uploaded to Cloudflare R2
- ✅ Accessible via secure download links
- ✅ Version tracked in the database
- ✅ Tenant isolated for security

**Start using it today!**

---

**Questions?** Check [CLOUDFLARE_R2_INTEGRATION.md](./CLOUDFLARE_R2_INTEGRATION.md)  
**Issues?** Run `./test_r2_upload.sh` to diagnose

---

**Last Updated:** January 20, 2026  
**Status:** ✅ Ready for Production
