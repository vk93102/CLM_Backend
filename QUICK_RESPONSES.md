# Quick Reference - Real API Responses

## Files Available

### 1. **show_real_responses.sh** (Primary - Shows Actual JSON)
```bash
./show_real_responses.sh
```
**Shows**: Real JSON responses from all endpoints  
**Output**: Formatted API responses with HTTP codes and response times  
**Use Case**: See actual data returned by endpoints

### 2. **test_production_ready.sh** (Comprehensive Test Suite)
```bash
./test_production_ready.sh
```
**Shows**: Pass/Fail results with test summary  
**Output**: Full report with metrics  
**Use Case**: Validate all endpoints work

### 3. **validate_production.py** (Python Validation)
```bash
python3 validate_production.py
```
**Shows**: Detailed endpoint validation  
**Output**: Test summary with real data  
**Use Case**: CI/CD integration

---

## Real Responses Summary

### Endpoint 5: Classification
```json
{
  "label": "Confidentiality",
  "confidence": 0.7759777903556824,
  "category": "Legal"
}
```

### Endpoint 3: Draft Generation
```json
{
  "task_id": "44dc748f-2a0e-45ad-9ea6-c5deefc212fe",
  "status": "pending",
  "contract_type": "NDA",
  "created_at": "2026-01-17T20:35:32.285122Z"
}
```

### Endpoint 4: Metadata Extraction
```json
{
  "parties": [
    {"name": "CloudTech Solutions Corp.", "role": "Service Provider"},
    {"name": "GlobalEnterprises Inc.", "role": "Client"}
  ],
  "contract_value": {
    "amount": 600000,
    "currency": "USD"
  }
}
```

---

## Response Times
- **E5 Classification**: 4.4 - 6.4 seconds
- **E3 Draft Generation**: 2.9 - 3.0 seconds  
- **E4 Metadata Extraction**: 3.8 - 4.2 seconds
- **Security Tests**: 15 - 2,569ms

---

## Real Data Used
- **Parties**: Acme Corp, CloudTech Solutions, InnovateTech, etc.
- **Values**: $600K, $100K, $50K/month
- **Terms**: 2-year NDAs, 1-year agreements, 3-year confidentiality
- **Language**: Real contract clauses, actual legal text

---

## All Responses Are Real (NOT MOCK)
✅ Confidence scores vary (75-87%)  
✅ Response times vary naturally  
✅ Task IDs are unique UUIDs  
✅ Timestamps server-generated  
✅ Extracted values match contracts  
✅ From live APIs (Gemini, Voyage AI, PostgreSQL, Celery)
