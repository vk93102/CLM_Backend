# 🔧 Production-Level Search Endpoints Testing Suite

**Port**: 11000 | **Rate Limit**: 3 calls per minute (20 seconds between calls)

---

## 📋 Quick Start

### 1. Run Complete Test Suite
```bash
./test_search_endpoints.sh
```

### 2. Run with Pre-configured Token
```bash
export JWT_TOKEN="your-jwt-token-here"
./test_search_endpoints.sh
```

### 3. Run with Custom Credentials
```bash
export TEST_EMAIL="admin@example.com"
export TEST_PASSWORD="admin123"
./test_search_endpoints.sh
```

---

## 🎯 What Gets Tested

The automated test suite runs **8 comprehensive tests** with automatic rate limiting:

1. **Health Check** - API availability
2. **Semantic Search** (Standard) - Query: "confidentiality", threshold: 0.2
3. **Keyword Search** - Query: "payment"
4. **Clause-Based Search** - Query: "termination"
5. **Hybrid Search** - Query: "data protection", combines semantic + keyword
6. **Semantic Search (Strict)** - Query: "confidentiality", threshold: 0.7
7. **Semantic Search (Loose)** - Query: "breach", threshold: 0.1
8. **Advanced Search** - With filters, query: "liability"

---

## 📊 Test Coverage

### Search Types Covered
✅ Semantic search (different thresholds)  
✅ Keyword search  
✅ Clause-based search  
✅ Hybrid search (semantic + keyword)  
✅ Advanced search with filters  

### Scenarios Tested
✅ Normal queries  
✅ Strict filtering (high threshold)  
✅ Loose filtering (low threshold)  
✅ Multiple top_k values  
✅ Error handling  

### Rate Limiting
✅ Automatic 20-second delays between calls  
✅ 3 calls per minute compliance  
✅ Prevents server overload  
✅ Production-safe  

---

## 🔐 Authentication

### Automatic Token Retrieval
The script automatically obtains a JWT token if not provided:
```bash
./test_search_endpoints.sh
# Script will prompt for login
```

### Using Existing Token
```bash
export JWT_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
./test_search_endpoints.sh
```

---

## 📝 Manual Testing

Use `CURL_ENDPOINTS_REFERENCE.sh` for manual testing:

### Individual Endpoint Tests
```bash
# Semantic Search
curl -X GET "http://localhost:11000/api/search/semantic/?q=confidentiality&threshold=0.2&top_k=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Keyword Search
curl -X GET "http://localhost:11000/api/search/keyword/?q=payment&top_k=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Clause Search
curl -X GET "http://localhost:11000/api/search/clause/?q=termination&top_k=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Hybrid Search
curl -X GET "http://localhost:11000/api/search/hybrid/?q=data+protection&threshold=0.3&top_k=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Advanced Search
curl -X POST "http://localhost:11000/api/search/advanced/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "liability", "filters": {"document_type": "agreement"}, "top_k": 10}'
```

---

## 📈 Response Examples

### Success Response (200 OK)
```json
{
  "success": true,
  "count": 2,
  "search_type": "semantic",
  "query": "confidentiality",
  "threshold": 0.2,
  "results": [
    {
      "chunk_id": "abc-123",
      "document_id": "doc-456",
      "text": "Confidentiality obligations...",
      "similarity": 0.9518,
      "similarity_percentage": "95.18%",
      "filename": "agreement.pdf",
      "document_title": "Master Service Agreement"
    },
    {
      "chunk_id": "def-789",
      "text": "Data protection and privacy...",
      "similarity": 0.3039,
      "similarity_percentage": "30.39%"
    }
  ]
}
```

### Error Response (400 Bad Request)
```json
{
  "success": false,
  "error": "Query parameter 'q' is required",
  "code": "MISSING_QUERY"
}
```

### Authentication Error (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## ⚙️ Configuration

### Rate Limiting
Edit `test_search_endpoints.sh` to change rate limit:

```bash
RATE_LIMIT_SECONDS=20  # 3 calls per minute (20 = 60/3)
```

Change to:
```bash
RATE_LIMIT_SECONDS=10  # 6 calls per minute
RATE_LIMIT_SECONDS=30  # 2 calls per minute
RATE_LIMIT_SECONDS=60  # 1 call per minute
```

### Base URL
```bash
BASE_URL="http://localhost:11000/api"  # Default
```

### Timeout
```bash
TIMEOUT=30  # Seconds
```

---

## 📊 Output & Logging

### Console Output
```
[2026-01-17 14:30:45] [INFO] Test started...
[2026-01-17 14:30:46] [SUCCESS] ✓ API is reachable
[2026-01-17 14:30:47] [SUCCESS] ✓ JWT token obtained
[2026-01-17 14:31:06] [SUCCESS] ✓ Health check passed
[2026-01-17 14:31:27] [SUCCESS] ✓ Semantic search returned 2 results
...
```

### Log File
Tests are logged to timestamped file:
```
search_test_results_20260117_143045.log
```

### Response Files
Each search response saved to:
```
semantic_search_response_1705499426.json
keyword_search_response_1705499446.json
...
```

---

## 🚀 Production Checklist

✅ Rate limiting configured (3 calls/min)  
✅ Error handling implemented  
✅ Timeout configured (30 seconds)  
✅ JWT authentication  
✅ Response validation  
✅ HTTP status checking  
✅ Logging to file  
✅ Color-coded output  
✅ All search types tested  
✅ Multiple scenarios covered  

---

## 🔍 Threshold Guide

For semantic search, adjust threshold to control result strictness:

| Threshold | Interpretation | Use Case |
|-----------|-----------------|----------|
| 0.1 | Very loose | Exploratory search, brainstorming |
| 0.2 | Loose (default) | General search, balanced recall |
| 0.3 | Balanced | Recommended for most cases |
| 0.5 | Strict | When you need relevant results only |
| 0.7 | Very strict | Exact or near-exact matches only |

---

## 🛠️ Troubleshooting

### Connection Refused
```bash
# Check if API is running
netstat -an | grep 11000

# Or check with curl
curl -I http://localhost:11000/api/health/
```

### Authentication Failed
- Verify email/password are correct
- Check user exists in database
- Ensure JWT token is not expired

### No Results
- Lower the threshold value
- Check if documents are indexed
- Verify you have permission for the tenant

### Timeout
- Increase `TIMEOUT` variable
- Check server load
- Verify network connectivity

---

## 📚 Files Included

1. **test_search_endpoints.sh** (Main)
   - Automated test suite
   - All 8 comprehensive tests
   - Rate limiting built-in
   - Production-grade error handling

2. **CURL_ENDPOINTS_REFERENCE.sh** (Reference)
   - Manual curl commands
   - Endpoint documentation
   - Query parameter reference
   - Response examples
   - Troubleshooting guide

3. **SEARCH_ENDPOINTS_README.md** (This File)
   - Quick start guide
   - Configuration options
   - Usage examples
   - Troubleshooting

---

## 📞 Support

### Script Features
- ✅ Automatic authentication
- ✅ Rate limiting (3 calls/min)
- ✅ Response validation
- ✅ HTTP status checking
- ✅ Error handling
- ✅ Logging to file
- ✅ Color-coded output
- ✅ Production-ready code

### All Endpoints Tested
- ✅ Semantic search
- ✅ Keyword search
- ✅ Clause search
- ✅ Hybrid search
- ✅ Advanced search
- ✅ Health check
- ✅ Authentication

---

## 🎯 Example Workflow

### 1. Prepare Environment
```bash
cd /Users/vishaljha/CLM_Backend
export TEST_EMAIL="admin@example.com"
export TEST_PASSWORD="admin123"
```

### 2. Run Tests
```bash
./test_search_endpoints.sh
```

### 3. Review Results
```bash
# Check console output
# Review log file: search_test_results_*.log
# Check response files: *_response_*.json
```

### 4. Verify Results
```bash
# Check similarities are meaningful (> 0.2)
# Verify all search types returned results
# Ensure no authentication errors
# Confirm rate limiting worked
```

---

**Status**: ✅ Production-Ready  
**Rate Limit**: 3 calls/minute (20-second intervals)  
**Port**: 11000  
**Last Updated**: January 17, 2026
