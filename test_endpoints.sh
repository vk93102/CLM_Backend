#!/bin/bash

##############################################################################
# CLM Backend - Comprehensive API Testing Script
# Tests all endpoints locally on http://localhost:8888
# Usage: bash test_endpoints.sh
##############################################################################

# Configuration
BASE_URL="http://localhost:8888/api"
TIMESTAMP=$(date +%s)
TEST_EMAIL="test_${TIMESTAMP}@example.com"
TEST_PASSWORD="TestPass123!"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

##############################################################################
# Helper Functions
##############################################################################

print_header() {
    echo -e "\n${YELLOW}========================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}========================================${NC}\n"
}

test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local headers=$4
    local test_name=$5
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ -z "$headers" ]; then
        headers="Content-Type: application/json"
    fi
    
    echo -n "[$TOTAL_TESTS] Testing $test_name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" \
            -H "$headers")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "$headers" \
            -d "$data")
    elif [ "$method" = "PATCH" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL$endpoint" \
            -H "$headers" \
            -d "$data")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL$endpoint" \
            -H "$headers")
    fi
    
    # Extract status code and body
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Check if response is 2xx or 3xx (success)
    if [[ $status_code =~ ^[23][0-9][0-9]$ ]]; then
        echo -e "${GREEN}✓ PASSED${NC} (Status: $status_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo "$body" | jq . 2>/dev/null || echo "$body"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (Status: $status_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo "Response: $body"
        return 1
    fi
}

extract_json_value() {
    local json=$1
    local key=$2
    echo "$json" | jq -r "$key" 2>/dev/null || echo ""
}

##############################################################################
# Main Test Suite
##############################################################################

print_header "CLM Backend API Test Suite"
echo "Base URL: $BASE_URL"
echo "Test Email: $TEST_EMAIL"
echo "Test Password: $TEST_PASSWORD"
echo ""

# ============================================================================
# SECTION 1: AUTHENTICATION ENDPOINTS
# ============================================================================

print_header "1. AUTHENTICATION ENDPOINTS"

# Test 1.1: Register User
echo "Test 1.1: User Registration"
register_data="{
  \"email\": \"$TEST_EMAIL\",
  \"password\": \"$TEST_PASSWORD\",
  \"first_name\": \"Test\",
  \"last_name\": \"User\"
}"
register_response=$(curl -s -X POST "$BASE_URL/auth/register/" \
    -H "Content-Type: application/json" \
    -d "$register_data")
user_id=$(echo "$register_response" | jq -r '.user_id' 2>/dev/null)
echo "Response: $register_response" | jq .
echo ""

# Test 1.2: Login User
echo "Test 1.2: User Login"
login_data="{
  \"email\": \"$TEST_EMAIL\",
  \"password\": \"$TEST_PASSWORD\"
}"
login_response=$(curl -s -X POST "$BASE_URL/auth/login/" \
    -H "Content-Type: application/json" \
    -d "$login_data")
access_token=$(echo "$login_response" | jq -r '.access' 2>/dev/null)
refresh_token=$(echo "$login_response" | jq -r '.refresh' 2>/dev/null)
tenant_id=$(echo "$login_response" | jq -r '.tenant_id' 2>/dev/null)
echo "Response: $login_response" | jq .
echo "Access Token: ${access_token:0:50}..."
echo ""

if [ -z "$access_token" ] || [ "$access_token" = "null" ]; then
    echo -e "${RED}ERROR: Could not obtain access token. Exiting.${NC}"
    exit 1
fi

AUTH_HEADER="Authorization: Bearer $access_token"

# Test 1.3: Get Current User
echo "Test 1.3: Get Current User"
test_endpoint "GET" "/auth/me/" "" "$AUTH_HEADER" "Current User"
echo ""

# Test 1.4: Forgot Password
echo "Test 1.4: Forgot Password Request"
forgot_data="{
  \"email\": \"$TEST_EMAIL\"
}"
test_endpoint "POST" "/auth/forgot-password/" "$forgot_data" "Content-Type: application/json" "Forgot Password"
echo ""

# ============================================================================
# SECTION 2: CONTRACT ENDPOINTS
# ============================================================================

print_header "2. CONTRACT MANAGEMENT ENDPOINTS"

# Test 2.1: Create Contract (without file first to test)
echo "Test 2.1: List Contracts (Empty)"
test_endpoint "GET" "/contracts/" "" "$AUTH_HEADER" "List Contracts"
echo ""

# Test 2.2: Create a Simple Contract
echo "Test 2.2: Create Contract"
contract_data="{
  \"title\": \"Test Service Agreement\",
  \"contract_type\": \"service\",
  \"counterparty\": \"Acme Corporation\",
  \"value\": 50000.00,
  \"start_date\": \"2026-01-15\",
  \"end_date\": \"2027-01-15\",
  \"description\": \"Test contract for API validation\"
}"

# Create a temporary file for upload
temp_file="/tmp/test_contract_$TIMESTAMP.txt"
echo "This is a test contract document for API testing." > "$temp_file"

contract_response=$(curl -s -X POST "$BASE_URL/contracts/" \
    -H "$AUTH_HEADER" \
    -F "title=Test Service Agreement" \
    -F "contract_type=service" \
    -F "counterparty=Acme Corporation" \
    -F "value=50000.00" \
    -F "start_date=2026-01-15" \
    -F "end_date=2027-01-15" \
    -F "file=@$temp_file")

contract_id=$(echo "$contract_response" | jq -r '.id' 2>/dev/null)
echo "Response: $contract_response" | jq .
echo "Contract ID: $contract_id"
echo ""

if [ -z "$contract_id" ] || [ "$contract_id" = "null" ]; then
    echo -e "${YELLOW}Note: Contract creation may require file. Continuing with tests...${NC}"
else
    # Test 2.3: Get Contract Details
    echo "Test 2.3: Get Contract Details"
    test_endpoint "GET" "/contracts/$contract_id/" "" "$AUTH_HEADER" "Get Contract"
    echo ""
    
    # Test 2.4: Update Contract
    echo "Test 2.4: Update Contract"
    update_data="{
      \"title\": \"Updated Service Agreement\",
      \"value\": 60000.00
    }"
    test_endpoint "PATCH" "/contracts/$contract_id/" "$update_data" "$AUTH_HEADER" "Update Contract"
    echo ""
    
    # Test 2.5: Submit Contract
    echo "Test 2.5: Submit Contract for Approval"
    submit_data="{
      \"comment\": \"Ready for legal review\"
    }"
    test_endpoint "POST" "/contracts/$contract_id/submit/" "$submit_data" "$AUTH_HEADER" "Submit Contract"
    echo ""
    
    # Test 2.6: Approve Contract
    echo "Test 2.6: Approve Contract"
    approve_data="{
      \"decision\": \"approved\",
      \"comment\": \"Approved by legal team\"
    }"
    test_endpoint "POST" "/contracts/$contract_id/decide/" "$approve_data" "$AUTH_HEADER" "Approve Contract"
    echo ""
    
    # Test 2.7: Get Contract Logs
    echo "Test 2.7: Get Contract Audit Logs"
    test_endpoint "GET" "/contracts/$contract_id/logs/" "" "$AUTH_HEADER" "Contract Logs"
    echo ""
fi

# Test 2.8: List Contracts
echo "Test 2.8: List All Contracts"
test_endpoint "GET" "/contracts/" "" "$AUTH_HEADER" "List Contracts"
echo ""

# Test 2.9: Contract Statistics
echo "Test 2.9: Contract Statistics"
test_endpoint "GET" "/contracts/statistics/" "" "$AUTH_HEADER" "Statistics"
echo ""

# Test 2.10: Recent Contracts
echo "Test 2.10: Recent Contracts"
test_endpoint "GET" "/contracts/recent/" "" "$AUTH_HEADER" "Recent Contracts"
echo ""

# ============================================================================
# SECTION 3: TEMPLATE ENDPOINTS
# ============================================================================

print_header "3. TEMPLATE MANAGEMENT ENDPOINTS"

# Test 3.1: List Templates
echo "Test 3.1: List Contract Templates"
test_endpoint "GET" "/contract-templates/" "" "$AUTH_HEADER" "List Templates"
echo ""

# Test 3.2: Create Template
echo "Test 3.2: Create Contract Template"
template_data="{
  \"name\": \"Standard Service Agreement\",
  \"contract_type\": \"service\",
  \"merge_fields\": [\"service_name\", \"start_date\", \"end_date\", \"price\"],
  \"mandatory_clauses\": [\"scope_of_work\", \"payment_terms\"]
}"

# Create template file
template_file="/tmp/test_template_$TIMESTAMP.docx"
echo "Template content" > "$template_file"

template_response=$(curl -s -X POST "$BASE_URL/contract-templates/" \
    -H "$AUTH_HEADER" \
    -F "name=Standard Service Agreement" \
    -F "contract_type=service" \
    -F "file=@$template_file")

template_id=$(echo "$template_response" | jq -r '.id' 2>/dev/null)
echo "Response: $template_response" | jq .
echo ""

if [ ! -z "$template_id" ] && [ "$template_id" != "null" ]; then
    echo "Test 3.3: Get Template Details"
    test_endpoint "GET" "/contract-templates/$template_id/" "" "$AUTH_HEADER" "Get Template"
    echo ""
fi

# ============================================================================
# SECTION 4: CLAUSE ENDPOINTS
# ============================================================================

print_header "4. CLAUSE LIBRARY ENDPOINTS"

# Test 4.1: List Clauses
echo "Test 4.1: List Clauses"
test_endpoint "GET" "/clauses/" "" "$AUTH_HEADER" "List Clauses"
echo ""

# Test 4.2: Create Clause
echo "Test 4.2: Create Clause"
clause_data="{
  \"name\": \"Limitation of Liability\",
  \"contract_type\": \"service\",
  \"content\": \"Neither party shall be liable for indirect, incidental, or consequential damages...\",
  \"is_mandatory\": false,
  \"tags\": [\"liability\", \"risk_mitigation\"]
}"
test_endpoint "POST" "/clauses/" "$clause_data" "$AUTH_HEADER" "Create Clause"
echo ""

# ============================================================================
# SECTION 5: GENERATION ENDPOINTS
# ============================================================================

print_header "5. CONTRACT GENERATION ENDPOINTS"

# Test 5.1: List Generation Jobs
echo "Test 5.1: List Generation Jobs"
test_endpoint "GET" "/generation-jobs/" "" "$AUTH_HEADER" "List Generation Jobs"
echo ""

# Test 5.2: Create Generation Job
echo "Test 5.2: Create Generation Job"
job_data="{
  \"template_id\": \"test-template-id\",
  \"contract_type\": \"service\",
  \"structured_inputs\": {
    \"service_name\": \"Cloud Services\",
    \"start_date\": \"2026-02-01\",
    \"end_date\": \"2027-02-01\",
    \"price\": 100000
  }
}"
test_endpoint "POST" "/generation-jobs/" "$job_data" "$AUTH_HEADER" "Create Generation Job"
echo ""

# ============================================================================
# CLEANUP
# ============================================================================

print_header "CLEANUP"

# Delete temp files
rm -f "$temp_file" "$template_file"
echo "Temporary files cleaned up"
echo ""

# ============================================================================
# TEST SUMMARY
# ============================================================================

print_header "TEST SUMMARY"

echo "Total Tests Run: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    exit 1
fi
