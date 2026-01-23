# 📚 Complete Contract API Endpoints (10+ Endpoints)

**Base URL:** `http://127.0.0.1:11000/api/v1/`  
**Authentication:** Bearer Token (JWT)  
**Content-Type:** `application/json`

---

## 🎯 Core Contract Endpoints (8 Main)

### 1. **GET /templates/**
List all available contract templates

**Request:**
```bash
curl http://127.0.0.1:11000/api/v1/templates/ \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "success": true,
  "templates": [
    {
      "id": "nda",
      "name": "Non-Disclosure Agreement",
      "category": "Legal",
      "description": "Standard NDA template",
      "fields_required": 9
    },
    {
      "id": "employment",
      "name": "Employment Contract",
      "category": "HR",
      "description": "Employment agreement template",
      "fields_required": 15
    },
    {
      "id": "service",
      "name": "Service Agreement",
      "category": "Legal",
      "description": "Service contract template",
      "fields_required": 12
    }
  ]
}
```

---

### 2. **GET /fields/**
Get required fields for a specific contract template

**Request:**
```bash
curl "http://127.0.0.1:11000/api/v1/fields/?contract_type=nda" \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "contract_type": "nda",
  "fields": [
    {
      "name": "company_name",
      "type": "text",
      "required": true,
      "max_length": 100
    },
    {
      "name": "company_address",
      "type": "text",
      "required": true,
      "max_length": 200
    },
    {
      "name": "effective_date",
      "type": "date",
      "required": true
    },
    {
      "name": "term_months",
      "type": "integer",
      "required": true
    }
  ]
}
```

---

### 3. **GET /content/**
Get template content/preview

**Request:**
```bash
curl "http://127.0.0.1:11000/api/v1/content/?contract_type=nda" \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "contract_type": "nda",
  "content": "This Non-Disclosure Agreement (\"NDA\") is entered into...",
  "sections": ["Definitions", "Obligations", "Term", "Termination"],
  "preview_url": "https://r2.cloudflare.com/contracts/preview-nda.pdf"
}
```

---

### 4. **POST /create/**
Create a new contract (Main endpoint)

**Request:**
```bash
curl -X POST http://127.0.0.1:11000/api/v1/create/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_type": "nda",
    "data": {
      "company_name": "TechCorp Inc",
      "company_address": "123 Tech Street",
      "effective_date": "2026-01-20",
      "term_months": 12,
      "recipient_name": "John Doe",
      "recipient_email": "john@example.com",
      "jurisdiction": "California"
    }
  }'
```

**Response (201 CREATED):**
```json
{
  "success": true,
  "contract_id": "5657db63-7ed1-463f-a27b-fb5bf237121a",
  "file_path": "https://r2.cloudflare.com/contracts/contract_nda_43caaa8f.pdf",
  "file_size": 109766,
  "template_used": "nda",
  "fields_filled": 9,
  "created_at": "2026-01-20T08:01:43.070370+00:00",
  "message": "Contract generated successfully with 9 fields filled"
}
```

---

### 5. **GET /details/**
Get contract details and status

**Request:**
```bash
curl "http://127.0.0.1:11000/api/v1/details/?contract_id=5657db63-7ed1-463f-a27b-fb5bf237121a" \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "id": "5657db63-7ed1-463f-a27b-fb5bf237121a",
  "title": "NDA - 2026-01-20",
  "contract_type": "nda",
  "status": "draft",
  "description": "Auto-generated nda contract",
  "clauses": [],
  "signed": {
    "status": "awaiting_signature",
    "pending_signer": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  },
  "file_path": "https://r2.cloudflare.com/contracts/contract_nda_43caaa8f.pdf",
  "file_size": 109766,
  "created_at": "2026-01-20T08:01:43.070370+00:00",
  "updated_at": "2026-01-20T08:01:48.871535+00:00"
}
```

---

### 6. **GET /download/**
Download contract PDF

**Request:**
```bash
curl "http://127.0.0.1:11000/api/v1/download/?contract_id=5657db63-7ed1-463f-a27b-fb5bf237121a" \
  -H "Authorization: Bearer TOKEN" \
  -o contract.pdf
```

**Response (200 OK):**
```
[Binary PDF content]
Content-Type: application/pdf
Content-Length: 109766 bytes
```

---

### 7. **POST /send-to-signnow/**
Send contract to SignNow for signature

**Request:**
```bash
curl -X POST http://127.0.0.1:11000/api/v1/send-to-signnow/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "5657db63-7ed1-463f-a27b-fb5bf237121a",
    "signer_email": "john@example.com",
    "signer_name": "John Doe"
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "contract_id": "5657db63-7ed1-463f-a27b-fb5bf237121a",
  "signing_link": "https://app.signnow.com/sign/5657db63-7ed1-463f-a27b-fb5bf237121a",
  "message": "Send link to John Doe. They will type/draw signature and sign.",
  "next_step": "user_signs",
  "expires_in": "30 days"
}
```

---

### 8. **POST /webhook/signnow/**
Webhook endpoint for SignNow signature callback

**Request (from SignNow):**
```bash
curl -X POST http://127.0.0.1:11000/api/v1/webhook/signnow/ \
  -H "Content-Type: application/json" \
  -d '{
    "event": "document.signed",
    "document_id": "5657db63-7ed1-463f-a27b-fb5bf237121a",
    "signer": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Signature received and processed",
  "contract_id": "5657db63-7ed1-463f-a27b-fb5bf237121a",
  "signed_at": "2026-01-20T08:05:12.123456+00:00"
}
```

---

## 🏗️ Advanced Endpoints (ViewSet CRUD)

### 9. **GET /contract-templates/** (ViewSet)
List all contract template definitions

**Request:**
```bash
curl http://127.0.0.1:11000/api/v1/contract-templates/ \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Non-Disclosure Agreement",
      "template_type": "nda",
      "content": "...",
      "created_at": "2026-01-01"
    }
  ]
}
```

---

### 10. **GET /contracts/** (ViewSet)
List all generated contracts (paginated)

**Request:**
```bash
curl "http://127.0.0.1:11000/api/v1/contracts/?page=1&limit=20" \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "count": 45,
  "next": "http://127.0.0.1:11000/api/v1/contracts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "5657db63-7ed1-463f-a27b-fb5bf237121a",
      "title": "NDA - 2026-01-20",
      "contract_type": "nda",
      "status": "signed",
      "created_at": "2026-01-20T08:01:43.070370+00:00"
    }
  ]
}
```

---

### 11. **GET /clauses/** (ViewSet)
List available contract clauses

**Request:**
```bash
curl "http://127.0.0.1:11000/api/v1/clauses/?contract_type=nda" \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "title": "Confidentiality",
      "description": "Defines what is confidential",
      "category": "core"
    },
    {
      "id": 2,
      "title": "Term",
      "description": "Duration of agreement",
      "category": "core"
    }
  ]
}
```

---

### 12. **GET /generation-jobs/** (ViewSet)
List contract generation jobs (for tracking async operations)

**Request:**
```bash
curl "http://127.0.0.1:11000/api/v1/generation-jobs/?status=completed" \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "count": 12,
  "results": [
    {
      "id": "job-123",
      "contract_id": "5657db63-7ed1-463f-a27b-fb5bf237121a",
      "status": "completed",
      "started_at": "2026-01-20T08:01:40",
      "completed_at": "2026-01-20T08:01:43"
    }
  ]
}
```

---

## 📊 Status Codes Reference

| Code | Meaning |
|------|---------|
| 200 | OK - Success |
| 201 | Created - New resource created |
| 400 | Bad Request - Invalid data |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - No permission |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error |

---

## 🔐 Authentication

All endpoints (except webhook) require Bearer token:

```bash
Authorization: Bearer <your-jwt-token>
```

Get token:
```bash
curl -X POST http://127.0.0.1:11000/api/auth/token/ \
  -d '{"username": "user", "password": "pass"}'
```

---

## 💾 Cloudflare R2 Storage Integration

All contracts are stored in **Cloudflare R2**:
- 📁 Bucket: `contracts-production`
- 🔗 URLs: `https://r2.cloudflare.com/contracts/...`
- 🔒 Automatic backup every 24 hours
- ⚡ CDN acceleration enabled

**Storage Structure:**
```
contracts-production/
├── contract_nda_*.pdf
├── contract_employment_*.pdf
├── contract_service_*.pdf
└── archive/
    └── 2026-01/
```

---

## ✅ Test Coverage

- ✅ All 12+ endpoints tested
- ✅ Authentication verified
- ✅ Error handling validated
- ✅ Cloudflare R2 integration confirmed
- ✅ SignNow webhook functional
- ✅ PDF generation working
- ✅ Contract lifecycle (draft → signed → archived)

---

## 🚀 Quick Start

```bash
# 1. List templates
curl http://127.0.0.1:11000/api/v1/templates/ -H "Authorization: Bearer TOKEN"

# 2. Create contract
curl -X POST http://127.0.0.1:11000/api/v1/create/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"contract_type":"nda","data":{...}}'

# 3. Send for signature
curl -X POST http://127.0.0.1:11000/api/v1/send-to-signnow/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"contract_id":"...","signer_email":"..."}'

# 4. Download signed PDF
curl http://127.0.0.1:11000/api/v1/download/?contract_id=... \
  -H "Authorization: Bearer TOKEN" -o contract.pdf
```

---

**Last Updated:** 2026-01-20  
**Status:** ✅ Production Ready  
**Total Endpoints:** 12+
