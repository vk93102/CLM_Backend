# 🌐 Cloudflare R2 Contract Upload & Management Guide

**Complete guide for uploading, storing, and managing contracts in Cloudflare R2**

---

## 📚 Overview

All contracts are stored in **Cloudflare R2** with:
- ✅ Encrypted storage
- ✅ Global CDN distribution
- ✅ Daily automatic backups
- ✅ Signed URLs for temporary access
- ✅ Public URLs for direct access

---

## 🔌 Upload & Management Endpoints

### 1. **POST /api/v1/upload-contract/**
Upload contract PDF to Cloudflare R2

**Endpoint:** `POST /api/v1/upload-contract/`

**Authentication:** Required (Bearer Token)

**Request:**
```bash
curl -X POST http://127.0.0.1:11000/api/v1/upload-contract/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "contract_id=5657db63-7ed1-463f-a27b-fb5bf237121a" \
  -F "pdf_file=@contract.pdf" \
  -F "contract_type=nda" \
  -F "metadata={\"signer\": \"John Doe\"}"
```

**Response (200 OK):**
```json
{
  "success": true,
  "contract_id": "5657db63-7ed1-463f-a27b-fb5bf237121a",
  "object_key": "contracts/2026/01/20/5657db63-7ed1-463f-a27b-fb5bf237121a/contract_nda.pdf",
  "public_url": "https://r2.cloudflare.com/contracts/2026/01/20/5657db63-7ed1-463f-a27b-fb5bf237121a/contract_nda.pdf",
  "size": 109766,
  "uploaded_at": "2026-01-20T08:01:43.070370+00:00",
  "message": "Contract uploaded successfully to Cloudflare R2"
}
```

---

### 2. **GET /api/v1/contracts-list/**
List all contracts in Cloudflare R2

**Endpoint:** `GET /api/v1/contracts-list/`

**Authentication:** Required (Bearer Token)

**Query Parameters:**
| Parameter | Type | Optional | Example |
|-----------|------|----------|---------|
| `prefix` | string | Yes | `contracts/2026/01/` |
| `limit` | integer | Yes | `50` |

**Request:**
```bash
curl http://127.0.0.1:11000/api/v1/contracts-list/ \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "success": true,
  "bucket": "contracts-production",
  "total_files": 45,
  "files": [
    {
      "key": "contracts/2026/01/20/5657db63-7ed1-463f-a27b-fb5bf237121a/contract_nda.pdf",
      "size": 109766,
      "last_modified": "2026-01-20T08:01:43.070370+00:00",
      "url": "https://r2.cloudflare.com/contracts/2026/01/20/5657db63-7ed1-463f-a27b-fb5bf237121a/contract_nda.pdf"
    },
    {
      "key": "contracts/2026/01/20/8844cc55-2211-4455-8899-aabbccddeeff/contract_employment.pdf",
      "size": 145920,
      "last_modified": "2026-01-20T08:05:12.123456+00:00",
      "url": "https://r2.cloudflare.com/contracts/2026/01/20/8844cc55-2211-4455-8899-aabbccddeeff/contract_employment.pdf"
    }
  ],
  "storage_stats": {
    "total_objects": 156,
    "total_size_mb": 48.5
  }
}
```

---

### 3. **GET /api/v1/contract-url/**
Get public URL for contract

**Endpoint:** `GET /api/v1/contract-url/?contract_id=...`

**Authentication:** Required (Bearer Token)

**Request:**
```bash
curl "http://127.0.0.1:11000/api/v1/contract-url/?contract_id=5657db63-7ed1-463f-a27b-fb5bf237121a" \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "success": true,
  "contract_id": "5657db63-7ed1-463f-a27b-fb5bf237121a",
  "public_url": "https://r2.cloudflare.com/contracts/2026/01/20/5657db63-7ed1-463f-a27b-fb5bf237121a/contract_nda.pdf",
  "signed_url": "https://r2.cloudflarestorage.com/contracts/.../contract_nda.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&...",
  "signed_url_expires_in": "3600 seconds",
  "metadata": {
    "size": 109766,
    "content_type": "application/pdf",
    "last_modified": "2026-01-20T08:01:43.070370+00:00"
  }
}
```

---

### 4. **GET /api/v1/download-from-r2/**
Download contract directly from R2

**Endpoint:** `GET /api/v1/download-from-r2/?object_key=...`

**Authentication:** Required (Bearer Token)

**Request:**
```bash
curl "http://127.0.0.1:11000/api/v1/download-from-r2/?object_key=contracts/2026/01/20/5657db63-7ed1-463f-a27b-fb5bf237121a/contract_nda.pdf" \
  -H "Authorization: Bearer TOKEN" \
  -o contract.pdf
```

**Response (200 OK):**
```
[Binary PDF Content]
Content-Type: application/pdf
Content-Length: 109766 bytes
```

---

### 5. **DELETE /api/v1/delete-contract-r2/**
Delete contract from Cloudflare R2

**Endpoint:** `DELETE /api/v1/delete-contract-r2/`

**Authentication:** Required (Bearer Token)

**Request:**
```bash
curl -X DELETE http://127.0.0.1:11000/api/v1/delete-contract-r2/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "object_key": "contracts/2026/01/20/5657db63-7ed1-463f-a27b-fb5bf237121a/contract_nda.pdf"
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Contract deleted from R2",
  "object_key": "contracts/2026/01/20/5657db63-7ed1-463f-a27b-fb5bf237121a/contract_nda.pdf"
}
```

---

### 6. **POST /api/v1/archive-contract-r2/**
Archive contract (move to archive folder)

**Endpoint:** `POST /api/v1/archive-contract-r2/`

**Authentication:** Required (Bearer Token)

**Request:**
```bash
curl -X POST http://127.0.0.1:11000/api/v1/archive-contract-r2/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "object_key": "contracts/2026/01/20/5657db63-7ed1-463f-a27b-fb5bf237121a/contract_nda.pdf"
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Contract archived",
  "original_key": "contracts/2026/01/20/5657db63-7ed1-463f-a27b-fb5bf237121a/contract_nda.pdf",
  "archive_key": "archive/2026/01/20/5657db63-7ed1-463f-a27b-fb5bf237121a/contract_nda.pdf"
}
```

---

### 7. **GET /api/v1/r2-stats/**
Get Cloudflare R2 storage statistics

**Endpoint:** `GET /api/v1/r2-stats/`

**Authentication:** Required (Bearer Token)

**Request:**
```bash
curl http://127.0.0.1:11000/api/v1/r2-stats/ \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "success": true,
  "bucket_name": "contracts-production",
  "total_objects": 156,
  "total_size_bytes": 50,
  "total_size_mb": 48.5,
  "total_size_gb": 0.05,
  "storage_limit_gb": 1000,
  "used_percent": 0.005,
  "last_updated": "2026-01-20T08:30:00.000000+00:00"
}
```

---

## 📄 Generate PDF from .txt Template

### **POST /api/v1/txt-to-pdf/**
Generate PDF from filled .txt template

**Endpoint:** `POST /api/v1/txt-to-pdf/`

**Authentication:** Required (Bearer Token)

**Request:**
```bash
curl -X POST http://127.0.0.1:11000/api/v1/txt-to-pdf/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "txt_content": "# Non-Disclosure Agreement\n\nEffective Date: 2026-01-20\n\n# Party Information\nCompany Name: TechCorp Inc\nRecipient Name: John Doe",
    "filename": "contract_nda.pdf",
    "title": "Non-Disclosure Agreement"
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "pdf_url": "https://r2.cloudflare.com/contracts/temp/contract_nda_20260120.pdf",
  "pdf_content": "[Binary PDF - Base64 encoded]",
  "size": 24500,
  "generated_at": "2026-01-20T08:30:00.000000+00:00",
  "message": "PDF generated successfully from template"
}
```

---

## 📋 Sample .txt Templates

### **NDA Template**
```txt
# Non-Disclosure Agreement

Effective Date: 2026-01-20
Term (Months): 12

# Party Information
Company Name: TechCorp Inc
Company Address: 123 Tech Street, San Francisco, CA 94105
Recipient Name: John Doe
Recipient Email: john@example.com

# Agreement Terms
Governing Law: California
Confidential Information: All technical data, business plans, and proprietary information
Additional Terms: Mutual non-disclosure agreement between parties

# Signatures
Company Representative: Jane Smith
Signer Date: 2026-01-20
```

### **Employment Template**
```txt
# Employment Contract

Effective Date: 2026-01-20
Employment Start Date: 2026-02-01

# Employee Information
Employee Name: John Doe
Job Title: Senior Software Engineer
Department: Engineering

# Compensation
Salary: $150,000
Currency: USD
Pay Frequency: Monthly
Vacation Days: 20

# Position Details
Work Location: San Francisco, CA
Reporting To: Engineering Manager

# Terms
Notice Period: 30 Days
Governing Law: California
Confidentiality Terms: All company information is confidential
```

### **Service Template**
```txt
# Service Agreement

Effective Date: 2026-01-20
Service Start Date: 2026-02-01

# Service Provider
Service Provider: ABC Consulting Inc
Client Name: XYZ Corporation

# Service Details
Service Description: Full-stack web development services
Project Price: $50,000
Payment Schedule: Monthly installments

# Deliverables
Deliverables: Fully functional web application
Milestones: Phase 1 (Feb), Phase 2 (Apr), Phase 3 (Jun)
```

---

## 🌐 Production URLs

### **Cloudflare R2 Bucket Access**

| Resource | Type | URL |
|----------|------|-----|
| **Bucket** | R2 | `contracts-production` |
| **CDN URL** | HTTPS | `https://r2.cloudflare.com/contracts/` |
| **Direct URL Example** | HTTPS | `https://r2.cloudflare.com/contracts/2026/01/20/CONTRACT_ID/contract.pdf` |
| **Storage URL** | HTTPS | `https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com/` |
| **Zone** | Cloudflare | Your Zone ID |

### **API Base URLs**

| Environment | URL |
|-------------|-----|
| **Development** | `http://127.0.0.1:11000/api/v1/` |
| **Staging** | `https://staging-clm.yourdomain.com/api/v1/` |
| **Production** | `https://api.yourdomain.com/api/v1/` |

---

## 💾 Storage Structure in Cloudflare R2

```
contracts-production/
├── contracts/
│   └── {YEAR}/{MONTH}/{DAY}/
│       └── {CONTRACT_ID}/
│           ├── contract_nda.pdf
│           ├── contract_employment.pdf
│           └── contract_service.pdf
├── archive/
│   └── {YEAR}/{MONTH}/{DAY}/
│       └── {CONTRACT_ID}/
│           └── contract_*.pdf
├── templates/
│   ├── nda_template.txt
│   ├── employment_template.txt
│   └── service_template.txt
└── backups/
    └── daily/
        └── {DATE}/
            └── backup.zip
```

---

## 🔐 Security Features

### **Access Control**
- ✅ Bucket set to **private** (requires authentication)
- ✅ Signed URLs for temporary access
- ✅ Public URLs for direct sharing
- ✅ API token-based authentication

### **Encryption**
- ✅ HTTPS/TLS in transit
- ✅ Server-side encryption at rest
- ✅ Private keys managed by Cloudflare

### **Audit & Logging**
- ✅ All operations logged
- ✅ Timestamp recorded
- ✅ User tracking
- ✅ Access monitoring

---

## 📊 Example Workflow

### **Complete Upload & Share Flow**

```bash
# Step 1: Create contract
CONTRACT_ID=$(curl -s -X POST http://127.0.0.1:11000/api/v1/create/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"contract_type":"nda","data":{...}}' \
  | jq -r '.contract_id')

# Step 2: Generate PDF from .txt
RESPONSE=$(curl -s -X POST http://127.0.0.1:11000/api/v1/txt-to-pdf/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "txt_content":"# NDA\nCompany: TechCorp\n...",
    "filename":"contract.pdf"
  }')

# Step 3: Upload to R2
curl -s -X POST http://127.0.0.1:11000/api/v1/upload-contract/ \
  -H "Authorization: Bearer TOKEN" \
  -F "contract_id=$CONTRACT_ID" \
  -F "pdf_file=@contract.pdf" \
  -F "contract_type=nda"

# Step 4: Get public URL
curl -s "http://127.0.0.1:11000/api/v1/contract-url/?contract_id=$CONTRACT_ID" \
  -H "Authorization: Bearer TOKEN" \
  | jq '.public_url'

# Step 5: Share with signer
echo "Contract URL: https://r2.cloudflare.com/contracts/2026/01/20/$CONTRACT_ID/contract.pdf"
```

---

## ✅ Verification Checklist

- ✅ Cloudflare R2 bucket configured
- ✅ API endpoints working
- ✅ PDFs generating from .txt
- ✅ Uploads to R2 successful
- ✅ Public URLs accessible
- ✅ Signed URLs generated
- ✅ Storage stats available
- ✅ Archive functionality working

---

## 🎯 Ready for Production

All Cloudflare R2 endpoints are:
- ✅ Tested
- ✅ Documented
- ✅ Secure
- ✅ Scalable
- ✅ Ready to deploy

---

**Last Updated:** 2026-01-20  
**Status:** ✅ Production Ready  
**CDN:** Global Distribution Enabled
