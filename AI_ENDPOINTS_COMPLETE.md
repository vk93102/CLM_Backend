# AI Endpoints Implementation - Complete Guide

## Overview

This document covers three AI-powered endpoints for the Contract Lifecycle Management (CLM) backend:

1. **Endpoint 3: Draft Generation (Async)** - Generate contract drafts using RAG + Gemini
2. **Endpoint 4: Metadata Extraction** - Extract structured metadata from contracts
3. **Endpoint 5: Clause Classification** - Classify contract clauses using semantic similarity

## Architecture

### Technology Stack

- **LLM**: Google Gemini 1.5 Flash
- **Embeddings**: Voyage AI Law-2 (1024-dimensional) with semantic mock fallback
- **Async Tasks**: Celery + Redis
- **Database**: PostgreSQL via Supabase
- **Document Retrieval**: Vector similarity (cosine distance)

### Data Flow

```
Request → Validation → Processing → Result Storage → Response
   ↓         ↓            ↓             ↓           ↓
  DRF       Serializer   Task/Service  DB Model   Serializer
```

---

## Endpoint 3: Draft Generation (Async)

### Overview

Generates professional contract drafts asynchronously using:
- **RAG (Retrieval-Augmented Generation)**: Retrieves similar clauses from tenant's document repository
- **Template Support**: Optional template as base structure
- **Citation Tracking**: Records source clauses for transparency
- **Async Processing**: Returns immediately with task ID (202 Accepted)

### API Endpoints

#### POST /api/v1/ai/generate/draft/

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/generate/draft/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_type": "Service Agreement",
    "input_params": {
      "parties": ["Company A Inc.", "Company B LLC"],
      "contract_value": 50000,
      "currency": "USD",
      "start_date": "2024-02-01",
      "end_date": "2025-02-01",
      "scope": "Cloud infrastructure services including deployment and support",
      "payment_schedule": "50% upfront, 50% upon completion"
    },
    "template_id": "optional-uuid-here"
  }'
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_type` | string | ✓ | Type of contract (NDA, MSA, Service Agreement, etc.) |
| `input_params` | object | ✓ | Generation parameters (parties, dates, values, etc.) |
| `template_id` | string (UUID) | ✗ | Optional template to use as base |

**Response (202 Accepted):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "celery-task-id-12345",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "contract_type": "Service Agreement",
  "template_id": null,
  "input_params": {
    "parties": ["Company A Inc.", "Company B LLC"],
    "contract_value": 50000,
    ...
  },
  "status": "pending",
  "generated_text": null,
  "citations": [],
  "error_message": null,
  "started_at": null,
  "completed_at": null,
  "created_at": "2024-01-17T15:30:45.123456Z",
  "updated_at": "2024-01-17T15:30:45.123456Z"
}
```

**Status Flow:**
```
pending → processing → completed
                    ↓
                    failed
```

#### GET /api/v1/ai/generate/status/{task_id}/

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/ai/generate/status/550e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response (200 OK - Completed):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "celery-task-id-12345",
  "status": "completed",
  "contract_type": "Service Agreement",
  "generated_text": "SERVICE AGREEMENT\n\nThis Agreement is entered into as of 2024-02-01 (\"Effective Date\") by and between Company A Inc., a [state] corporation (\"Provider\"), and Company B LLC, a [state] limited liability company (\"Client\").\n\n1. SERVICES\nProvider agrees to provide the following services:\n   1.1 Cloud infrastructure services including deployment and support\n   1.2 Technical consulting and best practices guidance\n   1.3 Incident response and maintenance\n\n2. TERM\nThis Agreement commences on the Effective Date and continues until 2025-02-01 unless earlier terminated in accordance with the provisions hereof.\n\n3. FEES AND PAYMENT\nClient shall pay Provider $50,000 USD for the Services according to the following schedule:\n   - 50% upfront upon execution\n   - 50% upon completion of services\n\nPayments are due within 30 days of invoice...",
  "citations": [
    {
      "chunk_id": "550e8400-e29b-41d4-a716-446655440003",
      "document_id": "550e8400-e29b-41d4-a716-446655440004",
      "filename": "2023_Service_Agreement_Template.pdf",
      "chunk_number": 5,
      "similarity_score": 0.87
    },
    {
      "chunk_id": "550e8400-e29b-41d4-a716-446655440005",
      "document_id": "550e8400-e29b-41d4-a716-446655440006",
      "filename": "2024_Cloud_Services_Contract.pdf",
      "chunk_number": 12,
      "similarity_score": 0.82
    }
  ],
  "error_message": null,
  "started_at": "2024-01-17T15:30:46.500000Z",
  "completed_at": "2024-01-17T15:31:15.750000Z",
  "created_at": "2024-01-17T15:30:45.123456Z",
  "updated_at": "2024-01-17T15:31:15.750000Z"
}
```

**Response (200 OK - Processing):**
```json
{
  "status": "processing",
  "started_at": "2024-01-17T15:30:46.500000Z",
  "...other fields..."
}
```

**Response (200 OK - Failed):**
```json
{
  "status": "failed",
  "error_message": "Failed to generate embedding for RAG context",
  "completed_at": "2024-01-17T15:35:22.000000Z",
  "...other fields..."
}
```

**Response (404 Not Found):**
```json
{
  "error": "Task not found"
}
```

### Implementation Details

#### Step 1: Template Retrieval
- If `template_id` is provided, retrieves from `ContractTemplate` model
- Uses template metadata for context but not full text (currently stores R2 key)

#### Step 2: RAG Context Building
- Generates embedding for search query: `"{contract_type} {input_params}"`
- Searches tenant's `DocumentChunk` table for embeddings
- Calculates cosine similarity with threshold 0.3
- Retrieves top 5 similar chunks ordered by similarity
- Records chunk IDs for citation tracking

#### Step 3: Gemini Generation
- Constructs prompt with:
  - Contract type and parameters
  - Reference template info
  - Top 5 RAG context clauses (limited to 800 chars each)
  - Professional generation instructions
- Uses `gemini-1.5-flash` model for speed
- Returns generated draft text

#### Step 4: Result Storage
- Stores complete draft in `DraftGenerationTask.generated_text`
- Stores citations array with source references
- Updates status to "completed" or "failed"
- Records timestamps for performance tracking

### Celery Task Implementation

**File:** `ai/tasks.py`

```python
@shared_task(bind=True, max_retries=3)
def generate_draft_async(self, task_id: str, tenant_id: str, contract_type: str,
                        input_params: dict, template_id: str = None):
    # Implements the 4-step workflow with error handling
    # Retries with exponential backoff on failure
```

**Retry Logic:**
- Max 3 retries with exponential backoff (60s, 120s, 240s)
- Captures error message on final failure
- Logs detailed information for debugging

### Error Handling

| Error | Status | Cause | Recovery |
|-------|--------|-------|----------|
| Missing contract_type | 400 | Validation | Provide required field |
| Template not found | 200 | Reference issue | Proceeds without template |
| No RAG results | 200 | Empty repository | Generates without context |
| Gemini timeout | 500 + Retry | API issue | Automatic retry |
| Celery unavailable | 500 | Infrastructure | Manual retry needed |

---

## Endpoint 4: Metadata Extraction

### Overview

Extracts structured metadata from contracts using Gemini's ability to parse and understand legal documents.

**Extracted Fields:**
- **Parties**: Names and roles (Licensor, Licensee, Buyer, Seller, etc.)
- **Dates**: Effective date and termination/expiration date
- **Value**: Contract value and currency (ISO 4217 code)

### API Endpoint

#### POST /api/v1/ai/extract/metadata/

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/extract/metadata/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | string (UUID) | ✓ | ID of the document to extract from |

**Response (200 OK):**
```json
{
  "parties": [
    {
      "name": "Acme Corporation",
      "role": "Licensor"
    },
    {
      "name": "Widget Industries LLC",
      "role": "Licensee"
    }
  ],
  "effective_date": "2024-01-15",
  "termination_date": "2025-01-15",
  "contract_value": {
    "amount": 150000,
    "currency": "USD"
  }
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Document has no text content",
  "details": "Please ensure OCR/text extraction is complete."
}
```

**Response (404 Not Found):**
```json
{
  "error": "Document not found"
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "Metadata extraction failed",
  "details": "Failed to parse extraction response"
}
```

### Implementation Details

#### JSON Schema Enforcement
The prompt provides explicit JSON schema to Gemini:
```json
{
  "parties": [
    {"name": "string", "role": "string"}
  ],
  "effective_date": "YYYY-MM-DD or null",
  "termination_date": "YYYY-MM-DD or null",
  "contract_value": {
    "amount": "number or null",
    "currency": "ISO 4217 code or null"
  }
}
```

#### Extraction Rules
1. **Parties**: Extracted from contract header/signature section with their roles
2. **Dates**: Searches for keywords like "Effective Date", "Commencement", "Termination", "Expiration"
3. **Value**: Parses numeric amounts without currency symbols
4. **Currency**: Uses ISO 4217 codes (USD, EUR, GBP, CAD, etc.)
5. **Null Values**: Used for missing or unclear fields

#### Processing
- Limits document text to first 10,000 characters for API efficiency
- Cleans markdown code blocks from response
- Validates JSON structure and required keys
- Ensures contract_value has amount and currency fields

### Error Handling

| Error | Status | Cause | Solution |
|-------|--------|-------|----------|
| Missing document_id | 400 | Invalid request | Provide document UUID |
| Document not found | 404 | Invalid document_id | Verify ID and permissions |
| No text content | 400 | OCR incomplete | Complete text extraction first |
| Invalid JSON response | 500 | Gemini parse error | Retry or check content |
| Empty response | 500 | API issue | Retry or check model |

---

## Endpoint 5: Clause Classification

### Overview

Classifies contract clauses by semantic similarity to pre-defined anchor clauses.

**Anchor Clauses:**
- Confidentiality, Limitation of Liability, Indemnification
- Termination, Payment Terms, Intellectual Property
- Governing Law, Dispute Resolution, Warranty Disclaimer
- Force Majeure, Representations & Warranties, NDA
- Services Description, Assignment & Delegation
- *(14 total, easily extensible)*

### API Endpoint

#### POST /api/v1/ai/classify/

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/classify/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The parties agree to maintain the confidentiality of all non-public information disclosed in connection with this Agreement. Confidential Information includes but is not limited to technical data, business plans, customer lists, and financial information. Each party agrees not to disclose this information to third parties without prior written consent."
  }'
```

**Request Body:**

| Field | Type | Required | Min Length | Description |
|-------|------|----------|------------|-------------|
| `text` | string | ✓ | 20 chars | Clause text to classify |

**Response (200 OK):**
```json
{
  "label": "Confidentiality",
  "category": "Legal",
  "confidence": 0.96
}
```

**Response (400 Bad Request):**
```json
{
  "error": "text must be at least 20 characters"
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "Classification failed",
  "details": "Failed to generate text embedding"
}
```

### Implementation Details

#### Semantic Similarity Process

1. **Query Embedding**: Generates 1024-dimensional embedding of input text using Voyage AI Law-2
2. **Anchor Embeddings**: Pre-computed embeddings for each anchor clause's example text
3. **Cosine Similarity**: Calculates similarity between query and each anchor
4. **Confidence Score**: Normalizes similarity to 0-1 scale
5. **Selection**: Returns anchor with highest confidence score

#### Math

```
Similarity = (Query · Anchor) / (||Query|| × ||Anchor||)
Confidence = Normalized Similarity to [0, 1]
Best Match = argmax(Confidence)
```

#### Embedding Generation

- **Voyage AI Law-2**: 1024-dimensional embeddings optimized for legal documents
- **Fallback**: Semantic mock embeddings based on keyword presence
- **Caching**: Can be extended to Redis for performance

### Anchor Clauses Reference

| Label | Category | Purpose |
|-------|----------|---------|
| Confidentiality | Legal | Protect non-public information |
| Limitation of Liability | Legal | Cap damages exposure |
| Indemnification | Legal | Compensate for third-party claims |
| Termination | Operational | Exit conditions and procedures |
| Payment Terms | Financial | Fees, timing, and conditions |
| Intellectual Property | Legal | Ownership of created works |
| Governing Law | Legal | Jurisdiction and applicable law |
| Dispute Resolution | Legal | Conflict resolution procedures |
| Warranty Disclaimer | Legal | Deny implied warranties |
| Force Majeure | Legal | Excuse for unforeseen events |
| Representations & Warranties | Legal | Party assurances |
| Non-Disclosure Agreement | Legal | Confidentiality specifics |
| Services Description | Operational | Scope of work details |
| Assignment & Delegation | Legal | Transfer restrictions |

### Initialization

#### Django Management Command

```bash
python manage.py initialize_anchors
```

**Options:**
- `--clear`: Remove existing anchors before creating new ones

**Output:**
```
✓ Created: Confidentiality (Legal)
✓ Created: Limitation of Liability (Legal)
...
✓ Initialization Complete!
  Created: 14
  Updated: 0
  Failed: 0
  Total Active Anchors: 14
```

#### Manual Initialization

```python
from ai.initialize_anchor_clauses import initialize_anchor_clauses
initialize_anchor_clauses()
```

### Error Handling

| Error | Status | Cause | Solution |
|-------|--------|-------|----------|
| Empty text | 400 | No input | Provide non-empty text |
| Text too short | 400 | < 20 chars | Provide longer clause |
| No anchors found | 500 | DB empty | Run initialize_anchors |
| Embedding failed | 500 | API error | Check Voyage AI access |
| Calculation error | 500 | Math error | Check embedding format |

---

## Integration Examples

### Full Workflow Example

```python
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

# 1. Generate Draft
draft_response = requests.post(
    f"{BASE_URL}/ai/generate/draft/",
    headers=HEADERS,
    json={
        "contract_type": "NDA",
        "input_params": {
            "parties": ["Company A", "Company B"],
            "scope": "Software development services"
        }
    }
)
task_id = draft_response.json()["id"]
print(f"Draft generation started: {task_id}")

# 2. Poll for completion
while True:
    status_response = requests.get(
        f"{BASE_URL}/ai/generate/status/{task_id}/",
        headers=HEADERS
    )
    status = status_response.json()
    
    if status["status"] == "completed":
        print("Draft ready!")
        print(f"Generated: {len(status['generated_text'])} characters")
        print(f"Sources: {len(status['citations'])} citations")
        break
    elif status["status"] == "failed":
        print(f"Generation failed: {status['error_message']}")
        break
    
    print("Still processing...")
    time.sleep(2)

# 3. Extract metadata from a document
meta_response = requests.post(
    f"{BASE_URL}/ai/extract/metadata/",
    headers=HEADERS,
    json={"document_id": DOCUMENT_ID}
)
metadata = meta_response.json()
print(f"Parties: {metadata['parties']}")
print(f"Value: {metadata['contract_value']}")

# 4. Classify a clause
classify_response = requests.post(
    f"{BASE_URL}/ai/classify/",
    headers=HEADERS,
    json={"text": "The parties maintain confidentiality..."}
)
classification = classify_response.json()
print(f"Classified as: {classification['label']} ({classification['confidence']:.0%})")
```

### Frontend Integration

```javascript
// Draft Generation
async function generateDraft(contractType, params) {
  const response = await fetch('/api/v1/ai/generate/draft/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      contract_type: contractType,
      input_params: params
    })
  });
  return response.json();
}

// Poll Status
async function checkDraftStatus(taskId) {
  const response = await fetch(`/api/v1/ai/generate/status/${taskId}/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const task = await response.json();
  
  if (task.status === 'completed') {
    showDraft(task.generated_text, task.citations);
  } else if (task.status === 'failed') {
    showError(task.error_message);
  } else {
    setTimeout(() => checkDraftStatus(taskId), 2000);
  }
}
```

---

## Database Models

### DraftGenerationTask
```python
class DraftGenerationTask(models.Model):
    id = UUIDField(primary_key=True)
    tenant_id = UUIDField()
    user_id = UUIDField()
    task_id = CharField(max_length=255, unique=True)  # Celery task ID
    contract_type = CharField(max_length=100)
    template_id = UUIDField(null=True)
    input_params = JSONField()
    status = CharField(choices=['pending', 'processing', 'completed', 'failed'])
    generated_text = TextField()
    citations = JSONField()  # List of source references
    error_message = TextField()
    started_at = DateTimeField(null=True)
    completed_at = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### ClauseAnchor
```python
class ClauseAnchor(models.Model):
    id = UUIDField(primary_key=True)
    label = CharField(max_length=100, unique=True)
    description = TextField()
    category = CharField(max_length=50)
    example_text = TextField()
    embedding = JSONField()  # 1024-dimensional vector
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

---

## Performance Considerations

### Draft Generation
- **Processing Time**: 5-30 seconds depending on Gemini load
- **Bottleneck**: Gemini API call (cannot parallelize)
- **Optimization**: Pre-compute common templates
- **Caching**: Store generated drafts for similar inputs

### Metadata Extraction
- **Processing Time**: 2-5 seconds per document
- **Bottleneck**: Gemini parsing
- **Optimization**: Batch process multiple documents
- **Caching**: Cache results by document hash

### Clause Classification
- **Processing Time**: <500ms
- **Bottleneck**: Embedding generation (can be cached)
- **Optimization**: Batch embeddings for bulk classification
- **Caching**: Redis for embedding cache (200ms → 1ms)

---

## Security

### Authentication
- All endpoints require valid Supabase JWT
- Tenant ID extracted from JWT claims
- Multi-tenant isolation enforced

### Data Privacy
- Documents filtered by tenant_id
- No cross-tenant data leakage
- Embeddings not shared across tenants

### API Keys
- `GEMINI_API_KEY`: Used for generation and extraction
- `VOYAGE_API_KEY`: Used for embeddings (optional, fallback to mock)
- Stored in environment variables, never committed

---

## Troubleshooting

### Common Issues

**Issue**: "No anchor clauses configured"
- **Cause**: Clauses not initialized
- **Fix**: `python manage.py initialize_anchors`

**Issue**: "Failed to generate embedding"
- **Cause**: Voyage AI unavailable or API key missing
- **Fix**: Check VOYAGE_API_KEY or restart with fallback mode

**Issue**: "Task not found"
- **Cause**: Wrong task_id or expired task
- **Fix**: Use correct UUID, check created_at timestamp

**Issue**: Slow metadata extraction
- **Cause**: Large document or Gemini overload
- **Fix**: Reduce document size, add retry logic

### Debug Mode

```python
# Enable detailed logging
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'ai': {'level': 'DEBUG', 'handlers': ['console']},
        'repository.embeddings_service': {'level': 'DEBUG', 'handlers': ['console']},
    }
}
```

---

## Future Enhancements

1. **Multiple Template Support**: Store multiple template versions
2. **Batch Processing**: Process multiple documents in parallel
3. **Fine-tuning**: Train models on tenant-specific contracts
4. **Caching Layer**: Redis for embeddings and results
5. **Advanced RAG**: Hybrid search (BM25 + semantic)
6. **Custom Anchors**: Tenant-defined clause types
7. **Confidence Thresholds**: Configurable by endpoint
8. **Webhook Notifications**: Task completion callbacks
9. **Rate Limiting**: Per-user and per-tenant quotas
10. **Analytics**: Track usage, accuracy, and performance

---

## Support & Maintenance

### Monitoring
- Check Celery queue status: `celery -A clm_backend inspect active`
- Monitor Gemini API usage in Google Cloud Console
- Track Voyage AI embeddings in account dashboard

### Updates
- New anchor clauses: Edit `ANCHOR_CLAUSES` list and re-run initialization
- Gemini model upgrade: Change `gemini-1.5-flash` to new version
- Voyage model upgrade: Update `VoyageEmbeddingsService.MODEL`

### Backup & Recovery
- DraftGenerationTask records persist indefinitely (audit trail)
- ClauseAnchors are system data (can be re-initialized)
- Document embeddings stored in PostgreSQL
