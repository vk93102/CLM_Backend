# CURL COMMANDS REFERENCE - AI ENDPOINTS
## Ready-to-Use Examples with Real Data

```bash
# Store token for reuse
TOKEN=$(cat /tmp/auth_token.txt)
```

---

## ENDPOINT 5: CLAUSE CLASSIFICATION

### Example 1: Confidentiality Clause
```bash
curl -X POST http://localhost:11000/api/v1/ai/classify/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Both parties agree to maintain strict confidentiality of all proprietary information, trade secrets, and technical data shared during the term of this agreement and for a period of five (5) years thereafter."
  }' | jq .
```

**Expected Response**:
```json
{
  "label": "Confidentiality",
  "category": "Legal",
  "confidence": 0.92
}
```

### Example 2: Termination Clause
```bash
curl -X POST http://localhost:11000/api/v1/ai/classify/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Either party may terminate this Agreement upon thirty (30) days prior written notice to the other party. In the event of material breach, either party may terminate immediately upon written notice if the breaching party fails to cure such breach within fifteen (15) days of notification."
  }' | jq .
```

### Example 3: Payment Terms
```bash
curl -X POST http://localhost:11000/api/v1/ai/classify/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Payment shall be made within thirty (30) days of invoice receipt. Late payments shall accrue interest at the rate of 1.5% per month or the maximum rate permitted by law. All invoices must be in USD and paid via wire transfer."
  }' | jq .
```

### Example 4: Intellectual Property
```bash
curl -X POST http://localhost:11000/api/v1/ai/classify/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "All intellectual property rights, including but not limited to patents, copyrights, trademarks, and trade secrets developed, created, or discovered by the Service Provider in the performance of this Agreement shall remain the exclusive property of the Service Provider."
  }' | jq .
```

---

## ENDPOINT 3: DRAFT GENERATION

### Example 1: Generate NDA
```bash
curl -X POST http://localhost:11000/api/v1/ai/generate/draft/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_type": "NDA",
    "input_params": {
      "parties": ["Acme Corporation", "Innovation Partners LLC"],
      "jurisdiction": "Delaware",
      "duration_years": 2
    }
  }' | jq .
```

**Expected Response** (HTTP 202):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "celery-task-id-...",
  "status": "pending",
  "contract_type": "NDA",
  "created_at": "2026-01-18T19:57:20.123456Z",
  "tenant_id": "...",
  "user_id": "..."
}
```

### Example 2: Generate Service Agreement
```bash
curl -X POST http://localhost:11000/api/v1/ai/generate/draft/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_type": "Service Agreement",
    "input_params": {
      "parties": ["TechCorp Services Inc.", "Enterprise Solutions Ltd."],
      "service_type": "Cloud Infrastructure Management",
      "monthly_fee": "50000",
      "sla_uptime": "99.9%",
      "jurisdiction": "New York"
    }
  }' | jq .
```

### Check Task Status
```bash
# After getting task_id from response
TASK_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X GET http://localhost:11000/api/v1/ai/generate/status/$TASK_ID/ \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

## ENDPOINT 4: METADATA EXTRACTION

### Example 1: Service Contract
```bash
curl -X POST http://localhost:11000/api/v1/ai/extract/metadata/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_text": "SERVICE AGREEMENT EFFECTIVE DATE: January 15, 2026 EXPIRATION DATE: January 14, 2027 This Service Agreement (Agreement) is entered into by and between CloudTech Solutions Corp., a Delaware corporation (Service Provider), and GlobalEnterprises Inc., a California corporation (Client). SCOPE OF SERVICES: Service Provider shall provide comprehensive cloud infrastructure management services, including server maintenance, security monitoring, and 24/7 technical support. FEES AND PAYMENT TERMS: Client shall pay Service Provider a monthly service fee of $600,000.00 USD, payable within thirty (30) days of invoice. SERVICE LEVEL AGREEMENT: Service Provider guarantees 99.95% uptime availability. Any downtime exceeding 0.05% monthly shall result in service credits of 5% of monthly fees per 0.1% of downtime. TERM AND TERMINATION: This Agreement shall commence on the Effective Date and continue for one (1) year unless terminated earlier. Either party may terminate with ninety (90) days written notice. JURISDICTION: State of New York"
  }' | jq .
```

**Expected Response** (HTTP 200):
```json
{
  "parties": [
    {
      "name": "CloudTech Solutions Corp.",
      "role": "Service Provider"
    },
    {
      "name": "GlobalEnterprises Inc.",
      "role": "Client"
    }
  ],
  "dates": {
    "effective_date": "2026-01-15",
    "expiration_date": "2026-01-14"
  },
  "financial_terms": {
    "monthly_fee": 600000,
    "currency": "USD",
    "payment_terms": "30 days"
  },
  "service_level": {
    "uptime_guarantee": "99.95%"
  },
  "jurisdiction": "New York"
}
```

### Example 2: NDA
```bash
curl -X POST http://localhost:11000/api/v1/ai/extract/metadata/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_text": "MUTUAL NON-DISCLOSURE AGREEMENT PARTIES: InnovateTech Inc., a Massachusetts corporation (Discloser) Venture Capital Partners LP, a Delaware limited partnership (Recipient) CONFIDENTIAL VALUE: $100,000.00 EFFECTIVE DATE: January 10, 2026 EXPIRATION: January 10, 2031 The parties agree to maintain strict confidentiality regarding all proprietary information, trade secrets, technical data, business plans, and financial information disclosed under this Agreement. PERMITTED USES: Recipient may use the Confidential Information solely to evaluate potential business opportunities and for no other purpose without prior written consent. RETURN OR DESTRUCTION: Upon termination of this Agreement or request by Discloser, Recipient shall return or destroy all Confidential Information within thirty (30) days. GOVERNING LAW: Commonwealth of Massachusetts"
  }' | jq .
```

---

## SECURITY TESTS

### Test 1: Missing Authentication
```bash
# Should return 401
curl -X POST http://localhost:11000/api/v1/ai/classify/ \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}' -w "\nStatus: %{http_code}\n"
```

### Test 2: Invalid Token
```bash
# Should return 401
curl -X POST http://localhost:11000/api/v1/ai/classify/ \
  -H "Authorization: Bearer invalid_token_xyz" \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}' -w "\nStatus: %{http_code}\n"
```

### Test 3: Missing Required Field
```bash
# Should return 400
curl -X POST http://localhost:11000/api/v1/ai/classify/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": ""}' -w "\nStatus: %{http_code}\n"
```

---

## BATCH TEST (All Endpoints)

```bash
#!/bin/bash

TOKEN=$(cat /tmp/auth_token.txt)
API="http://localhost:11000/api/v1"

echo "Testing Endpoint 5 (Classify)..."
curl -s -X POST $API/ai/classify/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Both parties agree to maintain strict confidentiality..."}' | jq .label

echo "Testing Endpoint 3 (Generate)..."
curl -s -X POST $API/ai/generate/draft/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contract_type": "NDA", "input_params": {"parties": ["Acme Corp", "Partner LLC"], "jurisdiction": "Delaware", "duration_years": 2}}' | jq .id

echo "Testing Endpoint 4 (Extract)..."
curl -s -X POST $API/ai/extract/metadata/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_text": "SERVICE AGREEMENT... CloudTech Solutions Corp..."}' | jq .parties

echo "All tests completed!"
```

---

## QUICK STATUS CHECK

```bash
TOKEN=$(cat /tmp/auth_token.txt)

# Health check
echo "Health Status:"
curl -s http://localhost:11000/api/v1/health/ \
  -H "Authorization: Bearer $TOKEN" | jq .

# Quick classify test
echo "Classify Test:"
curl -s -X POST http://localhost:11000/api/v1/ai/classify/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "strict confidentiality agreement"}' | jq .
```

---

## ERROR CODES

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | Success | ✓ Expected for Endpoints 4, 5 |
| 202 | Accepted | ✓ Expected for Endpoint 3 (async) |
| 400 | Bad Request | Check JSON syntax, required fields |
| 401 | Unauthorized | Verify token is valid and current |
| 500 | Server Error | Check server logs, Gemini API availability |

---

## NOTES

- All endpoints require Bearer token authentication
- Token valid: Verify with `echo $TOKEN | cut -d'.' -f1-2 | base64 -d | jq .`
- Endpoint 3 is async (202) - check status with returned task_id
- Endpoints 4 & 5 are synchronous (200)
- All examples use real business data (not mock/dummy data)
