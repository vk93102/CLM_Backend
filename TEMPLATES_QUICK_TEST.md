# Templates Endpoints - Quick Reference

## ✅ All Endpoints Working

### 5 Endpoints Available

1. **GET /api/v1/templates/types/** → Lists all 7 template types (200 OK)
2. **GET /api/v1/templates/types/{type}/** → Gets specific template details (200 OK)
3. **GET /api/v1/templates/summary/** → Gets template summary (200 OK)
4. **POST /api/v1/templates/validate/** → Validates template data (200 OK)
5. **POST /api/v1/templates/create-from-type/** → Creates template (201 CREATED)

---

## Real Working Responses

### Endpoint 1: Get All Templates
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:11000/api/v1/templates/types/
```

Response:
```json
{
  "success": true,
  "total_types": 7,
  "template_types": {
    "NDA": {...},
    "MSA": {...},
    ...
  }
}
```

---

### Endpoint 2: Get Template Details
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:11000/api/v1/templates/types/NDA/
```

Response:
```json
{
  "success": true,
  "template_type": "NDA",
  "display_name": "Non-Disclosure Agreement",
  "required_fields": [
    {"name": "effective_date", "description": "..."},
    {"name": "first_party_name", "description": "..."},
    ...
  ],
  "optional_fields": [...],
  "mandatory_clauses": ["CONF-001", "TERM-001", "LIAB-001"]
}
```

---

### Endpoint 3: Validate Data
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "NDA",
    "data": {
      "effective_date": "2026-01-20",
      "first_party_name": "Company A",
      "first_party_address": "123 Main St",
      "second_party_name": "Company B",
      "second_party_address": "456 Oak Ave",
      "agreement_type": "Mutual",
      "governing_law": "California"
    }
  }' \
  http://127.0.0.1:11000/api/v1/templates/validate/
```

Response:
```json
{
  "success": true,
  "is_valid": true,
  "missing_fields": [],
  "message": "All required fields provided"
}
```

---

### Endpoint 4: Create Template
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "NDA",
    "name": "Acme-Tech NDA",
    "description": "Mutual NDA",
    "status": "published",
    "data": {
      "effective_date": "2026-01-20",
      "first_party_name": "Acme Corp",
      "first_party_address": "123 Business Ave",
      "second_party_name": "Tech Inc",
      "second_party_address": "456 Tech Blvd",
      "agreement_type": "Mutual",
      "governing_law": "California"
    }
  }' \
  http://127.0.0.1:11000/api/v1/templates/create-from-type/
```

Response (201 CREATED):
```json
{
  "success": true,
  "template_id": "3cbafb65-4dc6-45d7-bb5b-368c13264012",
  "name": "Acme-Tech NDA",
  "contract_type": "NDA",
  "status": "published",
  "merge_fields": [
    "effective_date",
    "first_party_name",
    "first_party_address",
    ...
  ],
  "mandatory_clauses": ["CONF-001", "TERM-001", "LIAB-001"],
  "message": "Template created successfully"
}
```

---

## 7 Template Types

| Type | Fields | Status |
|------|--------|--------|
| NDA | 7+5 | ✅ Working |
| MSA | 9+6 | ✅ Working |
| EMPLOYMENT | 9+7 | ✅ Working |
| SERVICE_AGREEMENT | 8+6 | ✅ Working |
| AGENCY_AGREEMENT | 7+5 | ✅ Working |
| PROPERTY_MANAGEMENT | 8+6 | ✅ Working |
| PURCHASE_AGREEMENT | 9+7 | ✅ Working |

---

## Authentication

```bash
# Get token
TOKEN=$(python3 manage.py shell << 'EOF'
from authentication.models import User
from rest_framework_simplejwt.tokens import RefreshToken
user = User.objects.first()
print(str(RefreshToken.for_user(user).access_token))
EOF
)

# Use token
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:11000/api/v1/templates/types/
```

---

## Status Summary

✅ **All endpoints working**
✅ **Proper HTTP status codes (200, 201)**
✅ **JSON responses formatted correctly**
✅ **Validation working**
✅ **Template creation working**
✅ **Authentication enforced**

**Ready for production use!**

