#!/bin/bash

################################################################################
# CURL TEST CONFIGURATION & REFERENCE
# For Production-Level Semantic Search Endpoints Testing
# Port: 11000 | Rate Limit: 3 calls/min
################################################################################

# ============================================================================
# QUICK START
# ============================================================================

# 1. Basic usage with auto-authentication:
#    ./test_search_endpoints.sh

# 2. With pre-configured JWT token:
#    export JWT_TOKEN="your-jwt-token-here"
#    ./test_search_endpoints.sh

# 3. With custom email/password:
#    export TEST_EMAIL="admin@example.com"
#    export TEST_PASSWORD="admin123"
#    ./test_search_endpoints.sh

# ============================================================================
# INDIVIDUAL ENDPOINT TESTS (MANUAL)
# ============================================================================

# To test individual endpoints manually:

# 1. SEMANTIC SEARCH
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/search/semantic/?q=confidentiality&threshold=0.2&top_k=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  --max-time 30

# 2. KEYWORD SEARCH
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/search/keyword/?q=payment&top_k=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  --max-time 30

# 3. CLAUSE SEARCH
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/search/clause/?q=termination&top_k=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  --max-time 30

# 4. HYBRID SEARCH (Semantic + Keyword)
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/search/hybrid/?q=data+protection&threshold=0.3&top_k=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  --max-time 30

# 5. ADVANCED SEARCH (with filters)
# ────────────────────────────────────────────────────────────────────────────
curl -X POST "http://localhost:11000/api/search/advanced/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "liability",
    "filters": {"document_type": "agreement"},
    "top_k": 10
  }' \
  --max-time 30

# 6. SEMANTIC SEARCH WITH STRICT THRESHOLD
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/search/semantic/?q=confidentiality&threshold=0.7&top_k=5" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  --max-time 30

# 7. SEMANTIC SEARCH WITH LOOSE THRESHOLD
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/search/semantic/?q=breach&threshold=0.1&top_k=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  --max-time 30

# ============================================================================
# AUTHENTICATION - GET JWT TOKEN
# ============================================================================

curl -X POST "http://localhost:11000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }' \
  --max-time 30 | jq '.access'  # Extract token

# ============================================================================
# HEALTH CHECK
# ============================================================================

curl -X GET "http://localhost:11000/api/health/" \
  --max-time 30 | jq '.'

# ============================================================================
# QUERY PARAMETERS REFERENCE
# ============================================================================

# SEMANTIC SEARCH PARAMETERS:
#   q          (required) - Search query (string)
#   threshold  (optional) - Min similarity (0-1, default: 0.2)
#   top_k      (optional) - Max results (integer, default: 10)

# KEYWORD SEARCH PARAMETERS:
#   q          (required) - Search query (string)
#   top_k      (optional) - Max results (integer, default: 10)

# CLAUSE SEARCH PARAMETERS:
#   q          (required) - Search query (string)
#   top_k      (optional) - Max results (integer, default: 10)

# HYBRID SEARCH PARAMETERS:
#   q          (required) - Search query (string)
#   threshold  (optional) - Min semantic similarity (0-1, default: 0.3)
#   top_k      (optional) - Max results (integer, default: 10)

# ADVANCED SEARCH PARAMETERS (POST body):
#   query      (required) - Search query (string)
#   filters    (optional) - Filter criteria (object)
#   top_k      (optional) - Max results (integer, default: 10)

# ============================================================================
# THRESHOLD GUIDE FOR SEMANTIC SEARCH
# ============================================================================

# threshold=0.1  - Very loose (includes loosely related)
# threshold=0.2  - Loose (default, balanced recall)
# threshold=0.3  - Balanced (good for general search)
# threshold=0.5  - Strict (only relevant results)
# threshold=0.7  - Very strict (only exact/near-exact)

# ============================================================================
# RESPONSE FORMAT EXAMPLES
# ============================================================================

# SUCCESS RESPONSE (200 OK):
# {
#   "success": true,
#   "count": 2,
#   "search_type": "semantic",
#   "query": "confidentiality",
#   "threshold": 0.2,
#   "results": [
#     {
#       "chunk_id": "uuid",
#       "document_id": "uuid",
#       "text": "Confidentiality obligations...",
#       "similarity": 0.9518,
#       "similarity_percentage": "95.18%",
#       "filename": "agreement.pdf",
#       "document_title": "Master Service Agreement"
#     }
#   ]
# }

# ERROR RESPONSE (400 Bad Request):
# {
#   "success": false,
#   "error": "Query parameter 'q' is required",
#   "code": "MISSING_QUERY"
# }

# AUTHENTICATION ERROR (401 Unauthorized):
# {
#   "detail": "Authentication credentials were not provided."
# }

# ============================================================================
# RATE LIMITING CONFIGURATION
# ============================================================================

# Current settings: 3 calls per minute
# Sleep interval between calls: 20 seconds
# To change rate limit, edit RATE_LIMIT_SECONDS variable in test_search_endpoints.sh

# Calculation: 60 seconds / desired_calls_per_minute = sleep_interval_seconds
# Examples:
#   1 call/min   → sleep 60 seconds
#   2 calls/min  → sleep 30 seconds
#   3 calls/min  → sleep 20 seconds (current)
#   5 calls/min  → sleep 12 seconds
#   10 calls/min → sleep 6 seconds

# ============================================================================
# USEFUL CURL OPTIONS
# ============================================================================

# --max-time 30           - Timeout after 30 seconds
# -w "\n%{http_code}"     - Show HTTP status code
# -i                      - Include response headers
# -I                      - Headers only
# -v                      - Verbose (show request/response)
# -X GET/POST/PUT/DELETE  - HTTP method
# -H "Header: value"      - Add header
# -d '{"json":"data"}'    - JSON request body
# --data-raw '...'        - Raw data without JSON parsing

# ============================================================================
# TESTING SCENARIOS
# ============================================================================

# SCENARIO 1: Basic Search Flow
# 1. Get JWT token
# 2. Perform semantic search for "confidentiality"
# 3. Review results and similarity scores
# 4. Check response time

# SCENARIO 2: Threshold Testing
# Test same query with different thresholds:
#   threshold=0.1  (loose)
#   threshold=0.3  (balanced)
#   threshold=0.7  (strict)
# Compare result count and quality

# SCENARIO 3: Multiple Search Types
# Test all search types for same query:
#   semantic search
#   keyword search
#   clause search
#   hybrid search
# Compare results from each method

# SCENARIO 4: Edge Cases
# Test with:
#   Empty query
#   Special characters
#   Very long query
#   Non-existent keyword
#   Multiple keywords

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

# CONNECTION REFUSED:
#   - Check if API is running on port 11000
#   - Command: netstat -an | grep 11000

# AUTHENTICATION FAILED:
#   - Verify email and password are correct
#   - Ensure user exists in database
#   - Check token is not expired

# NO RESULTS:
#   - Lower the threshold value
#   - Check if documents are indexed
#   - Verify tenant_id permissions

# TIMEOUT:
#   - Increase --max-time value
#   - Check server load
#   - Verify network connectivity

# ============================================================================
# PRODUCTION BEST PRACTICES
# ============================================================================

# 1. Always use HTTPS in production (update http:// to https://)
# 2. Store JWT tokens securely (use environment variables)
# 3. Implement proper error handling and retry logic
# 4. Monitor API response times and errors
# 5. Log all requests for audit trails
# 6. Rate limit to avoid overwhelming the server
# 7. Use meaningful variable names and comments
# 8. Validate responses before processing
# 9. Set appropriate timeout values
# 10. Test with realistic query patterns

# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

# To monitor response times:
curl -w "@response_time.txt" "http://localhost:11000/api/search/semantic/?q=test"

# Create response_time.txt with:
# time_namelookup: %{time_namelookup}\n
# time_connect:    %{time_connect}\n
# time_appconnect: %{time_appconnect}\n
# time_pretransfer:%{time_pretransfer}\n
# time_redirect:   %{time_redirect}\n
# time_starttransfer: %{time_starttransfer}\n
# time_total:      %{time_total}\n

# ============================================================================
