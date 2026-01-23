# 📚 Template Endpoints & Structures Reference

**Complete guide to all template-related endpoints**

---

## 1️⃣ GET /templates/
### List All Available Contract Templates

**Endpoint:** `GET /api/v1/templates/`

**Authentication:** Required (Bearer Token)

**Query Parameters:** None

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
      "description": "Standard NDA to protect confidential information",
      "fields_required": 9,
      "average_pages": 3,
      "signers_needed": 1,
      "created_date": "2026-01-01"
    },
    {
      "id": "employment",
      "name": "Employment Contract",
      "category": "HR",
      "description": "Employment agreement between company and employee",
      "fields_required": 15,
      "average_pages": 5,
      "signers_needed": 1,
      "created_date": "2026-01-05"
    },
    {
      "id": "service",
      "name": "Service Agreement",
      "category": "Legal",
      "description": "Service contract for freelancers and vendors",
      "fields_required": 12,
      "average_pages": 4,
      "signers_needed": 1,
      "created_date": "2026-01-10"
    },
    {
      "id": "agency",
      "name": "Agency Agreement",
      "category": "Business",
      "description": "Agreement between company and agency",
      "fields_required": 12,
      "average_pages": 4,
      "signers_needed": 2,
      "created_date": "2026-01-15"
    }
  ]
}
```

**Error Responses:**

```json
{
  "error": "Authentication credentials were not provided.",
  "status": 401
}
```

---

## 2️⃣ GET /content/
### Get Contract Template Content

**Endpoint:** `GET /api/v1/content/`

**Authentication:** Required (Bearer Token)

**Query Parameters:**
| Parameter | Type | Required | Example |
|-----------|------|----------|---------|
| `contract_type` | string | Yes | `nda`, `employment`, `service`, `agency` |

**Request:**
```bash
curl "http://127.0.0.1:11000/api/v1/content/?contract_type=nda" \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "contract_type": "nda",
  "name": "Non-Disclosure Agreement",
  "content": "THIS NON-DISCLOSURE AGREEMENT (\"NDA\") is entered into as of the Effective Date by and between the disclosing party (\"Discloser\") and the receiving party (\"Recipient\"). WHEREAS, the Discloser wishes to disclose certain confidential information to the Recipient; NOW, THEREFORE, in consideration of the mutual covenants and agreements herein contained, the parties agree as follows:\n\n1. DEFINITIONS\n...",
  "sections": [
    "Definitions",
    "Confidential Information",
    "Obligations",
    "Term",
    "Termination",
    "Miscellaneous"
  ],
  "preview_url": "https://r2.cloudflare.com/contracts/preview-nda.pdf",
  "total_words": 1250,
  "reading_time_minutes": 4
}
```

**Employment Template Content:**
```bash
curl "http://127.0.0.1:11000/api/v1/content/?contract_type=employment"
```

```json
{
  "contract_type": "employment",
  "name": "Employment Contract",
  "content": "EMPLOYMENT AGREEMENT\n\nThis Employment Agreement (\"Agreement\") is entered into as of [DATE] by and between [COMPANY NAME] (\"Employer\") and [EMPLOYEE NAME] (\"Employee\").\n\nWHEREAS, the Employer desires to employ the Employee, and the Employee desires to be employed by the Employer, upon the terms and conditions set forth herein...",
  "sections": [
    "Position & Title",
    "Compensation",
    "Benefits",
    "Term",
    "Duties & Responsibilities",
    "Confidentiality",
    "Non-Compete",
    "Termination"
  ]
}
```

**Service Template Content:**
```bash
curl "http://127.0.0.1:11000/api/v1/content/?contract_type=service"
```

```json
{
  "contract_type": "service",
  "name": "Service Agreement",
  "sections": [
    "Services Provided",
    "Payment Terms",
    "Deliverables",
    "Timeline",
    "Intellectual Property",
    "Liability"
  ]
}
```

**Agency Template Content:**
```bash
curl "http://127.0.0.1:11000/api/v1/content/?contract_type=agency"
```

```json
{
  "contract_type": "agency",
  "name": "Agency Agreement",
  "sections": [
    "Appointment as Agent",
    "Term & Duration",
    "Compensation",
    "Duties & Obligations",
    "Termination",
    "Confidentiality"
  ]
}
```

---

## 3️⃣ GET /contract-templates/ (ViewSet)
### List Template Definitions (Admin View)

**Endpoint:** `GET /api/v1/contract-templates/`

**Authentication:** Required (Bearer Token)

**Query Parameters:**
| Parameter | Type | Example |
|-----------|------|---------|
| `page` | integer | `1` |
| `limit` | integer | `20` |
| `template_type` | string | `nda` |

**Request:**
```bash
curl "http://127.0.0.1:11000/api/v1/contract-templates/?page=1&limit=10" \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "uuid": "template-nda-001",
      "name": "Non-Disclosure Agreement",
      "template_type": "nda",
      "description": "Standard NDA template",
      "content": "THIS NON-DISCLOSURE AGREEMENT...",
      "fields_required": 9,
      "clauses_available": 8,
      "created_at": "2026-01-01T10:00:00Z",
      "updated_at": "2026-01-20T08:00:00Z",
      "is_active": true,
      "version": 2.1
    },
    {
      "id": 2,
      "uuid": "template-employment-001",
      "name": "Employment Contract",
      "template_type": "employment",
      "description": "Employment agreement",
      "fields_required": 15,
      "clauses_available": 12,
      "is_active": true,
      "version": 1.5
    }
  ]
}
```

---

## 4️⃣ POST /contract-templates/ (Create)
### Create New Template (Admin Only)

**Endpoint:** `POST /api/v1/contract-templates/`

**Authentication:** Required (Admin Bearer Token)

**Request:**
```bash
curl -X POST http://127.0.0.1:11000/api/v1/contract-templates/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vendor Agreement",
    "template_type": "vendor",
    "description": "Agreement with vendors",
    "content": "VENDOR AGREEMENT...",
    "fields_required": 10,
    "clauses_available": 5
  }'
```

**Response (201 CREATED):**
```json
{
  "id": 5,
  "uuid": "template-vendor-001",
  "name": "Vendor Agreement",
  "template_type": "vendor",
  "created_at": "2026-01-20T12:00:00Z"
}
```

---

## 5️⃣ GET /contract-templates/{id}/
### Get Single Template Details

**Endpoint:** `GET /api/v1/contract-templates/{id}/`

**Request:**
```bash
curl http://127.0.0.1:11000/api/v1/contract-templates/1/ \
  -H "Authorization: Bearer TOKEN"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "uuid": "template-nda-001",
  "name": "Non-Disclosure Agreement",
  "template_type": "nda",
  "description": "Standard NDA template",
  "content": "THIS NON-DISCLOSURE AGREEMENT...",
  "fields_required": 9,
  "clauses_available": 8,
  "created_at": "2026-01-01T10:00:00Z",
  "updated_at": "2026-01-20T08:00:00Z",
  "is_active": true,
  "version": 2.1
}
```

---

## 📋 Template Fields Reference

### NDA Template (9 Fields)
```json
{
  "contract_type": "nda",
  "fields": [
    {
      "name": "company_name",
      "display_name": "Company Name",
      "type": "text",
      "required": true,
      "max_length": 100,
      "placeholder": "Your company name"
    },
    {
      "name": "company_address",
      "display_name": "Company Address",
      "type": "text",
      "required": true,
      "max_length": 200
    },
    {
      "name": "recipient_name",
      "display_name": "Recipient Name",
      "type": "text",
      "required": true,
      "max_length": 100
    },
    {
      "name": "recipient_email",
      "display_name": "Recipient Email",
      "type": "email",
      "required": true
    },
    {
      "name": "effective_date",
      "display_name": "Effective Date",
      "type": "date",
      "required": true
    },
    {
      "name": "term_months",
      "display_name": "Term (Months)",
      "type": "integer",
      "required": true,
      "min": 1,
      "max": 60
    },
    {
      "name": "governing_law",
      "display_name": "Governing Law",
      "type": "select",
      "required": true,
      "options": ["California", "New York", "Texas", "Federal"]
    },
    {
      "name": "confidential_info",
      "display_name": "Confidential Information Description",
      "type": "textarea",
      "required": true,
      "max_length": 1000
    },
    {
      "name": "additional_terms",
      "display_name": "Additional Terms",
      "type": "textarea",
      "required": false,
      "max_length": 2000
    }
  ]
}
```

### Employment Template (15 Fields)
```json
{
  "contract_type": "employment",
  "fields": [
    {"name": "employee_name", "type": "text", "required": true},
    {"name": "job_title", "type": "text", "required": true},
    {"name": "department", "type": "text", "required": true},
    {"name": "start_date", "type": "date", "required": true},
    {"name": "employment_type", "type": "select", "required": true, "options": ["Full-time", "Part-time", "Contract"]},
    {"name": "salary", "type": "number", "required": true},
    {"name": "currency", "type": "select", "required": true, "options": ["USD", "EUR", "GBP"]},
    {"name": "pay_frequency", "type": "select", "required": true, "options": ["Monthly", "Bi-weekly", "Weekly"]},
    {"name": "work_location", "type": "text", "required": true},
    {"name": "reporting_to", "type": "text", "required": true},
    {"name": "vacation_days", "type": "integer", "required": true},
    {"name": "benefits", "type": "textarea", "required": false},
    {"name": "confidentiality_terms", "type": "textarea", "required": true},
    {"name": "notice_period", "type": "integer", "required": true},
    {"name": "governing_law", "type": "select", "required": true}
  ]
}
```

### Service Template (12 Fields)
```json
{
  "contract_type": "service",
  "fields": [
    {"name": "service_provider", "type": "text", "required": true},
    {"name": "client_name", "type": "text", "required": true},
    {"name": "service_description", "type": "textarea", "required": true},
    {"name": "start_date", "type": "date", "required": true},
    {"name": "end_date", "type": "date", "required": true},
    {"name": "project_price", "type": "number", "required": true},
    {"name": "payment_schedule", "type": "select", "required": true},
    {"name": "deliverables", "type": "textarea", "required": true},
    {"name": "milestones", "type": "textarea", "required": false},
    {"name": "intellectual_property", "type": "select", "required": true},
    {"name": "confidentiality", "type": "checkbox", "required": true},
    {"name": "termination_clause", "type": "textarea", "required": false}
  ]
}
```

### Agency Template (12 Fields)
```json
{
  "contract_type": "agency",
  "fields": [
    {"name": "principal_name", "type": "text", "required": true},
    {"name": "agent_name", "type": "text", "required": true},
    {"name": "agency_scope", "type": "textarea", "required": true},
    {"name": "term_start", "type": "date", "required": true},
    {"name": "term_end", "type": "date", "required": true},
    {"name": "commission_rate", "type": "number", "required": true},
    {"name": "exclusive_territory", "type": "text", "required": false},
    {"name": "responsibilities", "type": "textarea", "required": true},
    {"name": "termination_notice", "type": "integer", "required": true},
    {"name": "governing_law", "type": "select", "required": true},
    {"name": "dispute_resolution", "type": "select", "required": true},
    {"name": "additional_terms", "type": "textarea", "required": false}
  ]
}
```

---

## 🎯 Frontend Implementation

### Step 1: Load Templates
```javascript
// Get list of available templates
fetch('/api/v1/templates/', {
  headers: {'Authorization': `Bearer ${token}`}
})
.then(r => r.json())
.then(data => {
  // Show templates in dropdown
  data.templates.forEach(t => {
    console.log(`${t.name} (${t.fields_required} fields)`);
  });
});
```

### Step 2: Get Template Fields
```javascript
// Get fields for selected template
const contractType = 'nda';
fetch(`/api/v1/fields/?contract_type=${contractType}`, {
  headers: {'Authorization': `Bearer ${token}`}
})
.then(r => r.json())
.then(data => {
  // Generate form from fields
  data.fields.forEach(field => {
    // Create input based on field.type
  });
});
```

### Step 3: Show Template Preview
```javascript
// Get preview content
fetch(`/api/v1/content/?contract_type=nda`, {
  headers: {'Authorization': `Bearer ${token}`}
})
.then(r => r.json())
.then(data => {
  // Show preview text
  document.getElementById('preview').innerHTML = data.content;
});
```

---

**Status:** ✅ Production Ready  
**Last Updated:** 2026-01-20  
**Total Templates:** 4 (NDA, Employment, Service, Agency)
