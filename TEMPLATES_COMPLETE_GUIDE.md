# CONTRACT TEMPLATE STRUCTURE & ENDPOINTS - COMPLETE SUMMARY

## 📋 Quick Overview

The Contract Template Management System provides a comprehensive framework for creating and managing 7 different types of contract templates. Each template type has predefined required fields, optional fields, mandatory clauses, and business rules.

---

## 🎯 7 Contract Template Types

### 1. **NDA** - Non-Disclosure Agreement
- **Purpose**: Protect confidential information between parties
- **Required Fields**: 7 fields
  - effective_date, first_party_name, first_party_address
  - second_party_name, second_party_address, agreement_type, governing_law
- **Optional Fields**: 5 fields
  - term_length, confidentiality_period, exclusions, remedies, notice_period
- **Mandatory Clauses**: CONF-001, CONF-002, CONF-003

### 2. **MSA** - Master Service Agreement
- **Purpose**: Establish terms for ongoing service delivery
- **Required Fields**: 9 fields
  - effective_date, client_name, client_address
  - service_provider_name, service_provider_address
  - service_description, monthly_fees, payment_terms, sla_uptime
- **Optional Fields**: 6 fields
  - contract_term, renewal_terms, termination_notice, support_hours, escalation_path, change_management
- **Mandatory Clauses**: SERVICE-001, SERVICE-002

### 3. **EMPLOYMENT** - Employment Agreement
- **Purpose**: Define employment terms and conditions
- **Required Fields**: 9 fields
  - effective_date, employer_name, employer_address
  - employee_name, employee_address, job_title, employment_type
  - annual_salary, start_date
- **Optional Fields**: 7 fields
  - benefits_description, vacation_days, sick_leave, bonus_structure, confidentiality_clause, non_compete, probation_period
- **Mandatory Clauses**: EMP-001, EMP-002

### 4. **SERVICE_AGREEMENT** - Professional Services Agreement
- **Purpose**: Define scope and terms for project-based services
- **Required Fields**: 8 fields
  - effective_date, service_provider_name, service_provider_address
  - client_name, client_address, scope_of_services, total_project_value, payment_schedule
- **Optional Fields**: 6 fields
  - project_timeline, deliverables, acceptance_criteria, change_order_process, warranty_period, support_period
- **Mandatory Clauses**: SERVICE-001, SERVICE-002

### 5. **AGENCY_AGREEMENT** - Agent/Representative Agreement
- **Purpose**: Establish agency relationship and authority
- **Required Fields**: 7 fields
  - effective_date, principal_name, principal_address
  - agent_name, agent_address, scope_of_agency, compensation_structure
- **Optional Fields**: 5 fields
  - term_period, territory, exclusive, termination_clause, indemnification
- **Mandatory Clauses**: AGENCY-001

### 6. **PROPERTY_MANAGEMENT** - Property Management Agreement
- **Purpose**: Govern property management services
- **Required Fields**: 8 fields
  - effective_date, owner_name, owner_address
  - manager_name, manager_address, property_address
  - management_fees_percentage, services_included
- **Optional Fields**: 6 fields
  - lease_collection, maintenance_threshold, insurance_responsibility, rent_increase_policy, emergency_contact, reporting_frequency
- **Mandatory Clauses**: PROPERTY-001

### 7. **PURCHASE_AGREEMENT** - Purchase Agreement
- **Purpose**: Govern the purchase of goods or assets
- **Required Fields**: 9 fields
  - effective_date, buyer_name, buyer_address
  - seller_name, seller_address, item_description
  - purchase_price, payment_terms, delivery_date
- **Optional Fields**: 7 fields
  - warranty, inspection_period, return_policy, insurance_responsibility, title_transfer, dispute_resolution, force_majeure
- **Mandatory Clauses**: PURCHASE-001, PURCHASE-002

---

## 🔌 API Endpoints

### Endpoint 1: GET /api/v1/templates/types/
**Get all template types with complete documentation**

```
Method: GET
Path: /api/v1/templates/types/
Authentication: Required (Token)
```

**Response**: Returns all 7 template types with full metadata (display_name, description, required_fields, optional_fields, mandatory_clauses, business_rules, sample_data)

---

### Endpoint 2: GET /api/v1/templates/summary/
**Quick summary of all template types**

```
Method: GET
Path: /api/v1/templates/summary/
Authentication: Required (Token)
```

**Response**: Returns template types with field counts and clause information

---

### Endpoint 3: GET /api/v1/templates/types/{template_type}/
**Get detailed information about a specific template type**

```
Method: GET
Path: /api/v1/templates/types/{template_type}/
Parameters: template_type = NDA | MSA | EMPLOYMENT | SERVICE_AGREEMENT | AGENCY_AGREEMENT | PROPERTY_MANAGEMENT | PURCHASE_AGREEMENT
Authentication: Required (Token)
```

**Response**: Complete template definition including all fields with descriptions and sample data

---

### Endpoint 4: POST /api/v1/templates/validate/
**Validate data against template requirements**

```
Method: POST
Path: /api/v1/templates/validate/
Authentication: Required (Token)
Content-Type: application/json
```

**Request Body**:
```json
{
  "template_type": "NDA",
  "data": {
    "effective_date": "2026-01-20",
    "first_party_name": "Company A",
    "first_party_address": "123 Main St, City, State",
    "second_party_name": "Company B",
    "second_party_address": "456 Oak Ave, City, State",
    "agreement_type": "Mutual",
    "governing_law": "California"
  }
}
```

**Response**: Validation result with missing fields, provided fields, and error messages

---

### Endpoint 5: POST /api/v1/templates/create-from-type/
**Create a new contract template from a predefined type**

```
Method: POST
Path: /api/v1/templates/create-from-type/
Authentication: Required (Token)
Content-Type: application/json
```

**Request Body**:
```json
{
  "template_type": "NDA",
  "name": "Standard NDA 2026",
  "description": "Our standard mutual NDA",
  "status": "published",
  "data": {
    "effective_date": "2026-01-20",
    "first_party_name": "Acme Corporation",
    "first_party_address": "123 Business Ave, San Francisco, CA",
    "second_party_name": "Tech Innovations Inc",
    "second_party_address": "456 Innovation Blvd, Palo Alto, CA",
    "agreement_type": "Mutual",
    "governing_law": "California"
  }
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "template_id": "uuid-here",
  "name": "Standard NDA 2026",
  "contract_type": "NDA",
  "status": "published",
  "merge_fields": [...],
  "mandatory_clauses": [...],
  "message": "Template created successfully from NDA type",
  "data": {...}
}
```

---

## 📊 Data Model

### ContractTemplate Model Fields
- `id` (UUID) - Unique template identifier
- `tenant_id` (UUID) - Tenant isolation for multi-tenancy
- `name` (String) - Template name
- `contract_type` (String) - Type: NDA, MSA, EMPLOYMENT, etc.
- `description` (Text) - Template description
- `version` (Integer, default=1) - Version number
- `status` (String) - draft, published, archived
- `r2_key` (String) - Cloudflare R2 storage location
- `merge_fields` (JSON Array) - All placeholder fields
- `mandatory_clauses` (JSON Array) - Required clauses
- `business_rules` (JSON Dict) - Enforcement rules
- `created_by` (UUID) - User who created template
- `created_at` (DateTime) - Creation timestamp
- `updated_at` (DateTime) - Last update timestamp

---

## ✅ Working Examples

### Example 1: Creating an NDA Template

```bash
curl -X POST http://localhost:11000/api/v1/templates/create-from-type/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "NDA",
    "name": "Standard Mutual NDA",
    "status": "published",
    "data": {
      "effective_date": "2026-01-20",
      "first_party_name": "Acme Corporation",
      "first_party_address": "123 Business Ave, San Francisco, CA 94102",
      "second_party_name": "Tech Innovations Inc",
      "second_party_address": "456 Innovation Blvd, Palo Alto, CA 94301",
      "agreement_type": "Mutual",
      "governing_law": "California"
    }
  }'
```

**Expected Response (201 Created)**:
```json
{
  "success": true,
  "template_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Standard Mutual NDA",
  "contract_type": "NDA",
  "status": "published",
  "merge_fields": [
    "effective_date", "first_party_name", "first_party_address",
    "second_party_name", "second_party_address", "agreement_type",
    "governing_law", "term_length", "confidentiality_period",
    "exclusions", "remedies", "notice_period"
  ],
  "mandatory_clauses": ["CONF-001", "CONF-002", "CONF-003"],
  "message": "Template \"Standard Mutual NDA\" created successfully from NDA type"
}
```

---

### Example 2: Creating an MSA Template

```bash
curl -X POST http://localhost:11000/api/v1/templates/create-from-type/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "MSA",
    "name": "Cloud Services MSA",
    "status": "published",
    "data": {
      "effective_date": "2026-01-20",
      "client_name": "Enterprise Solutions Ltd",
      "client_address": "789 Corporate Way, New York, NY 10001",
      "service_provider_name": "CloudTech Services Inc",
      "service_provider_address": "321 Cloud Street, Seattle, WA 98101",
      "service_description": "Cloud-based SaaS platform with 24/7 support",
      "monthly_fees": 5000,
      "payment_terms": "Net 30 from invoice date",
      "sla_uptime": "99.9% monthly uptime guarantee"
    }
  }'
```

**Expected Response (201 Created)**:
```json
{
  "success": true,
  "template_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "name": "Cloud Services MSA",
  "contract_type": "MSA",
  "status": "published",
  "merge_fields": [...],
  "mandatory_clauses": ["SERVICE-001", "SERVICE-002"],
  "message": "Template \"Cloud Services MSA\" created successfully from MSA type"
}
```

---

### Example 3: Creating an Employment Template

```bash
curl -X POST http://localhost:11000/api/v1/templates/create-from-type/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "EMPLOYMENT",
    "name": "Senior Engineer Employment Agreement",
    "status": "published",
    "data": {
      "effective_date": "2026-02-01",
      "employer_name": "Global Tech Corporation",
      "employer_address": "100 Tech Plaza, Austin, TX 78701",
      "employee_name": "John Smith",
      "employee_address": "456 Residential Lane, Austin, TX 78704",
      "job_title": "Senior Software Engineer",
      "employment_type": "Full-Time",
      "annual_salary": 150000,
      "start_date": "2026-02-15"
    }
  }'
```

**Expected Response (201 Created)**:
```json
{
  "success": true,
  "template_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "name": "Senior Engineer Employment Agreement",
  "contract_type": "EMPLOYMENT",
  "status": "published",
  "merge_fields": [...],
  "mandatory_clauses": ["EMP-001", "EMP-002"],
  "message": "Template \"Senior Engineer Employment Agreement\" created successfully from EMPLOYMENT type"
}
```

---

### Example 4: Validating Template Data

```bash
curl -X POST http://localhost:11000/api/v1/templates/validate/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "SERVICE_AGREEMENT",
    "data": {
      "effective_date": "2026-01-15",
      "service_provider_name": "Consulting Partners LLC",
      "service_provider_address": "222 Consulting Drive, Boston, MA 02101",
      "client_name": "Manufacturing Co",
      "client_address": "333 Factory Road, Boston, MA 02102",
      "scope_of_services": "Business optimization and analysis",
      "total_project_value": 50000,
      "payment_schedule": "3 equal installments"
    }
  }'
```

**Expected Response (200 OK)**:
```json
{
  "success": true,
  "is_valid": true,
  "template_type": "SERVICE_AGREEMENT",
  "required_fields": [
    "effective_date", "service_provider_name", "service_provider_address",
    "client_name", "client_address", "scope_of_services",
    "total_project_value", "payment_schedule"
  ],
  "optional_fields": [...],
  "provided_fields": [
    "effective_date", "service_provider_name", "service_provider_address",
    "client_name", "client_address", "scope_of_services",
    "total_project_value", "payment_schedule"
  ],
  "missing_fields": [],
  "message": "All required fields provided",
  "validation_details": {
    "total_required": 8,
    "total_provided": 8,
    "fields_missing": 0,
    "fields_extra": 0
  }
}
```

---

## 🔐 Security & Features

✅ **Multi-Tenant Isolation**: Each template is isolated by tenant_id  
✅ **Authentication Required**: All endpoints require valid API token  
✅ **Field Validation**: Automatic validation of required vs optional fields  
✅ **Clause Management**: Predefined mandatory clauses per template type  
✅ **Business Rules Enforcement**: Custom business rules per template  
✅ **Version Control**: Template versioning for tracking changes  
✅ **Draft & Publish**: Support for draft and published states  
✅ **Audit Trail**: Created_by and timestamp tracking  

---

## 📝 Integration Notes

1. **Authentication**: All endpoints require `Authorization: Token <your_token>`
2. **Content-Type**: All POST requests require `Content-Type: application/json`
3. **Responses**: All responses include a `success` boolean flag
4. **Errors**: Failed requests return appropriate HTTP status codes (400, 404, 500)
5. **Pagination**: List endpoints support limit/offset pagination
6. **Filtering**: Templates can be filtered by contract_type, status, created_by

---

## 📂 Files Created

- `/contracts/template_views.py` - All template management endpoint views
- `/contracts/template_definitions.py` - Template type definitions with metadata
- `/contracts/urls.py` - Updated with new endpoints
- `/TEMPLATE_MANAGEMENT_GUIDE.md` - Complete API documentation
- `/TEMPLATE_CURL_EXAMPLES.sh` - Curl command examples for all endpoints

---

## ✨ Key Capabilities

1. **List all template types** with complete metadata
2. **Get detailed template information** including all fields and business rules
3. **Validate template data** before creation
4. **Create new templates** from predefined types
5. **Enforce field requirements** automatically
6. **Support multiple contract types** (7 different template types)
7. **Tenant-aware** - Automatic tenant isolation
8. **Audit trail** - Track creation and modifications

This comprehensive system enables seamless contract template management with strong validation, security, and multi-tenancy support.
