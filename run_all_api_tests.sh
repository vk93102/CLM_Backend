#!/bin/bash

# ============================================================================
# COMPREHENSIVE API TESTING SCRIPT - All Endpoints Week 1, 2, 3
# ============================================================================
# This script tests ALL endpoints in the AI-powered CLM system
# Run with: ./run_all_api_tests.sh
# ============================================================================

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

BASE_URL="http://13.48.148.79"
TEST_LOG="api_test_results_$(date +%Y%m%d_%H%M%S).txt"

# Counter for test results
TESTS_PASSED=0
TESTS_FAILED=0

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_header() {
  echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║ $1${NC}"
  echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_test() {
  echo -e "${YELLOW}[TEST] $1${NC}"
}

print_success() {
  echo -e "${GREEN}✓ $1${NC}"
  TESTS_PASSED=$((TESTS_PASSED + 1))
}

print_error() {
  echo -e "${RED}✗ $1${NC}"
  TESTS_FAILED=$((TESTS_FAILED + 1))
}

print_info() {
  echo -e "${CYAN}ℹ $1${NC}"
}

log_response() {
  echo "
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$2
" >> "$TEST_LOG"
}

check_health() {
  print_info "Checking server health..."
  HEALTH=$(curl -s -X GET "$BASE_URL/api/health/" 2>/dev/null)
  
  if [ -z "$HEALTH" ]; then
    echo -e "${RED}✗ Server is not running on $BASE_URL${NC}"
    echo -e "${RED}Start server with: python manage.py runserver 4000${NC}"
    exit 1
  fi
  
  print_success "Server is running"
}

# ============================================================================
# START MAIN SCRIPT
# ============================================================================

clear

print_header "🚀 AI-POWERED CLM - COMPREHENSIVE API TEST SUITE"

# Check server health
check_health

# Initialize test log
echo "API Test Results - $(date)" > "$TEST_LOG"
echo "Base URL: $BASE_URL" >> "$TEST_LOG"
echo "" >> "$TEST_LOG"

# ============================================================================
# WEEK 1: CORE AUTHENTICATION & CONTRACT MANAGEMENT
# ============================================================================

print_header "WEEK 1: Authentication & Contract Management"

# TEST 1: Login
print_test "1. Authentication - Login (POST /api/auth/login/)"
echo ""
echo "Sending login request..."

AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }')

echo "Response:"
echo "$AUTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$AUTH_RESPONSE"

TOKEN=$(echo "$AUTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))" 2>/dev/null)

if [ ! -z "$TOKEN" ] && [ ${#TOKEN} -gt 50 ]; then
  print_success "Authentication successful"
  print_info "Token: ${TOKEN:0:50}..."
  log_response "TEST 1: Login" "$AUTH_RESPONSE"
else
  print_error "Authentication failed - No valid token returned"
  log_response "TEST 1: Login (FAILED)" "$AUTH_RESPONSE"
  exit 1
fi

echo ""
sleep 2

# TEST 2: List Contracts
print_test "2. Contract Management - List Contracts (GET /api/contracts/)"
echo ""

CONTRACTS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/contracts/?page=1&page_size=5" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "Response:"
echo "$CONTRACTS_RESPONSE" | python3 -m json.tool 2>/dev/null | head -40

CONTRACT_COUNT=$(echo "$CONTRACTS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)

if [ "$CONTRACT_COUNT" -gt 0 ]; then
  print_success "Retrieved $CONTRACT_COUNT contracts"
  log_response "TEST 2: List Contracts" "$CONTRACTS_RESPONSE"
else
  print_error "No contracts found or invalid response"
  log_response "TEST 2: List Contracts (FAILED)" "$CONTRACTS_RESPONSE"
fi

# Extract first contract ID
CONTRACT_ID=$(echo "$CONTRACTS_RESPONSE" | python3 -c "import sys, json; results = json.load(sys.stdin).get('results', []); print(results[0]['id'] if results else '')" 2>/dev/null)

if [ ! -z "$CONTRACT_ID" ]; then
  print_info "Using contract ID: $CONTRACT_ID"
else
  print_error "Could not extract contract ID"
  exit 1
fi

echo ""
sleep 2

# TEST 3: Get Contract Details
print_test "3. Contract Management - Get Contract Details (GET /api/contracts/{id}/)"
echo ""

CONTRACT_DETAIL=$(curl -s -X GET "$BASE_URL/api/contracts/$CONTRACT_ID/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "Response (without content field):"
echo "$CONTRACT_DETAIL" | python3 -c "import sys, json; d = json.load(sys.stdin); d.pop('content', ''); print(json.dumps(d, indent=2))" 2>/dev/null | head -40

CONTRACT_TITLE=$(echo "$CONTRACT_DETAIL" | python3 -c "import sys, json; print(json.load(sys.stdin).get('title', ''))" 2>/dev/null)

if [ ! -z "$CONTRACT_TITLE" ]; then
  print_success "Retrieved contract: $CONTRACT_TITLE"
  log_response "TEST 3: Get Contract Details" "$CONTRACT_DETAIL"
else
  print_error "Could not retrieve contract details"
  log_response "TEST 3: Get Contract Details (FAILED)" "$CONTRACT_DETAIL"
fi

echo ""
sleep 2

# ============================================================================
# WEEK 2: AI FEATURES & ADVANCED SEARCH
# ============================================================================

print_header "WEEK 2: AI Features & Advanced Search"

# TEST 4: Hybrid Search
print_test "4. AI Search - Hybrid Search (POST /api/search/global/)"
echo ""

SEARCH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/search/global/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "software development",
    "mode": "hybrid",
    "limit": 5
  }')

echo "Response:"
echo "$SEARCH_RESPONSE" | python3 -m json.tool 2>/dev/null | head -50

SEARCH_RESULTS=$(echo "$SEARCH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('results', []))" 2>/dev/null)
SEARCH_COUNT=$(echo "$SEARCH_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('results', [])))" 2>/dev/null)

if [ "$SEARCH_COUNT" -gt 0 ]; then
  print_success "Hybrid search returned $SEARCH_COUNT results"
  log_response "TEST 4: Hybrid Search" "$SEARCH_RESPONSE"
else
  print_error "No search results returned"
  log_response "TEST 4: Hybrid Search (FAILED)" "$SEARCH_RESPONSE"
fi

echo ""
sleep 2

# TEST 5: Autocomplete
print_test "5. AI Search - Autocomplete (GET /api/search/suggestions/)"
echo ""

AUTOCOMPLETE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/search/suggestions/?q=soft&limit=3" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "Response:"
echo "$AUTOCOMPLETE_RESPONSE" | python3 -m json.tool 2>/dev/null

SUGGESTIONS_COUNT=$(echo "$AUTOCOMPLETE_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('suggestions', [])))" 2>/dev/null)

if [ "$SUGGESTIONS_COUNT" -gt 0 ]; then
  print_success "Autocomplete returned $SUGGESTIONS_COUNT suggestions"
  log_response "TEST 5: Autocomplete" "$AUTOCOMPLETE_RESPONSE"
else
  print_error "No autocomplete suggestions"
  log_response "TEST 5: Autocomplete (FAILED)" "$AUTOCOMPLETE_RESPONSE"
fi

echo ""
sleep 2

# TEST 6: Clause Summary
print_test "6. AI Analysis - Clause Summary (POST /api/analysis/clause-summary/)"
echo ""

CLAUSE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/analysis/clause-summary/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clause_text": "The Disclosing Party shall not be liable for any indirect, incidental, special, consequential or punitive damages, or any loss of profits or revenues, whether incurred directly or indirectly."
  }')

echo "Response:"
echo "$CLAUSE_RESPONSE" | python3 -m json.tool 2>/dev/null

SUMMARY=$(echo "$CLAUSE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('plain_summary', ''))" 2>/dev/null)

if [ ! -z "$SUMMARY" ] && [ ${#SUMMARY} -gt 20 ]; then
  print_success "Clause summary generated (${#SUMMARY} chars)"
  print_info "Summary: ${SUMMARY:0:100}..."
  log_response "TEST 6: Clause Summary" "$CLAUSE_RESPONSE"
else
  print_error "Could not generate clause summary"
  log_response "TEST 6: Clause Summary (FAILED)" "$CLAUSE_RESPONSE"
fi

echo ""
sleep 2

# TEST 7: Related Contracts
print_test "7. AI Search - Related Contracts (GET /api/contracts/{id}/related/)"
echo ""

RELATED_RESPONSE=$(curl -s -X GET "$BASE_URL/api/contracts/$CONTRACT_ID/related/?limit=5" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "Response:"
echo "$RELATED_RESPONSE" | python3 -m json.tool 2>/dev/null | head -50

RELATED_COUNT=$(echo "$RELATED_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('related_contracts', [])))" 2>/dev/null)

if [ "$RELATED_COUNT" -gt 0 ]; then
  print_success "Found $RELATED_COUNT related contracts"
  log_response "TEST 7: Related Contracts" "$RELATED_RESPONSE"
else
  print_error "No related contracts found"
  log_response "TEST 7: Related Contracts (FAILED)" "$RELATED_RESPONSE"
fi

echo ""
sleep 2

# TEST 8: Contract Comparison
print_test "8. AI Analysis - Contract Comparison (POST /api/analysis/compare/)"
echo ""

# Get second contract for comparison
CONTRACT_ID_2=$(echo "$CONTRACTS_RESPONSE" | python3 -c "import sys, json; results = json.load(sys.stdin).get('results', []); print(results[1]['id'] if len(results) > 1 else results[0]['id'])" 2>/dev/null)

if [ ! -z "$CONTRACT_ID_2" ] && [ "$CONTRACT_ID_2" != "$CONTRACT_ID" ]; then
  COMPARE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/analysis/compare/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"contract_a_id\": \"$CONTRACT_ID\",
      \"contract_b_id\": \"$CONTRACT_ID_2\"
    }")

  echo "Response:"
  echo "$COMPARE_RESPONSE" | python3 -c "import sys, json; d = json.load(sys.stdin); d.pop('raw_analysis', ''); print(json.dumps(d, indent=2))" 2>/dev/null | head -50

  COMPARISON=$(echo "$COMPARE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('summary', ''))" 2>/dev/null)

  if [ ! -z "$COMPARISON" ] && [ ${#COMPARISON} -gt 20 ]; then
    print_success "Contract comparison generated"
    print_info "Comparison: ${COMPARISON:0:100}..."
    log_response "TEST 8: Contract Comparison" "$COMPARE_RESPONSE"
  else
    print_error "Could not generate comparison"
    log_response "TEST 8: Contract Comparison (FAILED)" "$COMPARE_RESPONSE"
  fi
else
  print_error "Not enough contracts for comparison"
fi

echo ""
sleep 2

# ============================================================================
# WEEK 3: ADVANCED FEATURES & BACKGROUND PROCESSING
# ============================================================================

print_header "WEEK 3: Advanced Features & Background Processing"

# TEST 9: Start Contract Generation
print_test "9. Contract Generation - Start Generation (POST /api/generation/start/)"
echo ""

GENERATION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/generation/start/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Technology Services Agreement - API Test",
    "contract_type": "MSA",
    "description": "Master Service Agreement for technology and consulting services",
    "variables": {
      "party_a": "Test Technology Corp",
      "party_b": "Client Services Inc",
      "effective_date": "2024-02-01",
      "term": "12 months",
      "payment_amount": "$100,000",
      "payment_terms": "Net 30"
    }
  }')

echo "Response:"
echo "$GENERATION_RESPONSE" | python3 -m json.tool 2>/dev/null

GENERATION_ID=$(echo "$GENERATION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('contract_id', ''))" 2>/dev/null)
GEN_STATUS=$(echo "$GENERATION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)

if [ ! -z "$GENERATION_ID" ] && [ "$GEN_STATUS" = "processing" ]; then
  print_success "Contract generation started (ID: $GENERATION_ID)"
  log_response "TEST 9: Start Generation" "$GENERATION_RESPONSE"
else
  print_error "Could not start contract generation"
  log_response "TEST 9: Start Generation (FAILED)" "$GENERATION_RESPONSE"
  GENERATION_ID=""
fi

echo ""
sleep 2

# TEST 10: Check Generation Status
if [ ! -z "$GENERATION_ID" ]; then
  print_test "10. Contract Generation - Check Status (GET /api/generation/{id}/status/)"
  echo ""
  print_info "Checking generation status (may take 10-30 seconds)..."
  echo ""

  for i in {1..5}; do
    STATUS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/generation/$GENERATION_ID/status/" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json")

    echo "Status Check $i/5:"
    echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null | head -20

    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)

    if [ "$STATUS" = "completed" ]; then
      print_success "Contract generation completed!"
      GENERATED_TEXT=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('result', {}).get('generated_text', '')[:100])" 2>/dev/null)
      print_info "Generated text preview: ${GENERATED_TEXT}..."
      log_response "TEST 10: Generation Status (Completed)" "$STATUS_RESPONSE"
      break
    elif [ "$STATUS" = "failed" ]; then
      print_error "Contract generation failed"
      log_response "TEST 10: Generation Status (Failed)" "$STATUS_RESPONSE"
      break
    else
      print_info "Still processing ($STATUS)... waiting 5 seconds"
      log_response "TEST 10: Generation Status (Check $i)" "$STATUS_RESPONSE"
      sleep 5
    fi
  done
fi

echo ""
sleep 2

# TEST 11: Email Configuration Test
print_test "11. Email System - SMTP Configuration Test"
echo ""

EMAIL_TEST=$(curl -s -X POST "$BASE_URL/api/email-test/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "admin@example.com",
    "test_type": "smtp_configuration"
  }' 2>/dev/null)

if [ ! -z "$EMAIL_TEST" ]; then
  echo "Response:"
  echo "$EMAIL_TEST" | python3 -m json.tool 2>/dev/null
  
  EMAIL_STATUS=$(echo "$EMAIL_TEST" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)
  
  if [ "$EMAIL_STATUS" = "success" ]; then
    print_success "Email SMTP configuration is working"
    log_response "TEST 11: Email Test" "$EMAIL_TEST"
  else
    print_error "Email SMTP configuration may have issues"
    log_response "TEST 11: Email Test (Warning)" "$EMAIL_TEST"
  fi
else
  print_error "Email test endpoint not available (optional test)"
fi

echo ""

# ============================================================================
# TEST SUMMARY
# ============================================================================

print_header "📊 TEST SUMMARY"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

echo -e "Total Tests Run:    ${CYAN}$TOTAL_TESTS${NC}"
echo -e "Tests Passed:       ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed:       ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
  echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
  echo -e "${GREEN}✓ System is working correctly with REAL data${NC}"
  echo -e "${GREEN}✓ All endpoints returning proper responses${NC}"
else
  echo -e "${RED}✗ Some tests failed${NC}"
  echo -e "${RED}✗ Check the log file for details${NC}"
fi

echo ""
echo -e "${BLUE}Test log saved to: ${CYAN}$TEST_LOG${NC}"
echo ""

# ============================================================================
# ENDPOINT SUMMARY
# ============================================================================

print_header "✅ ENDPOINTS TESTED"

echo "WEEK 1 - Authentication & Management:"
echo "  ✓ POST   /api/auth/login/"
echo "  ✓ GET    /api/contracts/"
echo "  ✓ GET    /api/contracts/{id}/"
echo ""
echo "WEEK 2 - AI Features & Search:"
echo "  ✓ POST   /api/search/global/"
echo "  ✓ GET    /api/search/suggestions/"
echo "  ✓ POST   /api/analysis/clause-summary/"
echo "  ✓ GET    /api/contracts/{id}/related/"
echo "  ✓ POST   /api/analysis/compare/"
echo ""
echo "WEEK 3 - Advanced Features:"
echo "  ✓ POST   /api/generation/start/"
echo "  ✓ GET    /api/generation/{id}/status/"
echo "  ✓ POST   /api/email-test/"
echo ""

echo -e "${BLUE}For detailed results, see: ${CYAN}$TEST_LOG${NC}"
echo ""
