# 📋 All Contract & Template Endpoints - Complete Reference

## Overview
This document lists **ALL endpoints** available in the CLM Backend, including the new Cloudflare R2 upload endpoints.

---

## 🆕 New Cloudflare R2 Upload Endpoints

### 1. Upload Any Document
```http
POST /api/contracts/upload-document/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- file: Document file [REQUIRED]
- filename: Custom filename [OPTIONAL]

Response:
{
  "success": true,
  "r2_key": "tenant-id/contracts/uuid.pdf",
  "download_url": "https://...",
  "file_size": 123456,
  "uploaded_at": "2026-01-20T12:00:00Z"
}
```

### 2. Upload Contract Document with Record
```http
POST /api/contracts/upload-contract-document/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- file: Contract file [REQUIRED]
- create_contract: Boolean [OPTIONAL, default: false]
- title: Contract title [OPTIONAL]
- contract_type: Contract type [OPTIONAL]
- counterparty: Counterparty name [OPTIONAL]

Response:
{
  "success": true,
  "contract_id": "uuid",
  "r2_key": "tenant-id/contracts/uuid.pdf",
  "download_url": "https://...",
  "contract_title": "My Contract",
  "contract_status": "draft"
}
```

### 3. Get Download URL by R2 Key
```http
GET /api/contracts/document-download-url/?r2_key=<key>&expiration=3600
Authorization: Bearer <token>

Response:
{
  "success": true,
  "download_url": "https://...",
  "expiration_seconds": 3600
}
```

### 4. Get Contract Download URL by ID
```http
GET /api/contracts/<contract_id>/download-url/
Authorization: Bearer <token>

Response:
{
  "success": true,
  "contract_id": "uuid",
  "contract_title": "My Contract",
  "version_number": 1,
  "download_url": "https://..."
}
```

---

## 📄 Contract Endpoints (Existing - Enhanced with R2)

### 5. List All Contracts
```http
GET /api/contracts/contracts/
Authorization: Bearer <token>

Response:
[
  {
    "id": "uuid",
    "title": "Service Agreement",
    "contract_type": "service_agreement",
    "status": "draft",
    "created_at": "2026-01-20T12:00:00Z"
  }
]
```

### 6. Create Contract
```http
POST /api/contracts/contracts/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- title: Contract title [REQUIRED]
- contract_type: Type [REQUIRED]
- file: Document file [OPTIONAL] → Auto-uploaded to R2 if provided
- status: Status [OPTIONAL]
- counterparty: Counterparty [OPTIONAL]
- value: Contract value [OPTIONAL]

Response:
{
  "id": "uuid",
  "title": "Service Agreement",
  "status": "draft",
  "created_at": "2026-01-20T12:00:00Z"
}
```
**Note:** If `file` is uploaded, it's automatically stored in Cloudflare R2 and a ContractVersion is created!

### 7. Get Contract Details
```http
GET /api/contracts/contracts/<id>/
Authorization: Bearer <token>

Response:
{
  "id": "uuid",
  "title": "Service Agreement",
  "contract_type": "service_agreement",
  "status": "draft",
  "counterparty": "Acme Corp",
  "value": "50000.00",
  "start_date": "2026-01-01",
  "end_date": "2026-12-31",
  "created_at": "2026-01-20T12:00:00Z"
}
```

### 8. Update Contract
```http
PATCH /api/contracts/contracts/<id>/
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "title": "Updated Title",
  "status": "approved",
  "value": "60000.00"
}
```

### 9. Delete Contract
```http
DELETE /api/contracts/contracts/<id>/
Authorization: Bearer <token>
```

---

## 🎯 Contract Generation Endpoints

### 10. Generate Contract from Template
```http
POST /api/contracts/contracts/generate/
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "template_id": "uuid",
  "structured_inputs": {
    "counterparty": "Acme Corp",
    "value": 5000000,
    "start_date": "2026-01-01",
    "end_date": "2026-12-31"
  },
  "title": "MSA with Acme Corp",
  "selected_clauses": ["CONF-001", "TERM-001"]
}

Response:
{
  "contract": {...},
  "version": {...},
  "mandatory_clauses": [...],
  "clause_suggestions": {...}
}
```

### 11. Get Contract Versions
```http
GET /api/contracts/contracts/<id>/versions/
Authorization: Bearer <token>

Response:
[
  {
    "id": "uuid",
    "version_number": 1,
    "r2_key": "tenant-id/contracts/uuid.pdf",
    "change_summary": "Initial upload",
    "created_at": "2026-01-20T12:00:00Z"
  }
]
```

### 12. Create New Version
```http
POST /api/contracts/contracts/<id>/new-version/
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "changes": {...},
  "change_summary": "Updated contract terms"
}
```

---

## 📝 Template Endpoints

### 13. List Contract Templates
```http
GET /api/contracts/contract-templates/
Authorization: Bearer <token>

Response:
[
  {
    "id": "uuid",
    "name": "Standard NDA Template",
    "contract_type": "nda",
    "status": "published",
    "version": 1
  }
]
```

### 14. Get Template Details
```http
GET /api/contracts/contract-templates/<id>/
Authorization: Bearer <token>

Response:
{
  "id": "uuid",
  "name": "Standard NDA Template",
  "contract_type": "nda",
  "description": "Standard non-disclosure agreement",
  "merge_fields": ["party1_name", "party2_name", "effective_date"],
  "mandatory_clauses": ["CONF-001"],
  "status": "published"
}
```

### 15. Create Template
```http
POST /api/contracts/contract-templates/
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "name": "Custom NDA",
  "contract_type": "nda",
  "description": "Custom NDA template",
  "merge_fields": ["party1_name", "party2_name"],
  "status": "published"
}
```

### 16. Get Supported Template Types
```http
GET /api/contracts/templates/
Authorization: Bearer <token>

Response:
{
  "supported_types": [
    "nda",
    "agency_agreement",
    "property_management",
    "employment_contract",
    "service_agreement"
  ],
  "templates": [...]
}
```

---

## 🔤 Clause Endpoints

### 17. List Clauses
```http
GET /api/contracts/clauses/
Authorization: Bearer <token>

Query Parameters:
- contract_type: Filter by contract type [OPTIONAL]

Response:
[
  {
    "id": "uuid",
    "clause_id": "CONF-001",
    "name": "Confidentiality Clause",
    "version": 1,
    "contract_type": "nda",
    "content": "The parties agree to...",
    "is_mandatory": true,
    "status": "published"
  }
]
```

### 18. Get Clause Details
```http
GET /api/contracts/clauses/<id>/
Authorization: Bearer <token>

Response:
{
  "id": "uuid",
  "clause_id": "CONF-001",
  "name": "Confidentiality Clause",
  "content": "Full clause text...",
  "alternatives": ["CONF-002", "CONF-003"],
  "tags": ["confidentiality", "security"]
}
```

### 19. Get Clause Alternatives
```http
POST /api/contracts/clauses/<id>/alternatives/
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "contract_type": "MSA",
  "contract_value": 5000000,
  "counterparty": "Acme Corp"
}

Response:
{
  "alternatives": [
    {
      "clause_id": "CONF-002",
      "name": "Strict Confidentiality",
      "rationale": "Higher value contracts require stricter terms",
      "confidence": 0.92
    }
  ]
}
```

---

## 📊 Statistics & Reports

### 20. Get Contract Statistics
```http
GET /api/contracts/contracts/statistics/
Authorization: Bearer <token>

Response:
{
  "total": 150,
  "by_status": {
    "draft": 45,
    "pending": 30,
    "approved": 50,
    "executed": 25
  },
  "monthly_trends": [...]
}
```

### 21. Get Recent Contracts
```http
GET /api/contracts/contracts/recent/?limit=10
Authorization: Bearer <token>

Response:
[
  {
    "id": "uuid",
    "title": "Service Agreement",
    "status": "draft",
    "created_at": "2026-01-20T12:00:00Z",
    "created_by_name": "John Doe"
  }
]
```

---

## ✅ Approval & Workflow

### 22. Approve Contract
```http
POST /api/contracts/contracts/<id>/approve/
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "comments": "Approved with minor revisions"
}

Response:
{
  "id": "uuid",
  "status": "approved",
  "approved_by": "user-uuid",
  "approved_at": "2026-01-20T12:00:00Z"
}
```

### 23. Get Contract History
```http
GET /api/contracts/contracts/<id>/history/
Authorization: Bearer <token>

Response:
[
  {
    "action": "created",
    "user": "John Doe",
    "timestamp": "2026-01-20T10:00:00Z"
  },
  {
    "action": "approved",
    "user": "Jane Smith",
    "timestamp": "2026-01-20T15:00:00Z"
  }
]
```

---

## 📥 Legacy Contract Generation (Still Works)

### 24. Create Contract from Form
```http
POST /api/contracts/create/
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "contract_type": "nda",
  "data": {
    "date": "2026-01-20",
    "1st_party_name": "Company A",
    "2nd_party_name": "Company B",
    "clauses": [
      {"name": "Confidentiality", "description": "..."}
    ]
  }
}

Response:
{
  "success": true,
  "contract_id": "uuid",
  "file_path": "/path/to/contract.pdf",
  "file_size": 123456,
  "created_at": "2026-01-20T12:00:00Z"
}
```

### 25. Get Contract Fields
```http
GET /api/contracts/fields/?contract_type=nda
Authorization: Bearer <token>

Response:
{
  "contract_type": "nda",
  "required_fields": ["date", "1st_party_name", "2nd_party_name"],
  "optional_fields": ["effective_date", "termination_date"],
  "signature_fields": ["1st_party_signature", "2nd_party_signature"],
  "example": {...}
}
```

### 26. Download Contract PDF (Legacy)
```http
GET /api/contracts/download/?contract_id=<id>
Authorization: Bearer <token>

Response: Binary PDF file
```

### 27. Get Contract Details (Legacy)
```http
GET /api/contracts/details/?contract_id=<id>
Authorization: Bearer <token>

Response:
{
  "success": true,
  "contract": {
    "id": "uuid",
    "title": "NDA - 2026-01-20",
    "contract_type": "nda",
    "status": "draft",
    "file_path": "/path/to/contract.pdf",
    "file_size": 123456
  },
  "download_url": "/api/contracts/download/?contract_id=uuid"
}
```

---

## 🔐 SignNow Integration

### 28. Send to SignNow
```http
POST /api/contracts/send-to-signnow/
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "contract_id": "uuid",
  "signers": [
    {
      "name": "John Doe",
      "email": "john@example.com",
      "order": 1
    }
  ]
}

Response:
{
  "success": true,
  "esignature_contract_id": "uuid",
  "signnow_document_id": "signnow-doc-id",
  "signing_link": "https://signnow.com/..."
}
```

### 29. SignNow Webhook (Callback)
```http
POST /api/contracts/webhook/signnow/
Content-Type: application/json

Body: SignNow callback payload
```

---

## 🎯 Summary: All Endpoints

### Cloudflare R2 Uploads (New) - 4 endpoints
- `POST /api/contracts/upload-document/`
- `POST /api/contracts/upload-contract-document/`
- `GET /api/contracts/document-download-url/`
- `GET /api/contracts/<id>/download-url/`

### Contract Management - 11 endpoints
- `GET /api/contracts/contracts/`
- `POST /api/contracts/contracts/`
- `GET /api/contracts/contracts/<id>/`
- `PATCH /api/contracts/contracts/<id>/`
- `DELETE /api/contracts/contracts/<id>/`
- `POST /api/contracts/contracts/generate/`
- `GET /api/contracts/contracts/<id>/versions/`
- `POST /api/contracts/contracts/<id>/new-version/`
- `POST /api/contracts/contracts/<id>/approve/`
- `GET /api/contracts/contracts/<id>/history/`
- `GET /api/contracts/contracts/statistics/`

### Templates & Clauses - 7 endpoints
- `GET /api/contracts/contract-templates/`
- `GET /api/contracts/contract-templates/<id>/`
- `POST /api/contracts/contract-templates/`
- `GET /api/contracts/templates/`
- `GET /api/contracts/clauses/`
- `GET /api/contracts/clauses/<id>/`
- `POST /api/contracts/clauses/<id>/alternatives/`

### Legacy Generation - 4 endpoints
- `POST /api/contracts/create/`
- `GET /api/contracts/fields/`
- `GET /api/contracts/download/`
- `GET /api/contracts/details/`

### SignNow - 2 endpoints
- `POST /api/contracts/send-to-signnow/`
- `POST /api/contracts/webhook/signnow/`

**Total: 28 Endpoints**

---

## 🚀 Key Features

✅ **Cloudflare R2 Storage** - All documents automatically uploaded  
✅ **Presigned URLs** - Secure, temporary download links  
✅ **Version Tracking** - Full contract version history  
✅ **Template System** - Reusable contract templates  
✅ **Clause Library** - Smart clause suggestions  
✅ **Approval Workflow** - Multi-stage approval process  
✅ **E-Signature** - SignNow integration  
✅ **Audit Logs** - Complete change history  
✅ **Tenant Isolation** - Multi-tenant secure storage  

---

**Last Updated:** January 20, 2026  
**API Version:** v1  
**Base URL:** `http://localhost:11000` (Development)

For detailed documentation on each endpoint, see:
- [CLOUDFLARE_R2_INTEGRATION.md](./CLOUDFLARE_R2_INTEGRATION.md) - R2 upload details
- [README.md](./README.md) - General API documentation
- [R2_QUICK_START.md](./R2_QUICK_START.md) - Quick start guide
