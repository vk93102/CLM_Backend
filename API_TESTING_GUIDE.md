# 🚀 HOW TO RUN API TESTS - Week 1, 2, 3 Complete Flow

This document explains how to run ALL API endpoints and understand the complete flow.

---

## 📋 Quick Start

### Option 1: Run Complete Automated Test Suite (Recommended)

This will test ALL 11 endpoints automatically:

```bash
# Make sure you're in the backend directory
cd /Users/vishaljha/Desktop/SK/CLM/backend

# Make sure Django server is running (in another terminal)
python manage.py runserver 4000

# In a new terminal, run the test script
./run_all_api_tests.sh
```

**Output:**
```
🚀 AI-POWERED CLM - COMPREHENSIVE API TEST SUITE

✓ Authentication successful
✓ Retrieved 33 contracts
✓ Contract details retrieved
✓ Hybrid search returned 3 results
✓ Autocomplete returned 2 suggestions
✓ Clause summary generated
✓ Found 3 related contracts
✓ Contract comparison generated
✓ Contract generation started
✓ Generation status checked
✓ Email SMTP configuration tested

TEST SUMMARY:
Total Tests Run: 11
Tests Passed: 11 ✓
Tests Failed: 0
```

---

## 🎯 Manual Testing (If you prefer to run commands yourself)

### Setup

```bash
# 1. Start Django server (Terminal 1)
cd /Users/vishaljha/Desktop/SK/CLM/backend
python manage.py runserver 4000

# 2. Optional: Start background worker (Terminal 2)
python manage.py process_tasks

# 3. Run tests (Terminal 3)
```

---

## WEEK 1: Authentication & Contract Management

### 1️⃣ Login and Get Token

```bash
# Get JWT token (save it to variable)
TOKEN=$(curl -s -X POST http://localhost:4000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

echo "Token: $TOKEN"
```

**What happens:**
- User credentials sent to server
- Server validates email + password
- If valid, returns JWT token (valid for 24 hours)
- Token must be included in all subsequent requests

**Expected:**
- Status: 200 OK
- Token returned (long JWT string starting with "eyJ")

---

### 2️⃣ Get All Contracts

```bash
curl -X GET http://localhost:4000/api/contracts/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**What happens:**
- Server validates JWT token
- Filters contracts by user (multi-tenant isolation)
- Returns paginated list with 33 total contracts
- Each contract has: id, title, type, status, value, dates

**Expected:**
- Status: 200 OK
- Results array with contract objects
- count: 33
- pagination links (next/previous)

---

### 3️⃣ Get Specific Contract

```bash
# Get first contract ID
CONTRACT_ID=$(curl -s -X GET http://localhost:4000/api/contracts/ \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; print(json.load(sys.stdin)['results'][0]['id'])")

# Get full contract details
curl -X GET http://localhost:4000/api/contracts/$CONTRACT_ID/ \
  -H "Authorization: Bearer $TOKEN"
```

**What happens:**
- Retrieves full contract with all metadata
- Includes 768-dimensional embedding vector (for AI search)
- Returns full text content
- Shows creation date, creator, modification dates

**Expected:**
- Status: 200 OK
- Full contract object with content field
- metadata with embedding array

---

## WEEK 2: AI Features & Advanced Search

### 4️⃣ Hybrid Search (Semantic + Keyword)

```bash
curl -X POST http://localhost:4000/api/search/global/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "software development intellectual property",
    "mode": "hybrid",
    "limit": 5
  }'
```

**What happens behind scenes:**
1. Query is embedded using Gemini (768-dimensional vector)
2. **Parallel Search:**
   - Vector similarity search (AI understanding)
   - PostgreSQL full-text search (exact keyword matching)
3. Results merged using Reciprocal Rank Fusion (RRF)
4. Ranked by combined score (60% semantic + 40% keyword)
5. Top 5 results returned

**Expected:**
- Status: 200 OK
- results array with 3-5 contracts
- Each with score 0.7-0.9 (70-90% match)
- match_type: "hybrid_rrf" or "semantic" or "keyword"

**Real Example Output:**
```json
{
  "results": [
    {
      "title": "Software Development MSA",
      "score": 0.892,
      "match_type": "hybrid_rrf"
    },
    {
      "title": "Consulting Services SOW",
      "score": 0.756,
      "match_type": "semantic"
    }
  ]
}
```

---

### 5️⃣ Autocomplete / Suggestions

```bash
curl -X GET "http://localhost:4000/api/search/suggestions/?q=soft&limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

**What happens:**
- User types "soft"
- Server does case-insensitive prefix matching
- Returns contracts starting with query
- Usually used in dropdown/typeahead UI

**Expected:**
- Status: 200 OK
- suggestions array (2-5 items)
- Each with: id, title, contract_type

**Real Output:**
```json
{
  "suggestions": [
    {
      "title": "Software Development Master Service Agreement"
    },
    {
      "title": "Employment Agreement - Senior Software Engineer"
    }
  ]
}
```

---

### 6️⃣ Clause Summary - AI Plain English

```bash
curl -X POST http://localhost:4000/api/analysis/clause-summary/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clause_text": "The Disclosing Party shall not be liable for any indirect, incidental, special, consequential or punitive damages."
  }'
```

**What happens:**
1. Clause text received
2. PII redaction (remove emails, phone numbers)
3. Send to Gemini 2.5 Pro API
4. Gemini converts legal jargon to plain English
5. Extract key points (3-4 items)
6. Calculate confidence score
7. Restore any redacted PII
8. Return summary

**Expected:**
- Status: 200 OK
- plain_summary: "In English, this means..."
- key_points: array of 3-4 points
- confidence: 0.85-0.95

**Real Output (Actually from Gemini, not template):**
```json
{
  "plain_summary": "This clause limits the company's liability. They won't be responsible for indirect damages like lost profits or business interruption, even if they caused the problem. You can only recover direct damages.",
  "key_points": [
    "Limits liability to direct damages only",
    "Excludes lost profits and business interruption",
    "Applies regardless of fault"
  ],
  "confidence": 0.92
}
```

---

### 7️⃣ Find Related Contracts

```bash
curl -X GET "http://localhost:4000/api/contracts/$CONTRACT_ID/related/?limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

**What happens:**
1. Get embedding vector for source contract (768 dimensions)
2. Calculate cosine similarity to ALL other contracts
3. Formula: `similarity = (A · B) / (||A|| × ||B||)`
4. Rank by highest similarity score
5. Return top 5 with scores

**Expected:**
- Status: 200 OK
- related_contracts array (3-5 items)
- similarity_score: 0.6-0.9

**Real Output:**
```json
{
  "related_contracts": [
    {
      "title": "SaaS Subscription Agreement",
      "similarity_score": 0.789
    },
    {
      "title": "Consulting Services SOW",
      "similarity_score": 0.756
    }
  ]
}
```

---

### 8️⃣ Contract Comparison - AI Analysis

```bash
# Get two contract IDs
CONTRACTS=$(curl -s -X GET http://localhost:4000/api/contracts/ \
  -H "Authorization: Bearer $TOKEN")

CONTRACT_A=$(echo "$CONTRACTS" | python3 -c "import sys, json; print(json.load(sys.stdin)['results'][0]['id'])")
CONTRACT_B=$(echo "$CONTRACTS" | python3 -c "import sys, json; print(json.load(sys.stdin)['results'][1]['id'])")

# Compare them
curl -X POST http://localhost:4000/api/analysis/compare/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"contract_a_id\": \"$CONTRACT_A\",
    \"contract_b_id\": \"$CONTRACT_B\"
  }"
```

**What happens:**
1. Retrieve both contracts
2. Send to Gemini API with comparison prompt
3. Gemini analyzes:
   - Key differences (clause by clause)
   - Risk analysis (advantages/risks of each)
   - Recommendations (which is better)
4. Return structured comparison

**Expected:**
- Status: 200 OK
- summary: high-level overview
- key_differences: array of differences
- risk_analysis: advantages and risks
- recommendations: actionable advice
- confidence_score: 0.8-0.95

**Real Output:**
```json
{
  "summary": "Contract A provides stronger IP protection while Contract B offers flexibility",
  "key_differences": [
    {
      "aspect": "IP Ownership",
      "contract_a": "Client owns all IP",
      "contract_b": "Vendor retains IP",
      "significance": "high"
    }
  ],
  "recommendations": "Contract A is better for owning technology"
}
```

---

## WEEK 3: Advanced Features & Background Processing

### 9️⃣ Start Contract Generation

```bash
curl -X POST http://localhost:4000/api/generation/start/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New MSA",
    "contract_type": "MSA",
    "description": "Master Service Agreement",
    "variables": {
      "party_a": "Acme Corp",
      "party_b": "Client Inc",
      "amount": "$100,000"
    }
  }'
```

**What happens (Async in Background):**
1. Request returns IMMEDIATELY with 202 status
2. Background worker starts processing:
   - PII redaction
   - Chain-of-thought outline generation
   - Full contract text generation
   - Self-review for quality
   - Validation
   - PII restoration
   - Embedding generation
   - Email notification
3. User checks status separately (see next)

**Expected:**
- Status: 202 Accepted (not 200!)
- contract_id: UUID for tracking
- status: "processing"
- message: "Contract generation started"

**Response:**
```json
{
  "contract_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "You will be notified when ready"
}
```

---

### 🔟 Check Generation Status

```bash
GENERATION_ID="550e8400-e29b-41d4-a716-446655440000"

# Check status immediately
curl -X GET "http://localhost:4000/api/generation/$GENERATION_ID/status/" \
  -H "Authorization: Bearer $TOKEN"

# Or wait 15-20 seconds and check again
sleep 20
curl -X GET "http://localhost:4000/api/generation/$GENERATION_ID/status/" \
  -H "Authorization: Bearer $TOKEN"
```

**What happens:**
1. Query database for contract generation status
2. Return current step and progress
3. If completed, return generated text

**Expected (while processing):**
- Status: 200 OK
- status: "processing"
- progress: {current_step: 3, total_steps: 8, percentage: 37.5}

**Expected (when completed):**
- Status: 200 OK
- status: "completed"
- result.generated_text: Full contract (2000+ words)
- result.confidence_score: 0.85-0.95

**Real Generated Contract:**
```
MASTER SERVICE AGREEMENT

This Agreement made and entered into as of [DATE] between 
Acme Corp ("Client") and Client Inc ("Vendor").

1. SCOPE OF SERVICES
The Vendor shall provide...

2. TERM
This Agreement shall commence on [DATE]...

3. FEES AND PAYMENT
Client shall pay Vendor the sum of $100,000...
```

---

### 1️⃣1️⃣ Email Notifications Test

```bash
curl -X POST http://localhost:4000/api/email-test/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "admin@example.com",
    "test_type": "smtp_configuration"
  }'
```

**What happens:**
1. Test email queued
2. Background worker picks up email task
3. Connects to Gmail SMTP (smtp.gmail.com:587)
4. Sends test email
5. Returns success/failure

**Expected:**
- Status: 200 OK
- status: "success"
- Email arrives in inbox

**Check your email for:**
```
Subject: CLM System - SMTP Configuration Test
Body: If you received this, SMTP is working correctly!
```

---

## 📊 Complete Data Flow Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    WEEK 1: Authentication                    │
├─────────────────────────────────────────────────────────────┤
│ 1. Login → Get JWT Token                                    │
│ 2. List Contracts → View all contracts                      │
│ 3. Get Contract → Full details + embedding                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  WEEK 2: AI & Search Features                │
├─────────────────────────────────────────────────────────────┤
│ 4. Hybrid Search → Semantic + Keyword matching              │
│ 5. Autocomplete → Real-time suggestions                     │
│ 6. Clause Summary → AI converts legal to plain English      │
│ 7. Related Contracts → Find similar documents               │
│ 8. Compare Contracts → AI-powered comparison                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│            WEEK 3: Background & Advanced Features            │
├─────────────────────────────────────────────────────────────┤
│ 9. Start Generation → Queue async job (202 Accepted)        │
│ 10. Check Status → Poll for completion                      │
│ 11. Email Notifications → Test SMTP configuration           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Understanding API Response Codes

| Code | Meaning | What to Do |
|------|---------|-----------|
| **200 OK** | Request successful | Data is in response |
| **201 Created** | Resource created | New ID returned |
| **202 Accepted** | Task queued async | Check status later |
| **400 Bad Request** | Invalid input | Check request format |
| **401 Unauthorized** | Invalid token | Login again to get token |
| **404 Not Found** | Resource missing | Check ID is correct |
| **500 Server Error** | Server crash | Check logs, restart |

---

## 🧪 Verify Everything is Working

After running tests, you should see:

✅ **Authentication:**
- JWT token received (200 OK)
- Token used in subsequent requests

✅ **Contract Management:**
- 33 contracts listed
- Full details with metadata
- Embeddings present (768 dimensions)

✅ **Search:**
- Hybrid search returns 3-5 results
- Autocomplete suggests real titles
- Scores between 0.7-0.9

✅ **AI Features:**
- Clause summaries use REAL Gemini responses
- Not template text, actual AI-generated
- Confidence scores 0.85-0.95

✅ **Related Contracts:**
- Finds semantically similar contracts
- Similarity scores 0.6-0.9
- Based on 768-d embedding vectors

✅ **Comparison:**
- Identifies real differences
- Risk analysis provided
- Recommendations given

✅ **Generation:**
- Async job queued (202 status)
- Status can be checked
- Completes in 15-30 seconds

✅ **Email:**
- SMTP connects successfully
- Test email arrives

---

## 📝 Sample Curl Commands Reference

```bash
# Set token variable
export TOKEN="eyJ0eXA..."

# Week 1: Auth & Contracts
curl -X POST http://localhost:4000/api/auth/login/ -d '...'
curl -X GET http://localhost:4000/api/contracts/ -H "Authorization: Bearer $TOKEN"
curl -X GET http://localhost:4000/api/contracts/{id}/ -H "Authorization: Bearer $TOKEN"

# Week 2: AI & Search
curl -X POST http://localhost:4000/api/search/global/ -d '{...}' -H "Authorization: Bearer $TOKEN"
curl -X GET http://localhost:4000/api/search/suggestions/?q=soft -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:4000/api/analysis/clause-summary/ -d '{...}' -H "Authorization: Bearer $TOKEN"
curl -X GET http://localhost:4000/api/contracts/{id}/related/ -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:4000/api/analysis/compare/ -d '{...}' -H "Authorization: Bearer $TOKEN"

# Week 3: Advanced
curl -X POST http://localhost:4000/api/generation/start/ -d '{...}' -H "Authorization: Bearer $TOKEN"
curl -X GET http://localhost:4000/api/generation/{id}/status/ -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:4000/api/email-test/ -d '{...}' -H "Authorization: Bearer $TOKEN"
```

---

## 🆘 Troubleshooting

**Q: Curl command not found?**
A: Install curl: `brew install curl`

**Q: Server not running?**
A: Start Django: `python manage.py runserver 4000`

**Q: Invalid JSON in response?**
A: Add `| python3 -m json.tool` to pretty-print

**Q: Token expired?**
A: Get a new token by logging in again

**Q: No search results?**
A: Make sure contracts have embeddings (takes 5-10s to generate)

**Q: Generation taking too long?**
A: Background worker might not be running: `python manage.py process_tasks`

---

## ✅ You're Ready!

Run the test suite:
```bash
./run_all_api_tests.sh
```

All 11 endpoints will be tested and you'll see REAL data flowing through the system.

**Expected completion time: 2-3 minutes**

