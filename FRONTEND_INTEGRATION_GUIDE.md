# Frontend Integration Guide - Contract Generation API

Complete guide for integrating contract generation, templates, and e-signature flows in your frontend application.

## Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Complete Workflow](#complete-workflow)
4. [Endpoint Reference](#endpoint-reference)
5. [Error Handling](#error-handling)
6. [Code Examples](#code-examples)
7. [State Management](#state-management)

---

## API Overview

**Base URL**: `http://your-domain/api/v1`

**Default Port (Development)**: `http://127.0.0.1:11000/api/v1`

**Authentication**: JWT Bearer Token (required for all endpoints except webhook)

**Response Format**: JSON with `success` flag and structured data

---

## Authentication

All endpoints (except webhook) require JWT authentication:

```javascript
const headers = {
  'Authorization': `Bearer ${JWT_TOKEN}`,
  'Content-Type': 'application/json'
};
```

Where `JWT_TOKEN` is obtained from your authentication service.

---

## Complete Workflow

### Phase 1: Template Selection (Frontend)

```
User Opens App
    ↓
[GET] /api/v1/templates/
    ↓
Display: List of contract types
    ↓
User Selects Type (NDA, Employment, etc.)
```

### Phase 2: Form Filling (Frontend)

```
User Selects Contract Type
    ↓
[GET] /api/v1/fields/?contract_type=nda
    ↓
Display: Form with required fields
    ↓
User Fills Form + Adds Clauses (Optional)
    ↓
Preview: [GET] /api/v1/content/?contract_type=nda
```

### Phase 3: Contract Creation (Backend)

```
User Submits Form
    ↓
[POST] /api/v1/create/
    ↓
Backend: Generates PDF
Backend: Stores in database
    ↓
Response: Contract ID + File details
    ↓
Display: Success message + Download button
```

### Phase 4: Download & Share (User Action)

```
User Clicks Download
    ↓
[GET] /api/v1/download/?contract_id={id}
    ↓
Download: PDF file
    ↓
User Shares Link: "Send to Signer"
    ↓
Copy & Email: SignNow signing link
```

### Phase 5: E-Signature Request (Backend)

```
User Enters Signer Details
    ↓
[POST] /api/v1/send-to-signnow/
    ↓
Backend: Prepares for signing
    ↓
Response: Signing link
    ↓
Display: Link to copy/share
```

### Phase 6: Signer Signs (External - SignNow)

```
Signer Receives Link
    ↓
Opens: SignNow app/web
    ↓
Types/Draws: Signature
    ↓
Clicks: Sign button
    ↓
SignNow: Calls webhook
```

### Phase 7: Signature Received (Backend)

```
[POST] /api/v1/webhook/signnow/
    ↓
Backend: Stores signature + PDF
Backend: Updates contract status
    ↓
Contract: Now marked as "signed"
```

### Phase 8: View Signed Contract (User)

```
User Checks: Contract status
    ↓
[GET] /api/v1/details/?contract_id={id}
    ↓
Display: Signer name, timestamp
    ↓
Download: [GET] /api/v1/download/?contract_id={id}
    ↓
File: Signed PDF with signature
```

---

## Endpoint Reference

### 1. List All Templates

```http
GET /api/v1/templates/
Authorization: Bearer {JWT_TOKEN}
```

**Response (200)**:
```json
{
  "success": true,
  "templates": {
    "nda": {
      "required_fields_count": 8,
      "optional_fields_count": 3
    },
    "agency_agreement": {
      "required_fields_count": 6,
      "optional_fields_count": 4
    },
    "property_management": {
      "required_fields_count": 7,
      "optional_fields_count": 5
    },
    "employment_contract": {
      "required_fields_count": 5,
      "optional_fields_count": 6
    }
  },
  "total_supported": 4
}
```

**Frontend Use**: Show dropdown/cards of contract types

---

### 2. Get Contract Fields

```http
GET /api/v1/fields/?contract_type=nda
Authorization: Bearer {JWT_TOKEN}
```

**Response (200)**:
```json
{
  "success": true,
  "contract_type": "nda",
  "required_fields": [
    "date",
    "1st_party_name",
    "2nd_party_name",
    "agreement_type",
    "governing_law"
  ],
  "optional_fields": [
    "1st_party_address",
    "2nd_party_address",
    "additional_terms"
  ],
  "signature_fields": [
    "1st_party_printed_name",
    "2nd_party_printed_name"
  ]
}
```

**Frontend Use**: Render form with required/optional sections

---

### 3. Get Template Content

```http
GET /api/v1/content/?contract_type=nda
Authorization: Bearer {JWT_TOKEN}
```

**Response (200)**:
```json
{
  "success": true,
  "contract_type": "nda",
  "title": "Non-Disclosure Agreement",
  "required_fields": [...],
  "full_content": "This Non-Disclosure Agreement ('NDA') is entered into on [date]...",
  "content_length": 2500
}
```

**Frontend Use**: Display in preview modal/panel

---

### 4. Create Contract

```http
POST /api/v1/create/
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "contract_type": "nda",
  "data": {
    "date": "2026-01-20",
    "1st_party_name": "Company A",
    "2nd_party_name": "Company B",
    "agreement_type": "Mutual",
    "1st_party_relationship": "Technology",
    "2nd_party_relationship": "Software",
    "governing_law": "California",
    "1st_party_printed_name": "John",
    "2nd_party_printed_name": "Jane",
    "clauses": [
      {
        "name": "Confidentiality",
        "description": "Info remains confidential"
      }
    ]
  }
}
```

**Response (201)**:
```json
{
  "success": true,
  "contract_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_path": "/Users/.../generated_contracts/contract_nda_abc12345.pdf",
  "file_size": 109766,
  "template_used": "nda",
  "fields_filled": 8,
  "created_at": "2026-01-20T15:30:45Z",
  "message": "Contract generated successfully with 8 fields filled"
}
```

**Frontend Use**: Store `contract_id`, show success + download button

---

### 5. Get Contract Details

```http
GET /api/v1/details/?contract_id={contract_id}
Authorization: Bearer {JWT_TOKEN}
```

**Response (200)**:
```json
{
  "success": true,
  "contract": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "NDA - 2026-01-20",
    "contract_type": "nda",
    "status": "draft",
    "clauses": [
      {
        "name": "Confidentiality",
        "description": "Info remains confidential"
      }
    ],
    "signed": {
      "status": "signed",
      "signers": [
        {
          "name": "Jane Doe",
          "email": "jane@example.com",
          "signature_text": "Jane Doe",
          "signed_at": "2026-01-20T16:45:30Z"
        }
      ],
      "signed_at": "2026-01-20T16:45:30Z",
      "pdf_signed": true,
      "pdf_size_bytes": 115000
    },
    "file_size": 109766,
    "created_at": "2026-01-20T15:30:45Z"
  },
  "download_url": "/api/v1/download/?contract_id={id}"
}
```

**Frontend Use**: Display contract info, signer details, status

---

### 6. Download Contract

```http
GET /api/v1/download/?contract_id={contract_id}
Authorization: Bearer {JWT_TOKEN}
```

**Response (200)**:
```
[Binary PDF content]
Content-Type: application/pdf
Content-Disposition: attachment; filename="contract_nda_abc12345.pdf"
```

**Frontend Use**: Download file directly in browser

---

### 7. Send to SignNow

```http
POST /api/v1/send-to-signnow/
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "contract_id": "550e8400-e29b-41d4-a716-446655440000",
  "signer_email": "jane.doe@company.com",
  "signer_name": "Jane Doe"
}
```

**Response (200)**:
```json
{
  "contract_id": "550e8400-e29b-41d4-a716-446655440000",
  "signing_link": "https://app.signnow.com/sign/abc123def456",
  "message": "Send link to Jane Doe. They will type/draw signature and sign.",
  "next_step": "user_signs",
  "user_action": "Click link → Type/Draw signature → Click Sign"
}
```

**Frontend Use**: Display link, allow copy/email

---

### 8. SignNow Webhook

```http
POST /api/v1/webhook/signnow/
[No authentication required - internal service call]
Content-Type: application/json

{
  "event": "document.signed",
  "document": {
    "contract_id": "550e8400-e29b-41d4-a716-446655440000",
    "signed_at": "2026-01-20T16:45:30Z",
    "signed_pdf_url": "https://signnow-cdn.s3.amazonaws.com/signed_doc.pdf",
    "signers": [
      {
        "full_name": "Jane Doe",
        "email": "jane.doe@company.com",
        "signed_at": "2026-01-20T16:45:30Z"
      }
    ]
  }
}
```

**Response (200)**:
```json
{
  "status": "received",
  "contract_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Signature received from Jane Doe. Contract is now signed."
}
```

**Backend Use**: Server-to-server communication (handled by SignNow service)

---

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "message": "Detailed description"
}
```

### Common Errors

#### 400 - Bad Request (Missing Fields)

```json
{
  "success": false,
  "error": "Missing required fields",
  "missing_fields": ["1st_party_name", "2nd_party_name"],
  "required_fields": ["date", "1st_party_name", "2nd_party_name", ...]
}
```

**Frontend Handle**: Show form validation errors

#### 400 - Unsupported Contract Type

```json
{
  "success": false,
  "error": "Unsupported contract type: invalid_type",
  "supported_types": ["nda", "agency_agreement", "property_management", "employment_contract"]
}
```

#### 404 - Not Found

```json
{
  "success": false,
  "error": "Contract not found: invalid-id"
}
```

#### 401 - Unauthorized

```json
{
  "success": false,
  "error": "Invalid or expired token"
}
```

**Frontend Handle**: Redirect to login

#### 500 - Internal Server Error

```json
{
  "success": false,
  "error": "Internal server error details",
  "message": "Failed to generate contract"
}
```

---

## Code Examples

### JavaScript/React

#### 1. Fetch Templates

```javascript
async function loadTemplates() {
  try {
    const response = await fetch('/api/v1/templates/', {
      headers: {
        'Authorization': `Bearer ${TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) throw new Error('Failed to load templates');
    
    const data = await response.json();
    setTemplates(data.templates);
    
  } catch (error) {
    console.error('Error:', error);
    setError('Failed to load templates');
  }
}
```

#### 2. Create Contract

```javascript
async function createContract(contractType, formData) {
  try {
    const response = await fetch('/api/v1/create/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        contract_type: contractType,
        data: formData,
        send_for_esignature: false
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }
    
    const data = await response.json();
    return data.contract_id;
    
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

#### 3. Send for Signature

```javascript
async function sendForSignature(contractId, signerEmail, signerName) {
  try {
    const response = await fetch('/api/v1/send-to-signnow/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        contract_id: contractId,
        signer_email: signerEmail,
        signer_name: signerName
      })
    });
    
    if (!response.ok) throw new Error('Failed to send for signature');
    
    const data = await response.json();
    return data.signing_link;
    
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

#### 4. Download Contract

```javascript
async function downloadContract(contractId) {
  try {
    const response = await fetch(
      `/api/v1/download/?contract_id=${contractId}`,
      {
        headers: {
          'Authorization': `Bearer ${TOKEN}`
        }
      }
    );
    
    if (!response.ok) throw new Error('Failed to download');
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `contract_${contractId}.pdf`;
    link.click();
    
  } catch (error) {
    console.error('Error:', error);
  }
}
```

---

## State Management

### Recommended State Structure

```javascript
const contractState = {
  // Template/Form
  selectedTemplate: 'nda',
  templates: {},
  templateFields: {},
  formData: {},
  
  // Contract
  currentContractId: null,
  contractDetails: {},
  
  // Signature
  signerEmail: '',
  signerName: '',
  signingLink: '',
  
  // UI
  loading: false,
  error: null,
  success: false
};
```

### State Transitions

```
INITIAL
  ↓
SELECT_TEMPLATE → LOAD_FIELDS
  ↓
FILL_FORM → CREATE_CONTRACT
  ↓
CONTRACT_CREATED (can download or send for signature)
  ↓
[Option A] DOWNLOAD → Done
  ↓
[Option B] SEND_FOR_SIGNATURE → WAITING_FOR_SIGNATURE
  ↓
SIGNATURE_RECEIVED → SIGNED
  ↓
DOWNLOAD_SIGNED → Done
```

---

## Implementation Checklist

- [ ] Implement JWT authentication
- [ ] Create template selection UI
- [ ] Build dynamic form based on fields
- [ ] Add preview functionality
- [ ] Implement contract creation
- [ ] Add download capability
- [ ] Implement signature flow
- [ ] Set up webhook receiver (if needed)
- [ ] Add error handling
- [ ] Implement polling for signature status (optional)
- [ ] Add loading states
- [ ] Test all endpoints
- [ ] Deploy to production

---

## Testing

Run comprehensive endpoint tests:

```bash
python endpoints_test.py
```

This will test:
- ✅ Template listing
- ✅ Field retrieval
- ✅ Contract creation
- ✅ PDF download
- ✅ Signature flow
- ✅ Error handling

---

## Support

For issues or questions:
1. Check the logs: `/var/log/clm_backend.log`
2. Run tests: `python endpoints_test.py`
3. Review API responses for error messages
4. Check network tab in browser dev tools

