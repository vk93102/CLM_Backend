#!/bin/bash

# Production endpoint testing script on port 11000
# Tests all contract management endpoints

BASE_URL="http://0.0.0.0:11000"
API_V1="$BASE_URL/api/v1"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0
TOTAL=0

# Helper function to test endpoints
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_code=$4
    local description=$5
    
    TOTAL=$((TOTAL + 1))
    echo -e "\n${YELLOW}Testing: $description${NC}"
    echo "Method: $method | Endpoint: $endpoint"
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            "$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$endpoint")
    fi
    
    # Extract status code (last line)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [[ "$http_code" =~ $expected_code ]]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAILED${NC} (Expected $expected_code, got $http_code)"
        echo "Response: $body"
        FAILED=$((FAILED + 1))
    fi
}

echo "=========================================="
echo "CLM Backend - Production Endpoint Tests"
echo "Testing on: $BASE_URL"
echo "=========================================="

# Test 1: Health Check
echo -e "\n${YELLOW}1. HEALTH CHECK ENDPOINTS${NC}"
test_endpoint "GET" "$API_V1/health/" "" "200" "Health check endpoint"

# Test 2: Contract List (requires auth - this should return 401)
echo -e "\n${YELLOW}2. BASIC CONTRACT ENDPOINTS${NC}"
test_endpoint "GET" "$API_V1/contracts/" "" "401" "Get contracts list (unauthorized)"

# Test 3: Upload Document (requires auth)
echo -e "\n${YELLOW}3. R2 DOCUMENT UPLOAD ENDPOINTS${NC}"
test_endpoint "POST" "$API_V1/upload-document/" "" "401" "Upload document (unauthorized)"

# Test 4: Contract Template List (requires auth)
echo -e "\n${YELLOW}4. CONTRACT TEMPLATE ENDPOINTS${NC}"
test_endpoint "GET" "$API_V1/contract-templates/" "" "401" "Get templates list (unauthorized)"

# Test 5: Clauses List (requires auth)
echo -e "\n${YELLOW}5. CLAUSE MANAGEMENT ENDPOINTS${NC}"
test_endpoint "GET" "$API_V1/clauses/" "" "401" "Get clauses list (unauthorized)"

# Test 6: Generation Jobs (requires auth)
echo -e "\n${YELLOW}6. CONTRACT GENERATION ENDPOINTS${NC}"
test_endpoint "GET" "$API_V1/generation-jobs/" "" "401" "Get generation jobs (unauthorized)"

# Test 7: E-Signature Endpoints (requires auth)
echo -e "\n${YELLOW}7. E-SIGNATURE ENDPOINTS${NC}"
test_endpoint "POST" "$API_V1/esign/send/" "" "401" "Send for e-signature (unauthorized)"
test_endpoint "GET" "$API_V1/esign/status/test-id/" "" "401" "Check e-signature status (unauthorized)"

# Test 8: 404 Error Handling
echo -e "\n${YELLOW}8. ERROR HANDLING${NC}"
test_endpoint "GET" "$API_V1/nonexistent/" "" "404" "Nonexistent endpoint (404)"

echo -e "\n=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "Total Tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
    exit 1
fi
