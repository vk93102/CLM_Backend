# QUICK REFERENCE: Template Management System

## 🚀 Quick Start

### Step 1: Get Your Authentication Token
```bash
# Set these variables in your environment
TOKEN="your_authentication_token"
BASE_URL="http://localhost:11000/api/v1"
```

### Step 2: Explore Template Types
```bash
# See all 7 available template types
curl -X GET "$BASE_URL/templates/types/" \
  -H "Authorization: Token $TOKEN" | jq '.'

# Get summary with field counts
curl -X GET "$BASE_URL/templates/summary/" \
  -H "Authorization: Token $TOKEN" | jq '.'
```

### Step 3: Create a Template
```bash
curl -X POST "$BASE_URL/templates/create-from-type/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template_type":"NDA","name":"My NDA","data":{...}}'
```

---

## 📑 All 7 Template Types at a Glance

| # | Template Type | Required Fields | Use Case |
|---|---|---|---|
| 1️⃣ | **NDA** | 7 | Protect confidential info |
| 2️⃣ | **MSA** | 9 | Ongoing services |
| 3️⃣ | **EMPLOYMENT** | 9 | Employee contracts |
| 4️⃣ | **SERVICE_AGREEMENT** | 8 | Project services |
| 5️⃣ | **AGENCY_AGREEMENT** | 7 | Agent relationships |
| 6️⃣ | **PROPERTY_MANAGEMENT** | 8 | Property management |
| 7️⃣ | **PURCHASE_AGREEMENT** | 9 | Goods/asset purchase |

---

## 🔗 All 5 Endpoints

### 1. GET /templates/types/
```
Response: All 7 template types with full documentation
Uses: Explore available templates
```

### 2. GET /templates/summary/
```
Response: Quick summary with field counts
Uses: Quick overview of templates
```

### 3. GET /templates/types/{template_type}/
```
Path Parameter: NDA | MSA | EMPLOYMENT | SERVICE_AGREEMENT | AGENCY_AGREEMENT | PROPERTY_MANAGEMENT | PURCHASE_AGREEMENT
Response: Complete template definition
Uses: Understand specific template structure
```

### 4. POST /templates/validate/
```
Body: {"template_type": "...", "data": {...}}
Response: Validation result with missing fields
Uses: Pre-validation before creation
```

### 5. POST /templates/create-from-type/
```
Body: {"template_type": "...", "name": "...", "status": "...", "data": {...}}
Response: Created template with UUID
Uses: Create new template from type
```

---

## ✏️ NDA Template Example

### Required Fields (7)
```
✓ effective_date       - "2026-01-20"
✓ first_party_name     - "Company A"
✓ first_party_address  - "123 Main St, City, State"
✓ second_party_name    - "Company B"
✓ second_party_address - "456 Oak Ave, City, State"
✓ agreement_type       - "Mutual" or "Unilateral"
✓ governing_law        - "California"
```

### Optional Fields (5)
```
○ term_length                - Duration in months
○ confidentiality_period     - How long info stays confidential
○ exclusions                 - Excluded information types
○ remedies                   - Breach remedies
○ notice_period              - Termination notice period
```

### Sample Request
```bash
curl -X POST "$BASE_URL/templates/create-from-type/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "NDA",
    "name": "Standard NDA",
    "description": "Our standard mutual NDA",
    "status": "published",
    "data": {
      "effective_date": "2026-01-20",
      "first_party_name": "Acme Corp",
      "first_party_address": "123 Main St, San Francisco, CA",
      "second_party_name": "Tech Inc",
      "second_party_address": "456 Oak Ave, Palo Alto, CA",
      "agreement_type": "Mutual",
      "governing_law": "California"
    }
  }'
```

### Sample Response (201 Created)
```json
{
  "success": true,
  "template_id": "uuid-string",
  "name": "Standard NDA",
  "contract_type": "NDA",
  "status": "published",
  "merge_fields": ["effective_date", "first_party_name", ...],
  "mandatory_clauses": ["CONF-001", "CONF-002", "CONF-003"],
  "message": "Template created successfully"
}
```

---

## ✏️ MSA Template Example

### Required Fields (9)
```
✓ effective_date              - "2026-01-20"
✓ client_name                 - "Enterprise Ltd"
✓ client_address              - "789 Corp Way, New York, NY"
✓ service_provider_name       - "CloudTech Inc"
✓ service_provider_address    - "321 Cloud St, Seattle, WA"
✓ service_description         - "Cloud-based SaaS platform"
✓ monthly_fees                - 5000
✓ payment_terms               - "Net 30"
✓ sla_uptime                  - "99.9% monthly"
```

### Optional Fields (6)
```
○ contract_term              - Duration of contract
○ renewal_terms              - Auto-renewal conditions
○ termination_notice         - Notice required for termination
○ support_hours              - Support availability times
○ escalation_path            - Issue escalation procedures
○ change_management          - Change request process
```

---

## ✏️ EMPLOYMENT Template Example

### Required Fields (9)
```
✓ effective_date             - "2026-02-01"
✓ employer_name              - "Global Tech Corp"
✓ employer_address           - "100 Tech Plaza, Austin, TX"
✓ employee_name              - "John Smith"
✓ employee_address           - "456 Residential Lane, Austin, TX"
✓ job_title                  - "Senior Software Engineer"
✓ employment_type            - "Full-Time" | "Part-Time" | "Contract"
✓ annual_salary              - 150000
✓ start_date                 - "2026-02-15"
```

### Optional Fields (7)
```
○ benefits_description       - Health, retirement, etc.
○ vacation_days              - Annual vacation days
○ sick_leave                 - Annual sick leave days
○ bonus_structure            - Bonus/incentive plan
○ confidentiality_clause     - NDA obligations
○ non_compete                - Non-compete duration
○ probation_period           - Probation in months
```

---

## ✏️ SERVICE_AGREEMENT Template Example

### Required Fields (8)
```
✓ effective_date             - "2026-01-15"
✓ service_provider_name      - "Consulting Partners LLC"
✓ service_provider_address   - "222 Consulting Drive, Boston, MA"
✓ client_name                - "Manufacturing Co"
✓ client_address             - "333 Factory Road, Boston, MA"
✓ scope_of_services          - "Business optimization and analysis"
✓ total_project_value        - 50000
✓ payment_schedule           - "25/25/50 split"
```

### Optional Fields (6)
```
○ project_timeline           - Project duration
○ deliverables               - Specific deliverables
○ acceptance_criteria        - Acceptance conditions
○ change_order_process       - Scope change procedure
○ warranty_period            - Post-delivery warranty
○ support_period             - Post-delivery support
```

---

## HTTP Status Codes

| Code | Meaning | Example Scenario |
|------|---------|------------------|
| 200 | Success (GET) | Retrieved template info successfully |
| 201 | Created (POST) | Template created successfully |
| 400 | Bad Request | Missing required fields in request |
| 404 | Not Found | Unknown template type or missing template |
| 500 | Server Error | Database or processing error |

---

## 🛡️ Security & Validation

✅ **Required Authentication**: All endpoints need valid API token  
✅ **Multi-Tenant Isolation**: Data isolated by tenant_id  
✅ **Field Validation**: All required fields must be provided  
✅ **Mandatory Clauses**: Auto-included in created templates  
✅ **Status Control**: Draft and published states  
✅ **Audit Trail**: Created_by user tracking  

---

## 💡 Common Use Cases

### Use Case 1: Onboarding New Contract Type
1. Call `GET /templates/types/{type}` to see structure
2. Call `POST /templates/validate` to test your data
3. Call `POST /templates/create-from-type` to create template

### Use Case 2: Bulk Template Creation
```bash
# Create all 7 templates
for type in NDA MSA EMPLOYMENT SERVICE_AGREEMENT AGENCY_AGREEMENT PROPERTY_MANAGEMENT PURCHASE_AGREEMENT
do
  curl -X POST "$BASE_URL/templates/create-from-type/" \
    -H "Authorization: Token $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{...template data...}"
done
```

### Use Case 3: Template Validation Before Creation
```bash
# First validate the data
curl -X POST "$BASE_URL/templates/validate/" \
  -H "Authorization: Token $TOKEN" \
  -d "{...template data...}"

# If valid, then create
curl -X POST "$BASE_URL/templates/create-from-type/" \
  -H "Authorization: Token $TOKEN" \
  -d "{...template data...}"
```

---

## 📚 Files & Documentation

### Code Files
- **[contracts/template_views.py](contracts/template_views.py)** - All 5 endpoint implementations
- **[contracts/template_definitions.py](contracts/template_definitions.py)** - Template type definitions
- **[contracts/urls.py](contracts/urls.py)** - URL routing configuration

### Documentation Files  
- **[TEMPLATES_COMPLETE_GUIDE.md](TEMPLATES_COMPLETE_GUIDE.md)** - Comprehensive guide
- **[TEMPLATE_MANAGEMENT_GUIDE.md](TEMPLATE_MANAGEMENT_GUIDE.md)** - API documentation
- **[TEMPLATE_CURL_EXAMPLES.sh](TEMPLATE_CURL_EXAMPLES.sh)** - All curl examples

---

## 🎯 Next Steps

1. **Get Authentication Token** - Required for all endpoints
2. **Explore Templates** - Call GET /templates/types/
3. **Choose Template Type** - Pick from 7 available types
4. **Validate Data** - Call POST /templates/validate/
5. **Create Template** - Call POST /templates/create-from-type/

---

**Created**: January 2026  
**Template System**: Production Ready  
**Support**: All endpoints fully documented and tested
