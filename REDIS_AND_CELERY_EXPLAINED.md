# Why Redis for AI Endpoints

## Architecture Explanation

### Celery Task Queue (Draft Generation - Endpoint 3)

**Why Redis is needed for Draft Generation:**

The draft generation endpoint is **asynchronous** because:
1. Gemini API calls take 5-30 seconds
2. Clients shouldn't wait blocking HTTP requests for that long
3. Task should run in background worker process

**Flow:**
```
Client Request
    ↓
create_draft() → queue task in Redis
    ↓
return 202 Accepted with task_id (immediately!)
    ↓
Client polls status with task_id
    ↓
Celery worker processes task from Redis queue
    ↓
Worker calls Gemini API
    ↓
Result stored in DB
    ↓
Client fetches completed result
```

**Without Redis:**
- Would need to call Gemini synchronously
- Client would wait 30 seconds for HTTP response
- Poor user experience
- Timeouts if server restarts

**With Redis:**
- Task queued immediately
- Client gets instant response (202)
- Worker processes async
- No timeout issues
- Can scale to multiple workers

### Anchor Clauses (NOT Dummy Data - Endpoint 5)

These are **legitimate reference data**, not dummy data:

- **Purpose**: Semantic anchors for classification
- **Pre-computed embeddings**: Each clause type has a 1024-dimensional vector
- **Real use case**: When user uploads a clause, we compare it to these anchors
- **Not optional**: Classification endpoint requires these to function

Think of it like a dictionary for legal clause types - you need reference definitions to classify new clauses.

---

## How to Test WITHOUT Celery Workers (Synchronous Mode)

If you don't want to run Celery workers, you can test synchronously:

### Option 1: Skip Draft Generation (Endpoints 4 & 5 don't need Redis)

Test only:
- Metadata Extraction (Endpoint 4) - Pure Gemini call
- Clause Classification (Endpoint 5) - Pure embedding similarity

### Option 2: Mock Celery for Testing

```python
# In settings.py for testing
CELERY_TASK_ALWAYS_EAGER = True  # Execute immediately instead of queue
```

### Option 3: Run Celery Worker in Same Process

```bash
# Single terminal with both Django + Celery
celery -A clm_backend worker --pool=solo
```

---

## Redis is Standard Industry Practice

- **Django**: Uses Redis for caching, sessions
- **FastAPI/Flask**: Uses Redis for task queues
- **Production**: ALL async frameworks use message brokers (Redis, RabbitMQ, AWS SQS)

Redis is lightweight and free - it's the standard choice.

---

## Summary

| Component | Why | Optional? |
|-----------|-----|-----------|
| Redis | Message broker for async draft generation | Only needed for Endpoint 3 |
| Celery Worker | Process draft generation tasks | Only needed for Endpoint 3 |
| Anchor Clauses | Reference data for classification | Required for Endpoint 5 |
| Gemini API | LLM for generation & extraction | Required for Endpoints 3 & 4 |
| Voyage AI | Embeddings for semantic similarity | Optional (has mock fallback) |

You need Redis + Celery **only** if you want the async draft generation feature.
For metadata extraction and classification, you only need Gemini API.
