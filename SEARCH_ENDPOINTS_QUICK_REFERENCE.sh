#!/bin/bash

################################################################################
# PRODUCTION-LEVEL CURL ENDPOINTS QUICK REFERENCE CARD
# Port: 11000 | Rate Limit: 3 calls/minute
################################################################################

# ============================================================================
# QUICK START - ONE COMMAND
# ============================================================================

# Run entire test suite with auto-authentication:
./test_search_endpoints.sh

# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================

# 1. Navigate to project directory:
cd /Users/vishaljha/CLM_Backend

# 2. Make scripts executable:
chmod +x test_search_endpoints.sh

# 3. Run with options:

# Option A: Auto-authenticate
./test_search_endpoints.sh

# Option B: With JWT token
export JWT_TOKEN="your-token-here"
./test_search_endpoints.sh

# Option C: With credentials
export TEST_EMAIL="admin@example.com"
export TEST_PASSWORD="admin123"
./test_search_endpoints.sh

# ============================================================================
# INDIVIDUAL ENDPOINT TESTS (COPY & PASTE)
# ============================================================================

# Get JWT Token
TOKEN=$(curl -s -X POST "http://localhost:11000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | jq -r '.access')

export JWT_TOKEN=$TOKEN

# ────────────────────────────────────────────────────────────────────────────
# 1. SEMANTIC SEARCH (Standard - Balanced Threshold)
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/search/semantic/?q=confidentiality&threshold=0.2&top_k=10" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" | jq '.'

# Sleep to respect rate limiting
sleep 20

# ────────────────────────────────────────────────────────────────────────────
# 2. KEYWORD SEARCH
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/search/keyword/?q=payment&top_k=10" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" | jq '.'

sleep 20

# ────────────────────────────────────────────────────────────────────────────
# 3. CLAUSE SEARCH
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/search/clause/?q=termination&top_k=10" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" | jq '.'

sleep 20

# ────────────────────────────────────────────────────────────────────────────
# 4. HYBRID SEARCH (Semantic + Keyword)
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/search/hybrid/?q=data+protection&threshold=0.3&top_k=10" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" | jq '.'

sleep 20

# ────────────────────────────────────────────────────────────────────────────
# 5. SEMANTIC SEARCH - STRICT (High Threshold)
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/search/semantic/?q=confidentiality&threshold=0.7&top_k=5" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" | jq '.'

sleep 20

# ────────────────────────────────────────────────────────────────────────────
# 6. SEMANTIC SEARCH - LOOSE (Low Threshold)
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/search/semantic/?q=breach&threshold=0.1&top_k=10" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" | jq '.'

sleep 20

# ────────────────────────────────────────────────────────────────────────────
# 7. ADVANCED SEARCH (with filters)
# ────────────────────────────────────────────────────────────────────────────
curl -X POST "http://localhost:11000/api/search/advanced/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "liability",
    "filters": {"document_type": "agreement"},
    "top_k": 10
  }' | jq '.'

sleep 20

# ────────────────────────────────────────────────────────────────────────────
# 8. HEALTH CHECK
# ────────────────────────────────────────────────────────────────────────────
curl -X GET "http://localhost:11000/api/health/" | jq '.'

# ============================================================================
# QUERY PARAMETER REFERENCE
# ============================================================================

# SEMANTIC SEARCH:
#   q=<query>              - Search query (REQUIRED)
#   threshold=<0.0-1.0>    - Min similarity (optional, default: 0.2)
#   top_k=<number>         - Max results (optional, default: 10)

# KEYWORD SEARCH:
#   q=<query>              - Search query (REQUIRED)
#   top_k=<number>         - Max results (optional, default: 10)

# CLAUSE SEARCH:
#   q=<query>              - Search query (REQUIRED)
#   top_k=<number>         - Max results (optional, default: 10)

# HYBRID SEARCH:
#   q=<query>              - Search query (REQUIRED)
#   threshold=<0.0-1.0>    - Min semantic similarity (optional, default: 0.3)
#   top_k=<number>         - Max results (optional, default: 10)

# ADVANCED SEARCH (POST body):
#   query=<query>          - Search query (REQUIRED)
#   filters=<object>       - Filter criteria (optional)
#   top_k=<number>         - Max results (optional, default: 10)

# ============================================================================
# THRESHOLD VALUES FOR SEMANTIC SEARCH
# ============================================================================

# threshold=0.1  → Very loose (includes loosely related)
# threshold=0.2  → Loose (DEFAULT - balanced)
# threshold=0.3  → Balanced (recommended)
# threshold=0.5  → Strict (only relevant)
# threshold=0.7  → Very strict (exact/near-exact)

# ============================================================================
# RATE LIMITING COMPLIANCE
# ============================================================================

# Current rate limit: 3 calls per minute
# Sleep interval: 20 seconds between calls
#
# To add rate limiting to any curl command:
#
#   curl <command> && sleep 20
#
# The test_search_endpoints.sh script includes automatic rate limiting!

# ============================================================================
# RESPONSE VALIDATION
# ============================================================================

# Check if response is valid (use jq):
curl -s "..." | jq '.success'        # Should return: true
curl -s "..." | jq '.count'          # Shows number of results
curl -s "..." | jq '.results | length' # Length of results array

# Example: Check if search returned results
RESULT_COUNT=$(curl -s "..." | jq '.count')
if [ "$RESULT_COUNT" -gt 0 ]; then
    echo "✓ Search returned $RESULT_COUNT results"
else
    echo "✗ No results found"
fi

# ============================================================================
# TROUBLESHOOTING ONE-LINERS
# ============================================================================

# Check if server is running:
curl -I http://localhost:11000/api/health/

# Check API connectivity:
curl -s http://localhost:11000/api/health/ | jq '.'

# Get JWT token:
curl -s -X POST "http://localhost:11000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | jq '.access'

# List response fields:
curl -s "..." | jq 'keys'

# Pretty print JSON:
curl -s "..." | jq '.'

# Extract just count:
curl -s "..." | jq '.count'

# Extract all similarity scores:
curl -s "..." | jq '.results[].similarity'

# Count results:
curl -s "..." | jq '.results | length'

# ============================================================================
# USEFUL CURL OPTIONS
# ============================================================================

# -i          Include response headers
# -I          Headers only (no body)
# -v          Verbose mode (shows full request/response)
# -X METHOD   Specify HTTP method (GET, POST, etc.)
# -H "Header" Add custom header
# -d '...'    Send JSON data (POST)
# -w "%{http_code}" Get HTTP status code
# -s          Silent mode (no progress)
# --max-time N Set timeout in seconds
# | jq '.'    Pretty print JSON

# ============================================================================
# EXAMPLE WORKFLOWS
# ============================================================================

# WORKFLOW 1: Quick test of all endpoints
echo "Testing all search endpoints..."
./test_search_endpoints.sh

# WORKFLOW 2: Test with specific token
export JWT_TOKEN="your-token"
./test_search_endpoints.sh

# WORKFLOW 3: Manual testing with rate limiting
TOKEN=$(curl -s ... | jq -r '.access')
export JWT_TOKEN=$TOKEN

curl -s "...semantic..." | jq '.' && sleep 20
curl -s "...keyword..." | jq '.' && sleep 20
curl -s "...clause..." | jq '.' && sleep 20
curl -s "...hybrid..." | jq '.'

# WORKFLOW 4: Performance testing
time curl -s "..." | jq '.results | length'

# ============================================================================
# FILE REFERENCES
# ============================================================================

# test_search_endpoints.sh
#   → Main automated test suite
#   → Includes rate limiting
#   → Auto-authentication
#   → Comprehensive logging

# CURL_ENDPOINTS_REFERENCE.sh
#   → Manual curl command reference
#   → Query parameter guide
#   → Response examples
#   → Troubleshooting tips

# SEARCH_ENDPOINTS_README.md
#   → Quick start guide
#   → Configuration options
#   → Production checklist

# SEARCH_ENDPOINTS_QUICK_REFERENCE.sh
#   → This file
#   → Quick commands
#   → Copy-paste ready

# ============================================================================
# PRODUCTION DEPLOYMENT CHECKLIST
# ============================================================================

# Before going to production:
# ☑ Test all endpoints with expected data
# ☑ Verify rate limiting is working (3 calls/min)
# ☑ Check JWT authentication
# ☑ Validate response formats
# ☑ Monitor performance (30-60ms expected)
# ☑ Test error scenarios
# ☑ Check logs are being written
# ☑ Verify timeout values are appropriate
# ☑ Test with realistic query patterns
# ☑ Monitor server load

# ============================================================================
# QUICK COMMANDS FOR TERMINAL
# ============================================================================

# Test health:
curl http://localhost:11000/api/health/

# Get token:
TOKEN=$(curl -s -X POST "http://localhost:11000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | jq -r '.access')

# Test semantic search:
curl "http://localhost:11000/api/search/semantic/?q=test" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# Save token to file:
echo "$TOKEN" > jwt_token.txt

# Use token from file:
TOKEN=$(cat jwt_token.txt)

# ============================================================================
# ADDITIONAL NOTES
# ============================================================================

# • All scripts are production-ready
# • Rate limiting is automatic (3 calls/min)
# • Responses are logged to timestamped files
# • Error handling is comprehensive
# • Exit codes indicate success/failure
# • Color-coded output for clarity
# • Works on macOS, Linux, and Unix

# ============================================================================
