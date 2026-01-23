# CLM Backend - Contract Generation API

Production-ready contract generation and management system with SignNow e-signature integration.

## Features

- **Multi-tenant contract generation** - Support for 4 contract types
- **PDF generation** - Auto-filled contracts using ReportLab
- **Clause management** - Dynamic clause storage and retrieval
- **E-signature integration** - SignNow API for document signing
- **Authentication** - JWT token-based API security
- **Database persistence** - PostgreSQL with tenant isolation

## Supported Contract Types

| Type | Description | Key Fields |
|------|-------------|-----------|
| NDA | Non-Disclosure Agreement | Mutual, party names, agreement type |
| Agency Agreement | Principal-Agent relationship | Commission, term, duties |
| Property Management | Property rental/lease management | Property address, tenant terms |
| Employment Contract | Employment terms | Salary, benefits, position |

## API Endpoints

### Core Endpoints

#### 1. Create Contract
```
POST /api/v1/create/
Authorization: Bearer <JWT_TOKEN>

Request:
{
  "contract_type": "nda|agency_agreement|property_management|employment_contract",
  "data": {
    "date": "2026-01-20",
    "1st_party_name": "Company A",
    "2nd_party_name": "Company B",
    "clauses": [
      {"name": "Confidentiality", "description": "..."},
      {"name": "Non-Compete", "description": "..."}
    ]
  }
}

Response (201):
{
  "success": true,
  "contract_id": "uuid",
  "file_path": "/path/to/contract.pdf",
  "file_size": 109766,
  "created_at": "2026-01-20T15:30:45Z"
}
```

#### 2. Get Contract Details
```
GET /api/v1/details/?contract_id=<contract_id>
Authorization: Bearer <JWT_TOKEN>

Response (200):
{
  "success": true,
  "contract": {
    "id": "uuid",
    "title": "NDA - 2026-01-20",
    "contract_type": "nda",
    "status": "draft",
    "clauses": [{"name": "Confidentiality", ...}],
    "signed": {"status": "signed", "signers": [...], "signed_at": "..."},
    "file_size": 109766,
    "created_at": "2026-01-20T15:30:45Z"
  }
}
```

#### 3. Download Contract PDF
```
GET /api/v1/download/?contract_id=<contract_id>
Authorization: Bearer <JWT_TOKEN>

Response: Binary PDF file (Content-Type: application/pdf)
```

#### 4. Send to SignNow for Signature
```
POST /api/v1/send-to-signnow/
Authorization: Bearer <JWT_TOKEN>

Request:
{
  "contract_id": "uuid",
  "signer_email": "user@example.com",
  "signer_name": "Jane Doe"
}

Response (200):
{
  "contract_id": "uuid",
  "signing_link": "https://app.signnow.com/sign/...",
  "message": "Send link to Jane Doe. They will type/draw signature and sign."
}
```

#### 5. SignNow Webhook (After Signing)
```
POST /api/v1/webhook/signnow/
(Internal service call - no authentication)

Request (from SignNow):
{
  "event": "document.signed",
  "document": {
    "contract_id": "uuid",
    "signed_at": "2026-01-20T15:30:45Z",
    "signed_pdf_url": "https://...",
    "signers": [
      {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "signed_at": "2026-01-20T15:30:45Z"
      }
    ]
  }
}

Response (200):
{
  "status": "received",
  "message": "Signature received from Jane Doe. Contract is now signed.",
  "pdf_size_bytes": 109766
}
```

### Template Information Endpoints

#### 6. Get Available Templates
```
GET /api/v1/templates/
Authorization: Bearer <JWT_TOKEN>

Response (200):
{
  "success": true,
  "templates": {
    "nda": {"required_fields_count": 5, "optional_fields_count": 3},
    "agency_agreement": {...},
    "property_management": {...},
    "employment_contract": {...}
  },
  "total_supported": 4
}
```

#### 7. Get Contract Fields for Type
```
GET /api/v1/fields/?contract_type=nda
Authorization: Bearer <JWT_TOKEN>

Response (200):
{
  "contract_type": "nda",
  "required_fields": ["date", "1st_party_name", "2nd_party_name", ...],
  "optional_fields": ["agreement_type", "governing_law", ...],
  "signature_fields": ["1st_party_printed_name", "2nd_party_printed_name"]
}
```

#### 8. Get Full Contract Template Content
```
GET /api/v1/content/?contract_type=nda
Authorization: Bearer <JWT_TOKEN>

Response (200):
{
  "contract_type": "nda",
  "title": "Non-Disclosure Agreement",
  "required_fields": [...],
  "full_content": "This Non-Disclosure Agreement ('NDA') is entered into..."
}
```

## Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Django 5.0+

### Quick Start

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Apply migrations**
```bash
python manage.py migrate
```

3. **Create superuser**
```bash
python manage.py createsuperuser
```

4. **Start server**
```bash
python manage.py runserver 0.0.0.0:11000
```

5. **Run tests**
```bash
python tests.py
```

## Testing

Run the complete end-to-end test suite:

```bash
python tests.py
```

Expected output:
```
================================================================================
CONTRACT GENERATION & SIGNNOW INTEGRATION TEST SUITE
================================================================================

Test                              Status      Code      
-----------–---------------------------------------------------
✅ Create Contract               PASS        201       
✅ Get Details (Before)          PASS        200       
✅ Send to SignNow               PASS        200       
✅ Webhook Received              PASS        200       
✅ Get Details (After)           PASS        200       
✅ Download PDF                  PASS        200       
-----------–---------------------------------------------------
Total: 6 | Passed: 6 | Failed: 0 | Skipped: 0

✅ ALL TESTS PASSED
```

## Database Models

### Contract
- `id` (UUID) - Primary key
- `tenant_id` (UUID) - Tenant isolation for RLS
- `title` (CharField) - Contract title
- `contract_type` (CharField) - Type: nda, agency_agreement, property_management, employment_contract
- `status` (CharField) - draft, pending, approved, executed
- `clauses` (JSONField) - Array of clause objects with name and description
- `signed` (JSONField) - Signature data with status, signers, signed_at
- `signed_pdf` (BinaryField) - Binary content of signed PDF
- `signnow_document_id` (CharField) - Reference to SignNow document
- `created_at`, `updated_at` (DateTimeField) - Timestamps
- `created_by` (UUID) - Creator user ID

### ContractTemplate
- Reusable template definitions with versioning

### Clause
- Reusable contract clauses with versioning and alternatives

### ESignatureContract
- E-signature workflow tracking

### Signer
- Signer information and status

## Configuration

### Django Settings
- `DEBUG = False` (Production)
- `ALLOWED_HOSTS` = ['yourdomain.com']
- `REST_FRAMEWORK` - JWT authentication configured
- `LOGGING` - JSON logging to file

### Environment Variables
```bash
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost/dbname
JWT_SECRET=your-jwt-secret
SIGNNOW_API_KEY=your-signnow-api-key
```

## Security Features

- ✅ JWT Authentication on all endpoints (except webhook)
- ✅ Tenant isolation at database level
- ✅ SQL injection prevention (ORM parameterized queries)
- ✅ CORS protection
- ✅ Input validation and sanitization
- ✅ Rate limiting ready
- ✅ HTTPS enforcement in production

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error message",
  "message": "Detailed description"
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid token)
- `403` - Forbidden (access denied)
- `404` - Not Found
- `500` - Internal Server Error

## Performance

- PDF generation: ~500ms per contract
- Database queries: Indexed by tenant_id
- File downloads: Direct from filesystem or R2
- Webhook processing: Asynchronous ready

## Production Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:11000"]
```

### Deployment Checklist
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set strong SECRET_KEY
- [ ] Configure PostgreSQL credentials
- [ ] Set up SSL/HTTPS
- [ ] Configure logging service
- [ ] Set up database backups
- [ ] Configure monitoring/alerts
- [ ] Test all endpoints
- [ ] Run security audit

## Monitoring & Logs

- **Log Location**: `/var/log/clm_backend.log`
- **Log Format**: JSON with timestamps
- **Log Level**: INFO (production), DEBUG (development)
- **Metrics**: Response times, error rates, PDF generation timing

## Database Backup

```bash
# Backup
pg_dump postgresql://user:pass@localhost/dbname > backup.sql

# Restore
psql postgresql://user:pass@localhost/dbname < backup.sql
```

## Version

**Current**: 1.0.0  
**Status**: Production Ready ✅  
**Last Updated**: January 2026

## Support

For issues or questions, check the logs and run the test suite to diagnose problems.
