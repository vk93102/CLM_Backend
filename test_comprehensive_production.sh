#!/bin/bash

# Production Test Suite with Authentication
# Tests all contract management endpoints with proper token handling

BASE_URL="http://localhost:11000"
API_V1="$BASE_URL/api/v1"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
TOTAL=0

# Test Authentication
test_auth() {
    echo -e "${BLUE}Attempting to authenticate...${NC}"
    
    # Get or create test user token
    TOKEN=$(curl -s -X POST "$BASE_URL/api/v1/token/" \
        -H "Content-Type: application/json" \
        -d '{
            "username": "admin",
            "password": "admin123"
        }' | grep -o '"access":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$TOKEN" ]; then
        echo -e "${YELLOW}Warning: Could not obtain auth token. Testing public endpoints only.${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ Authentication successful${NC}"
    echo "Token: ${TOKEN:0:20}..."
    return 0
}

# Test endpoint with proper handling
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_codes=$4
    local description=$5
    local with_auth=$6
    
    TOTAL=$((TOTAL + 1))
    echo -e "\n${YELLOW}[$TOTAL] Testing: $description${NC}"
    echo "  Endpoint: $method $endpoint"
    
    # Build curl command
    local cmd="curl -s -w '\n%{http_code}' -X $method"
    cmd="$cmd -H 'Content-Type: application/json'"
    
    if [ "$with_auth" = "true" ] && [ ! -z "$TOKEN" ]; then
        cmd="$cmd -H 'Authorization: Bearer $TOKEN'"
    fi
    
    if [ ! -z "$data" ]; then
        cmd="$cmd -d '$data'"
    fi
    
    cmd="$cmd '$endpoint'"
    
    # Execute
    response=$(eval $cmd)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Check if status code is expected
    if echo "$expected_codes" | grep -q "$http_code"; then
        echo -e "  ${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
        
        # Show partial response for successful calls
        if [ ! -z "$body" ] && [ "$http_code" != "204" ]; then
            echo "  Response: $(echo $body | head -c 100)..."
        fi
    else
        echo -e "  ${RED}✗ FAILED${NC} (Expected $expected_codes, got $http_code)"
        FAILED=$((FAILED + 1))
        if [ ! -z "$body" ]; then
            echo "  Error: $(echo $body | head -c 200)..."
        fi
    fi
}

# Main test execution
echo "=========================================="
echo "CLM Backend - Production Test Suite"
echo "Port: 11000"
echo "Date: $(date)"
echo "=========================================="

# 1. Health Check - Should work without auth
echo -e "\n${BLUE}=== SECTION 1: HEALTH CHECK ===${NC}"
test_endpoint "GET" "$API_V1/health/" "" "200" "Health check" "false"

# 2. Authentication
echo -e "\n${BLUE}=== SECTION 2: AUTHENTICATION ===${NC}"
test_auth
HAS_TOKEN=$?

# 3. Basic Contract Endpoints
if [ $HAS_TOKEN -eq 0 ]; then
    echo -e "\n${BLUE}=== SECTION 3: CONTRACT MANAGEMENT ===${NC}"
    test_endpoint "GET" "$API_V1/contracts/" "" "200" "List all contracts" "true"
    test_endpoint "GET" "$API_V1/contracts/?status=draft" "" "200" "Filter contracts by status" "true"
    test_endpoint "GET" "$API_V1/contracts/?page=1" "" "200" "Paginated contracts" "true"
    
    # 4. Contract Templates
    echo -e "\n${BLUE}=== SECTION 4: CONTRACT TEMPLATES ===${NC}"
    test_endpoint "GET" "$API_V1/contract-templates/" "" "200" "List templates" "true"
    test_endpoint "POST" "$API_V1/contract-templates/" \
        '{"name":"Test Template","contract_type":"NDA","status":"draft"}' \
        "201" "Create new template" "true"
    
    # 5. Clauses
    echo -e "\n${BLUE}=== SECTION 5: CLAUSE MANAGEMENT ===${NC}"
    test_endpoint "GET" "$API_V1/clauses/" "" "200" "List all clauses" "true"
    test_endpoint "POST" "$API_V1/clauses/" \
        '{"clause_id":"TEST-001","name":"Test Clause","content":"Test content"}' \
        "201" "Create new clause" "true"
    
    # 6. R2 Upload Endpoints
    echo -e "\n${BLUE}=== SECTION 6: DOCUMENT UPLOAD (R2) ===${NC}"
    test_endpoint "GET" "$API_V1/upload-document/" "" "405" "Upload endpoint (POST required)" "true"
    
    # 7. E-Signature Endpoints
    echo -e "\n${BLUE}=== SECTION 7: E-SIGNATURE WORKFLOWS ===${NC}"
    test_endpoint "POST" "$API_V1/esign/send/" \
        '{"contract_id":"test-uuid"}' \
        "400" "Send for signature (validation)" "true"
    test_endpoint "GET" "$API_V1/esign/status/nonexistent/" "" "404" "Check signature status" "true"
    
    # 8. Generation Jobs
    echo -e "\n${BLUE}=== SECTION 8: CONTRACT GENERATION ===${NC}"
    test_endpoint "GET" "$API_V1/generation-jobs/" "" "200" "List generation jobs" "true"
    
else
    echo -e "\n${YELLOW}Skipping authenticated endpoints (no valid token)${NC}"
    echo -e "${YELLOW}To test authenticated endpoints, ensure admin user exists${NC}"
fi

# Test public endpoints that should work
echo -e "\n${BLUE}=== SECTION 9: PUBLIC/UNAUTHORIZED ENDPOINTS ===${NC}"
test_endpoint "GET" "$API_V1/contracts/" "" "401" "Contracts without auth" "false"
test_endpoint "GET" "$API_V1/contract-templates/" "" "401" "Templates without auth" "false"

# Error Handling
echo -e "\n${BLUE}=== SECTION 10: ERROR HANDLING ===${NC}"
test_endpoint "GET" "$API_V1/nonexistent/" "" "404" "Nonexistent endpoint" "false"
test_endpoint "POST" "$API_V1/contracts/" '{"invalid":"data"}' "400|401" "Invalid request data" "false"

# Summary
echo -e "\n=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "Total Tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
SUCCESS_RATE=$((PASSED * 100 / TOTAL))
echo -e "Success Rate: $SUCCESS_RATE%"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
    exit 1
fi
