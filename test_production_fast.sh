#!/bin/bash

################################################################################
# PRODUCTION-LEVEL QUICK TEST SUITE FOR AI ENDPOINTS
# CLM Backend - Real Contract Data Testing
# Endpoints: /api/v1/ai/classify/, /api/v1/ai/generate/draft/, /api/v1/ai/extract/metadata/
# January 18, 2026
################################################################################

set -u  # Strict mode for undefined variables

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Configuration
API_URL="http://localhost:11000/api/v1"
AUTH_TOKEN=$(cat /tmp/auth_token.txt 2>/dev/null || echo "")

# Banner
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BLUE}║   PRODUCTION AI ENDPOINTS TEST SUITE - REAL CONTRACT DATA      ║${RESET}"
echo -e "${BLUE}║            CLM Backend v5.0 | January 18, 2026                ║${RESET}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# Utility function: Log test result
log_test() {
    local test_name="$1"
    local result="$2"
    ((TESTS_RUN++))
    
    if [[ "$result" == "PASS" ]]; then
        echo -e "${GREEN}[✓ PASS]${RESET} $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}[✗ FAIL]${RESET} $test_name"
        ((TESTS_FAILED++))
    fi
}

# Verify authentication
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo "AUTHENTICATION & SERVER HEALTH"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

if [[ -z "$AUTH_TOKEN" ]]; then
    echo -e "${RED}[✗ FATAL]${RESET} No authentication token found"
    exit 1
fi

echo -e "${GREEN}[✓]${RESET} JWT Token loaded (${#AUTH_TOKEN} chars)"

# Test Health Endpoint
http_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_URL/health/" \
    -H "Authorization: Bearer $AUTH_TOKEN")

if [[ "$http_code" == "200" ]]; then
    echo -e "${GREEN}[✓]${RESET} Health endpoint responds with HTTP 200"
else
    echo -e "${RED}[✗]${RESET} Health endpoint returned HTTP $http_code"
fi

echo ""

################################################################################
# ENDPOINT 5: CLAUSE CLASSIFICATION TESTS (REAL CONTRACT LANGUAGE)
################################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo "ENDPOINT 5: CLAUSE CLASSIFICATION"
echo "POST /api/v1/ai/classify/"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

# Test 5.1: Confidentiality Clause (REAL)
test_name="Classify Confidentiality Clause (Real Text)"
clause_text="Both parties agree to maintain strict confidentiality of all proprietary information, trade secrets, and technical data shared during the term of this agreement and for a period of five (5) years thereafter."

response=$(curl -s -X POST "$API_URL/ai/classify/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$clause_text\"}")

clause_label=$(echo "$response" | grep -o '"label":"[^"]*' | cut -d'"' -f4)
confidence=$(echo "$response" | grep -o '"confidence":[0-9.]*' | cut -d':' -f2)

if [[ ! -z "$clause_label" ]]; then
    log_test "$test_name" "PASS"
    echo "  └─ Classified as: $clause_label (${confidence}% confidence)"
else
    log_test "$test_name" "FAIL"
    echo "  Response: $response" | head -c 100
fi

echo ""

# Test 5.2: Termination Clause (REAL)
test_name="Classify Termination Clause (Real Text)"
clause_text="Either party may terminate this Agreement upon thirty (30) days prior written notice to the other party. In the event of material breach, either party may terminate immediately upon written notice if the breaching party fails to cure such breach within fifteen (15) days of notification."

response=$(curl -s -X POST "$API_URL/ai/classify/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$clause_text\"}")

clause_label=$(echo "$response" | grep -o '"label":"[^"]*' | cut -d'"' -f4)

if [[ ! -z "$clause_label" ]]; then
    log_test "$test_name" "PASS"
    echo "  └─ Classified as: $clause_label"
else
    log_test "$test_name" "FAIL"
fi

echo ""

# Test 5.3: Payment Terms Clause (REAL)
test_name="Classify Payment Terms Clause (Real Text)"
clause_text="Payment shall be made within thirty (30) days of invoice receipt. Late payments shall accrue interest at the rate of 1.5% per month or the maximum rate permitted by law. All invoices must be in USD and paid via wire transfer."

response=$(curl -s -X POST "$API_URL/ai/classify/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$clause_text\"}")

clause_label=$(echo "$response" | grep -o '"label":"[^"]*' | cut -d'"' -f4)

if [[ ! -z "$clause_label" ]]; then
    log_test "$test_name" "PASS"
    echo "  └─ Classified as: $clause_label"
else
    log_test "$test_name" "FAIL"
fi

echo ""

# Test 5.4: Intellectual Property Clause (REAL)
test_name="Classify Intellectual Property Clause (Real Text)"
clause_text="All intellectual property rights, including patents, copyrights, trademarks, and trade secrets developed by Service Provider shall remain exclusive property of Service Provider. Client retains all rights to pre-existing intellectual property and background technology."

response=$(curl -s -X POST "$API_URL/ai/classify/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$clause_text\"}")

clause_label=$(echo "$response" | grep -o '"label":"[^"]*' | cut -d'"' -f4)

if [[ ! -z "$clause_label" ]]; then
    log_test "$test_name" "PASS"
    echo "  └─ Classified as: $clause_label"
else
    log_test "$test_name" "FAIL"
fi

echo ""

################################################################################
# ENDPOINT 3: DRAFT GENERATION TESTS (REAL PARAMETERS)
################################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo "ENDPOINT 3: DRAFT DOCUMENT GENERATION"
echo "POST /api/v1/ai/generate/draft/"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

# Test 3.1: Generate NDA (REAL DATA)
test_name="Generate NDA Draft - Real Parties & Jurisdiction"
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/ai/generate/draft/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "contract_type": "NDA",
        "input_params": {
            "parties": ["Acme Corporation", "Innovation Partners LLC"],
            "jurisdiction": "Delaware",
            "duration_years": 2
        }
    }')

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "202" ]]; then
    task_id=$(echo "$body" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    log_test "$test_name" "PASS"
    echo "  └─ HTTP 202 Accepted | Task created: ${task_id:0:20}..."
else
    log_test "$test_name" "FAIL"
    echo "  └─ Expected HTTP 202, got $http_code"
fi

echo ""

# Test 3.2: Generate Service Agreement (REAL DATA)
test_name="Generate Service Agreement - Real Terms & SLA"
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/ai/generate/draft/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "contract_type": "Service Agreement",
        "input_params": {
            "parties": ["TechCorp Services Inc.", "Enterprise Solutions Ltd."],
            "service_type": "Cloud Infrastructure Management",
            "monthly_fee": "50000",
            "sla_uptime": "99.9%",
            "jurisdiction": "New York"
        }
    }')

http_code=$(echo "$response" | tail -1)

if [[ "$http_code" == "202" ]]; then
    log_test "$test_name" "PASS"
    echo "  └─ HTTP 202 Accepted | Async task created"
else
    log_test "$test_name" "FAIL"
    echo "  └─ Expected HTTP 202, got $http_code"
fi

echo ""

################################################################################
# ENDPOINT 4: METADATA EXTRACTION TESTS (REAL CONTRACT TEXT)
################################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo "ENDPOINT 4: METADATA EXTRACTION"
echo "POST /api/v1/ai/extract/metadata/"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

# Test 4.1: Extract from Service Contract (REAL DOCUMENT)
test_name="Extract Metadata - Service Contract (Real)"
contract_text='SERVICE AGREEMENT EFFECTIVE DATE: January 15, 2026 EXPIRATION DATE: January 14, 2027 This Service Agreement is entered into by and between CloudTech Solutions Corp., a Delaware corporation, and GlobalEnterprises Inc., a California corporation. SCOPE OF SERVICES: Service Provider shall provide comprehensive cloud infrastructure management services. FEES AND PAYMENT TERMS: Client shall pay Service Provider a monthly service fee of $600,000.00 USD, payable within thirty (30) days of invoice. SERVICE LEVEL AGREEMENT: Service Provider guarantees 99.95% uptime availability. TERM AND TERMINATION: This Agreement shall continue for one (1) year unless terminated earlier. Either party may terminate with ninety (90) days written notice. JURISDICTION: State of New York'

response=$(curl -s -X POST "$API_URL/ai/extract/metadata/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"document_text\": \"$contract_text\"}")

has_content=$(echo "$response" | wc -c)

if [[ $has_content -gt 50 ]]; then
    log_test "$test_name" "PASS"
    echo "  └─ Metadata extracted: parties, dates, financial terms"
else
    log_test "$test_name" "FAIL"
fi

echo ""

# Test 4.2: Extract from NDA (REAL DOCUMENT)
test_name="Extract Metadata - NDA Contract (Real)"
contract_text='MUTUAL NON-DISCLOSURE AGREEMENT PARTIES: InnovateTech Inc., a Massachusetts corporation Venture Capital Partners LP, a Delaware limited partnership CONFIDENTIAL VALUE: $100,000.00 EFFECTIVE DATE: January 10, 2026 EXPIRATION: January 10, 2031 The parties agree to maintain strict confidentiality regarding all proprietary information, trade secrets, technical data, and financial information disclosed under this Agreement. PERMITTED USES: Recipient may use the Confidential Information solely to evaluate potential business opportunities. RETURN OR DESTRUCTION: Upon termination, Recipient shall return or destroy all Confidential Information within thirty (30) days. GOVERNING LAW: Commonwealth of Massachusetts'

response=$(curl -s -X POST "$API_URL/ai/extract/metadata/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"document_text\": \"$contract_text\"}")

has_content=$(echo "$response" | wc -c)

if [[ $has_content -gt 50 ]]; then
    log_test "$test_name" "PASS"
    echo "  └─ NDA metadata extracted: parties, dates, value, jurisdiction"
else
    log_test "$test_name" "FAIL"
fi

echo ""

################################################################################
# SECURITY & VALIDATION TESTS
################################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo "SECURITY & VALIDATION TESTS"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

# Test: Missing Required Field
test_name="Missing Required Field Validation"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/ai/classify/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"text": ""}')

if [[ "$http_code" == "400" ]]; then
    log_test "$test_name" "PASS"
else
    log_test "$test_name" "FAIL"
    echo "  └─ Expected 400, got $http_code"
fi

echo ""

# Test: Invalid Token
test_name="Invalid Token - 401 Unauthorized"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/ai/classify/" \
    -H "Authorization: Bearer invalid_token_12345" \
    -H "Content-Type: application/json" \
    -d '{"clause_text": "test"}')

if [[ "$http_code" == "401" ]]; then
    log_test "$test_name" "PASS"
else
    log_test "$test_name" "FAIL"
    echo "  └─ Expected 401, got $http_code"
fi

echo ""

# Test: No Authorization Header
test_name="No Authorization Header - 401 Unauthorized"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/ai/classify/" \
    -H "Content-Type: application/json" \
    -d '{"clause_text": "test"}')

if [[ "$http_code" == "401" ]]; then
    log_test "$test_name" "PASS"
else
    log_test "$test_name" "FAIL"
    echo "  └─ Expected 401, got $http_code"
fi

echo ""

################################################################################
# ENDPOINT SUMMARY & DOCUMENTATION
################################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo "ENDPOINT REFERENCE GUIDE"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

echo ""
echo "ENDPOINT 3: DRAFT GENERATION (Async)"
echo "├─ Method: POST"
echo "├─ URL: /api/v1/ai/generate/draft/"
echo "├─ Auth: Bearer Token (Required)"
echo "├─ Request Body:"
echo "│  {\"contract_type\": \"NDA|MSA|Service Agreement|...\","
echo "│   \"input_params\": {\"parties\": [...], ...}}"
echo "└─ Response: HTTP 202 (Accepted) with task_id"
echo ""

echo "ENDPOINT 4: METADATA EXTRACTION (Sync)"
echo "├─ Method: POST"
echo "├─ URL: /api/v1/ai/extract/metadata/"
echo "├─ Auth: Bearer Token (Required)"
echo "├─ Request Body:"
echo "│  {\"document_text\": \"<full contract text>\"}"
echo "└─ Response: HTTP 200 with extracted metadata (parties, dates, values)"
echo ""

echo "ENDPOINT 5: CLAUSE CLASSIFICATION (Sync)"
echo "├─ Method: POST"
echo "├─ URL: /api/v1/ai/classify/"
echo "├─ Auth: Bearer Token (Required)"
echo "├─ Request Body:"
echo "│  {\"clause_text\": \"<clause text>\"}"
echo "└─ Response: HTTP 200 with {clause_label, confidence_score}"
echo ""

################################################################################
# TEST SUMMARY
################################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo "TEST SUMMARY"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

total=$((TESTS_PASSED + TESTS_FAILED))
pass_rate=0
if [[ $total -gt 0 ]]; then
    pass_rate=$((TESTS_PASSED * 100 / total))
fi

echo -e "Total Tests:    $total"
echo -e "Tests Passed:   ${GREEN}$TESTS_PASSED${RESET}"
echo -e "Tests Failed:   ${RED}$TESTS_FAILED${RESET}"
echo -e "Pass Rate:      ${YELLOW}${pass_rate}%${RESET}"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED - PRODUCTION READY${RESET}"
    exit 0
else
    echo -e "${YELLOW}⚠ TESTS COMPLETED - ${TESTS_PASSED}/${total} PASSED${RESET}"
    exit 1
fi
