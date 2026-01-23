# Contract Template Management System - Complete Documentation

## Overview
This document provides comprehensive information about the contract template management system, including all 7 template types, required fields, endpoints, and working examples.

---

## 1. Template Management Endpoints

### 1.1 GET /api/v1/templates/types/
**Description:** Get all available contract template types with complete documentation

**Authentication:** Required (Token-based)

**Response Example:**
```json
{
  "success": true,
  "total_types": 7,
  "template_types": {
    "NDA": {
      "display_name": "Non-Disclosure Agreement",
      "description": "Protects confidential information between parties...",
      "contract_type": "NDA",
      "required_fields": [
        "effective_date",
        "first_party_name",
        "first_party_address",
        "second_party_name",
        "second_party_address",
        "agreement_type",
        "governing_law"
      ],
      "optional_fields": [
        "term_length",
        "confidentiality_period",
        "exclusions",
        "remedies",
        "notice_period"
      ],
      "mandatory_clauses": [
        "CONF-001",
        "CONF-002",
        "CONF-003"
      ],
      "business_rules": {
        "min_parties": 2,
        "allows_amendments": true,
        "term_in_years": 2
      },
      "sample_data": {
        "effective_date": "2026-01-20",
        "first_party_name": "Acme Corporation",
        "first_party_address": "123 Business Ave, San Francisco, CA 94102",
        "second_party_name": "Tech Innovations Inc",
        "second_party_address": "456 Innovation Blvd, Palo Alto, CA 94301",
        "agreement_type": "Mutual",
        "governing_law": "California"
      }
    },
    "MSA": { ... },
    "EMPLOYMENT": { ... },
    "SERVICE_AGREEMENT": { ... },
    "AGENCY_AGREEMENT": { ... },
    "PROPERTY_MANAGEMENT": { ... },
    "PURCHASE_AGREEMENT": { ... }
  }
}
```

---

### 1.2 GET /api/v1/templates/summary/
**Description:** Quick summary of all template types with field counts

**Authentication:** Required (Token-based)

**Response Example:**
```json
{
  "success": true,
  "total_types": 7,
  "summary": {
    "NDA": {
      "display_name": "Non-Disclosure Agreement",
      "description": "Protects confidential information between parties...",
      "required_fields_count": 7,
      "optional_fields_count": 5,
      "mandatory_clauses": ["CONF-001", "CONF-002", "CONF-003"]
    },
    "MSA": { ... },
    ...
  }
}
```

---

### 1.3 GET /api/v1/templates/types/{template_type}/
**Description:** Get detailed information about a specific template type

**Authentication:** Required (Token-based)

**Path Parameters:**
- `template_type`: One of `NDA`, `MSA`, `EMPLOYMENT`, `SERVICE_AGREEMENT`, `AGENCY_AGREEMENT`, `PROPERTY_MANAGEMENT`, `PURCHASE_AGREEMENT`

**Response Example (for NDA):**
```json
{
  "success": true,
  "template_type": "NDA",
  "display_name": "Non-Disclosure Agreement",
  "description": "Protects confidential information between parties...",
  "contract_type": "NDA",
  "required_fields": [
    {
      "name": "effective_date",
      "description": "Date when the agreement becomes effective"
    },
    {
      "name": "first_party_name",
      "description": "Name of the first party"
    },
    {
      "name": "first_party_address",
      "description": "Address of the first party"
    },
    {
      "name": "second_party_name",
      "description": "Name of the second party"
    },
    {
      "name": "second_party_address",
      "description": "Address of the second party"
    },
    {
      "name": "agreement_type",
      "description": "Type of agreement (Mutual, Unilateral)"
    },
    {
      "name": "governing_law",
      "description": "Jurisdiction for dispute resolution"
    }
  ],
  "optional_fields": [
    {
      "name": "term_length",
      "description": "term_length (optional)"
    },
    {
      "name": "confidentiality_period",
      "description": "confidentiality_period (optional)"
    },
    {
      "name": "exclusions",
      "description": "exclusions (optional)"
    },
    {
      "name": "remedies",
      "description": "remedies (optional)"
    },
    {
      "name": "notice_period",
      "description": "notice_period (optional)"
    }
  ],
  "mandatory_clauses": [
    "CONF-001",
    "CONF-002",
    "CONF-003"
  ],
  "business_rules": {
    "min_parties": 2,
    "allows_amendments": true,
    "term_in_years": 2
  },
  "sample_data": {
    "effective_date": "2026-01-20",
    "first_party_name": "Acme Corporation",
    "first_party_address": "123 Business Ave, San Francisco, CA 94102",
    "second_party_name": "Tech Innovations Inc",
    "second_party_address": "456 Innovation Blvd, Palo Alto, CA 94301",
    "agreement_type": "Mutual",
    "governing_law": "California"
  }
}
```

---

### 1.4 POST /api/v1/templates/validate/
**Description:** Validate data against template type requirements before creation

**Authentication:** Required (Token-based)

**Request Body:**
```json
{
  "template_type": "NDA",
  "data": {
    "effective_date": "2026-01-20",
    "first_party_name": "Acme Corporation",
    "first_party_address": "123 Business Ave, San Francisco, CA 94102",
    "second_party_name": "Tech Innovations Inc",
    "second_party_address": "456 Innovation Blvd, Palo Alto, CA 94301",
    "agreement_type": "Mutual",
    "governing_law": "California"
  }
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "is_valid": true,
  "template_type": "NDA",
  "required_fields": [
    "effective_date",
    "first_party_name",
    "first_party_address",
    "second_party_name",
    "second_party_address",
    "agreement_type",
    "governing_law"
  ],
  "optional_fields": [
    "term_length",
    "confidentiality_period",
    "exclusions",
    "remedies",
    "notice_period"
  ],
  "provided_fields": [
    "effective_date",
    "first_party_name",
    "first_party_address",
    "second_party_name",
    "second_party_address",
    "agreement_type",
    "governing_law"
  ],
  "missing_fields": [],
  "message": "All required fields provided",
  "validation_details": {
    "total_required": 7,
    "total_provided": 7,
    "fields_missing": 0,
    "fields_extra": 0
  }
}
```

**Failure Response (400 Bad Request - Missing Fields):**
```json
{
  "success": true,
  "is_valid": false,
  "template_type": "NDA",
  "required_fields": [
    "effective_date",
    "first_party_name",
    "first_party_address",
    "second_party_name",
    "second_party_address",
    "agreement_type",
    "governing_law"
  ],
  "optional_fields": [ ... ],
  "provided_fields": [
    "effective_date",
    "first_party_name"
  ],
  "missing_fields": [
    "first_party_address",
    "second_party_name",
    "second_party_address",
    "agreement_type",
    "governing_law"
  ],
  "message": "Missing required fields: first_party_address, second_party_name, second_party_address, agreement_type, governing_law",
  "validation_details": {
    "total_required": 7,
    "total_provided": 2,
    "fields_missing": 5,
    "fields_extra": 0
  }
}
```

---

### 1.5 POST /api/v1/templates/create-from-type/
**Description:** Create a new contract template from a predefined type

**Authentication:** Required (Token-based)

**Request Body:**
```json
{
  "template_type": "NDA",
  "name": "Standard NDA - 2026",
  "description": "Our standard mutual NDA for business partnerships",
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
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "template_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Standard NDA - 2026",
  "contract_type": "NDA",
  "status": "published",
  "merge_fields": [
    "effective_date",
    "first_party_name",
    "first_party_address",
    "second_party_name",
    "second_party_address",
    "agreement_type",
    "governing_law",
    "term_length",
    "confidentiality_period",
    "exclusions",
    "remedies",
    "notice_period"
  ],
  "mandatory_clauses": [
    "CONF-001",
    "CONF-002",
    "CONF-003"
  ],
  "message": "Template \"Standard NDA - 2026\" created successfully from NDA type",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Standard NDA - 2026",
    "contract_type": "NDA",
    "description": "Our standard mutual NDA for business partnerships",
    "version": 1,
    "status": "published",
    "r2_key": "templates/NDA/a1b2c3d4-e5f6-7890-abcd-ef1234567890.docx",
    "merge_fields": [ ... ],
    "mandatory_clauses": [ ... ],
    "business_rules": { ... },
    "created_by": "user_id",
    "tenant_id": "tenant_id",
    "created_at": "2026-01-21T13:04:11Z",
    "updated_at": "2026-01-21T13:04:11Z"
  }
}
```

**Error Response (400 Bad Request - Missing Fields):**
```json
{
  "success": false,
  "error": "Missing required fields: first_party_address, second_party_name",
  "required_fields": [
    "effective_date",
    "first_party_name",
    "first_party_address",
    "second_party_name",
    "second_party_address",
    "agreement_type",
    "governing_law"
  ]
}
```

---

## 2. Template Types Reference

### 2.1 NDA (Non-Disclosure Agreement)
**Purpose:** Protects confidential information between parties

**Required Fields (7):**
- `effective_date` - Date when the agreement becomes effective
- `first_party_name` - Name of the first party
- `first_party_address` - Address of the first party
- `second_party_name` - Name of the second party
- `second_party_address` - Address of the second party
- `agreement_type` - Type: "Mutual" or "Unilateral"
- `governing_law` - Jurisdiction (e.g., "California")

**Optional Fields (5):**
- `term_length` - Agreement duration in months
- `confidentiality_period` - Period information remains confidential
- `exclusions` - Information excluded from confidentiality
- `remedies` - Remedies for breach
- `notice_period` - Notice period for termination

**Sample Request:**
```bash
curl -X POST http://localhost:11000/api/v1/templates/create-from-type/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "NDA",
    "name": "Standard NDA",
    "status": "published",
    "data": {
      "effective_date": "2026-01-20",
      "first_party_name": "Acme Corp",
      "first_party_address": "123 Main St, San Francisco, CA 94102",
      "second_party_name": "Tech Inc",
      "second_party_address": "456 Market St, Palo Alto, CA 94301",
      "agreement_type": "Mutual",
      "governing_law": "California"
    }
  }'
```

---

### 2.2 MSA (Master Service Agreement)
**Purpose:** Establishes terms for ongoing service delivery

**Required Fields (9):**
- `effective_date` - Start date of agreement
- `client_name` - Name of the client
- `client_address` - Address of the client
- `service_provider_name` - Name of the service provider
- `service_provider_address` - Address of the service provider
- `service_description` - Detailed description of services
- `monthly_fees` - Monthly cost (numeric)
- `payment_terms` - Payment terms (e.g., "Net 30")
- `sla_uptime` - Service level agreement uptime guarantee

**Optional Fields (6):**
- `contract_term` - Contract duration
- `renewal_terms` - Auto-renewal conditions
- `termination_notice` - Days notice required for termination
- `support_hours` - Support availability
- `escalation_path` - Issue escalation procedures
- `change_management` - Change request procedures

**Sample Request:**
```bash
curl -X POST http://localhost:11000/api/v1/templates/create-from-type/ \
  -H "Authorization: Token YOUR_TOKEN" \
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

---

### 2.3 EMPLOYMENT (Employment Agreement)
**Purpose:** Defines employment terms and conditions

**Required Fields (9):**
- `effective_date` - Employment start date
- `employer_name` - Name of the employer
- `employer_address` - Address of the employer
- `employee_name` - Name of the employee
- `employee_address` - Address of the employee
- `job_title` - Job position and title
- `employment_type` - Type: "Full-Time", "Part-Time", "Contract"
- `annual_salary` - Annual compensation (numeric)
- `start_date` - First day of employment

**Optional Fields (7):**
- `benefits_description` - Health insurance, retirement, etc.
- `vacation_days` - Annual vacation allowance
- `sick_leave` - Annual sick leave allowance
- `bonus_structure` - Bonus or incentive plan
- `confidentiality_clause` - Non-disclosure obligations
- `non_compete` - Non-compete period and scope
- `probation_period` - Probation period in months

**Sample Request:**
```bash
curl -X POST http://localhost:11000/api/v1/templates/create-from-type/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "EMPLOYMENT",
    "name": "Senior Engineer Employment",
    "status": "published",
    "data": {
      "effective_date": "2026-02-01",
      "employer_name": "Global Tech Corp",
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

---

### 2.4 SERVICE_AGREEMENT (Professional Services Agreement)
**Purpose:** Defines scope and terms for project-based services

**Required Fields (8):**
- `effective_date` - Agreement start date
- `service_provider_name` - Provider company name
- `service_provider_address` - Provider address
- `client_name` - Client company name
- `client_address` - Client address
- `scope_of_services` - Detailed service description
- `total_project_value` - Total project cost (numeric)
- `payment_schedule` - Payment milestones

**Optional Fields (6):**
- `project_timeline` - Project duration
- `deliverables` - Specific deliverables list
- `acceptance_criteria` - Acceptance conditions
- `change_order_process` - Scope change procedures
- `warranty_period` - Post-delivery warranty
- `support_period` - Post-delivery support

**Sample Request:**
```bash
curl -X POST http://localhost:11000/api/v1/templates/create-from-type/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "SERVICE_AGREEMENT",
    "name": "Consulting Services Agreement",
    "status": "published",
    "data": {
      "effective_date": "2026-01-15",
      "service_provider_name": "Consulting Partners LLC",
      "service_provider_address": "222 Consulting Drive, Boston, MA 02101",
      "client_name": "Manufacturing Co",
      "client_address": "333 Factory Road, Boston, MA 02102",
      "scope_of_services": "Business process optimization and supply chain analysis",
      "total_project_value": 50000,
      "payment_schedule": "25% upon signing, 25% at midpoint, 50% at completion"
    }
  }'
```

---

### 2.5 AGENCY_AGREEMENT
**Purpose:** Establishes agency relationship and authority

**Required Fields (7):**
- `effective_date` - Agreement start date
- `principal_name` - Principal company name
- `principal_address` - Principal address
- `agent_name` - Agent company/individual name
- `agent_address` - Agent address
- `scope_of_agency` - Agent's authority and responsibilities
- `compensation_structure` - Compensation terms (percentage or fixed)

**Optional Fields (5):**
- `term_period` - Agency duration
- `territory` - Geographic scope of authority
- `exclusive` - Exclusive or non-exclusive designation
- `termination_clause` - Termination conditions
- `indemnification` - Indemnification terms

---

### 2.6 PROPERTY_MANAGEMENT (Property Management Agreement)
**Purpose:** Governs property management services

**Required Fields (8):**
- `effective_date` - Agreement start date
- `owner_name` - Property owner name
- `owner_address` - Owner address
- `manager_name` - Property manager name
- `manager_address` - Manager address
- `property_address` - Managed property address
- `management_fees_percentage` - Monthly management fee as percentage
- `services_included` - List of management services

**Optional Fields (6):**
- `lease_collection` - Tenant lease collection services
- `maintenance_threshold` - Maintenance approval limits
- `insurance_responsibility` - Insurance obligations
- `rent_increase_policy` - Annual rent increase policy
- `emergency_contact` - Emergency procedure contacts
- `reporting_frequency` - Management reporting schedule

---

### 2.7 PURCHASE_AGREEMENT (Purchase Agreement)
**Purpose:** Governs the purchase of goods or assets

**Required Fields (9):**
- `effective_date` - Agreement date
- `buyer_name` - Buyer company/individual name
- `buyer_address` - Buyer address
- `seller_name` - Seller company/individual name
- `seller_address` - Seller address
- `item_description` - Detailed item description
- `purchase_price` - Total purchase price (numeric)
- `payment_terms` - Payment arrangements
- `delivery_date` - Expected delivery date

**Optional Fields (7):**
- `warranty` - Warranty period and terms
- `inspection_period` - Buyer inspection timeframe
- `return_policy` - Return or rejection policy
- `insurance_responsibility` - Insurance during shipment
- `title_transfer` - When title transfers to buyer
- `dispute_resolution` - Dispute handling procedure
- `force_majeure` - Force majeure clause

---

## 3. Complete Working Example: Creating Multiple Templates

### Step 1: Authenticate
```bash
# Get your authentication token
TOKEN="your_auth_token_here"
BASE_URL="http://localhost:11000/api/v1"
```

### Step 2: List All Available Template Types
```bash
curl -X GET "$BASE_URL/templates/types/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
```

### Step 3: Get Summary of All Template Types
```bash
curl -X GET "$BASE_URL/templates/summary/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
```

### Step 4: Get Detailed Information for Specific Type
```bash
curl -X GET "$BASE_URL/templates/types/NDA/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
```

### Step 5: Validate Data Before Creating Template
```bash
curl -X POST "$BASE_URL/templates/validate/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "NDA",
    "data": {
      "effective_date": "2026-01-20",
      "first_party_name": "Company A",
      "first_party_address": "123 Main St, City, State 12345",
      "second_party_name": "Company B",
      "second_party_address": "456 Oak Ave, City, State 67890",
      "agreement_type": "Mutual",
      "governing_law": "California"
    }
  }' | jq '.'
```

### Step 6: Create Template from Type
```bash
curl -X POST "$BASE_URL/templates/create-from-type/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "NDA",
    "name": "Standard NDA 2026",
    "description": "Our standard mutual NDA",
    "status": "published",
    "data": {
      "effective_date": "2026-01-20",
      "first_party_name": "Company A",
      "first_party_address": "123 Main St, City, State 12345",
      "second_party_name": "Company B",
      "second_party_address": "456 Oak Ave, City, State 67890",
      "agreement_type": "Mutual",
      "governing_law": "California"
    }
  }' | jq '.'
```

---

## 4. Summary

**Total Available Template Types: 7**

| Type | Required Fields | Optional Fields | Use Case |
|------|-----------------|-----------------|----------|
| **NDA** | 7 | 5 | Protecting confidential information |
| **MSA** | 9 | 6 | Ongoing service relationships |
| **EMPLOYMENT** | 9 | 7 | Employee hiring and terms |
| **SERVICE_AGREEMENT** | 8 | 6 | Project-based consulting services |
| **AGENCY_AGREEMENT** | 7 | 5 | Agent/representative relationships |
| **PROPERTY_MANAGEMENT** | 8 | 6 | Property management services |
| **PURCHASE_AGREEMENT** | 9 | 7 | Goods/asset purchases |

All templates support:
- ✅ Template validation before creation
- ✅ Customizable names and descriptions
- ✅ Draft and published states
- ✅ Automatic merge field population
- ✅ Mandatory clause enforcement
- ✅ Business rule enforcement
- ✅ Tenant isolation and security
