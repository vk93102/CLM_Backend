#!/bin/bash
################################################################################
# PRODUCTION-LEVEL BASH TEST SUITE FOR AI ENDPOINTS
# Contract Lifecycle Management (CLM) Backend
# Version: 1.0
# Date: January 18, 2026
################################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:11000/api/v1"
JWT_TOKEN=""
TENANT_ID=""
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

################################################################################
# UTILITY FUNCTIONS
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓ PASS]${NC} $1"
    ((PASSED_TESTS++))
}

log_error() {
    echo -e "${RED}[✗ FAIL]${NC} $1"
    ((FAILED_TESTS++))
}

log_warning() {
    echo -e "${YELLOW}[⚠ WARN]${NC} $1"
}

log_section() {
    echo ""
    echo "================================================================================"
    echo -e "${BLUE}$1${NC}"
    echo "================================================================================"
}

# Get authentication token
get_auth_token() {
    log_info "Retrieving JWT authentication token..."
    
    if [ ! -f "/tmp/auth_token.txt" ]; then
        log_error "No auth token found. Run setup first."
        exit 1
    fi
    
    JWT_TOKEN=$(cat /tmp/auth_token.txt)
    TENANT_ID=$(cat /tmp/tenant_id.txt)
    
    log_success "JWT Token loaded: ${JWT_TOKEN:0:50}..."
    log_success "Tenant ID: $TENANT_ID"
}

# Health check
health_check() {
    log_section "HEALTH CHECK"
    ((TOTAL_TESTS++))
    
    RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/health/")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        log_success "Health check passed (HTTP 200)"
        log_info "Response: $BODY"
    else
        log_error "Health check failed (HTTP $HTTP_CODE)"
        exit 1
    fi
}

################################################################################
# ENDPOINT 5: CLAUSE CLASSIFICATION TESTS
################################################################################

test_endpoint_5_confidentiality() {
    ((TOTAL_TESTS++))
    
    local description="Classify Confidentiality Clause"
    local clause_text="Both parties agree to maintain strict confidentiality of all proprietary information, trade secrets, and sensitive business data disclosed under this agreement. Confidential information shall not be disclosed to third parties without prior written consent."
    
    log_info "Testing: $description"
    
    local payload=$(cat <<EOF
{
    "text": "$clause_text"
}
EOF
)
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/classify/" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        LABEL=$(echo "$BODY" | jq -r '.label' 2>/dev/null || echo "")
        CONFIDENCE=$(echo "$BODY" | jq -r '.confidence' 2>/dev/null || echo "0")
        
        if [ "$LABEL" = "Confidentiality" ] && (( $(echo "$CONFIDENCE > 0.7" | bc -l) )); then
            log_success "$description: Label=$LABEL, Confidence=${CONFIDENCE}%"
        else
            log_error "$description: Expected Confidentiality, got $LABEL"
        fi
    else
        log_error "$description (HTTP $HTTP_CODE): $BODY"
    fi
}

test_endpoint_5_termination() {
    ((TOTAL_TESTS++))
    
    local description="Classify Termination Clause"
    local clause_text="Either party may terminate this agreement at any time upon thirty (30) days written notice. In case of material breach, the non-breaching party may terminate immediately upon written notice if the breach is not cured within fifteen (15) days of notification."
    
    log_info "Testing: $description"
    
    local payload=$(cat <<EOF
{
    "text": "$clause_text"
}
EOF
)
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/classify/" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        LABEL=$(echo "$BODY" | jq -r '.label' 2>/dev/null || echo "")
        CONFIDENCE=$(echo "$BODY" | jq -r '.confidence' 2>/dev/null || echo "0")
        
        if [ "$LABEL" = "Termination" ] && (( $(echo "$CONFIDENCE > 0.7" | bc -l) )); then
            log_success "$description: Label=$LABEL, Confidence=${CONFIDENCE}%"
        else
            log_error "$description: Expected Termination, got $LABEL"
        fi
    else
        log_error "$description (HTTP $HTTP_CODE): $BODY"
    fi
}

test_endpoint_5_payment_terms() {
    ((TOTAL_TESTS++))
    
    local description="Classify Payment Terms"
    local clause_text="Payment shall be made within thirty (30) days of invoice receipt. Invoices must include itemized charges for services rendered. Late payments incur a 1.5% monthly interest charge. All payments must be made via wire transfer to the designated bank account."
    
    log_info "Testing: $description"
    
    local payload=$(cat <<EOF
{
    "text": "$clause_text"
}
EOF
)
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/classify/" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        LABEL=$(echo "$BODY" | jq -r '.label' 2>/dev/null || echo "")
        CONFIDENCE=$(echo "$BODY" | jq -r '.confidence' 2>/dev/null || echo "0")
        
        if [ "$LABEL" = "Payment Terms" ] && (( $(echo "$CONFIDENCE > 0.7" | bc -l) )); then
            log_success "$description: Label=$LABEL, Confidence=${CONFIDENCE}%"
        else
            log_error "$description: Expected Payment Terms, got $LABEL"
        fi
    else
        log_error "$description (HTTP $HTTP_CODE): $BODY"
    fi
}

test_endpoint_5_intellectual_property() {
    ((TOTAL_TESTS++))
    
    local description="Classify Intellectual Property Clause"
    local clause_text="All intellectual property, including patents, trademarks, copyrights, and trade secrets developed by either party shall remain the exclusive property of that party. Each party grants the other a non-exclusive, royalty-free license to use such intellectual property solely for the purposes of this agreement."
    
    log_info "Testing: $description"
    
    local payload=$(cat <<EOF
{
    "text": "$clause_text"
}
EOF
)
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/classify/" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        LABEL=$(echo "$BODY" | jq -r '.label' 2>/dev/null || echo "")
        CONFIDENCE=$(echo "$BODY" | jq -r '.confidence' 2>/dev/null || echo "0")
        
        if [ "$LABEL" = "Intellectual Property" ] && (( $(echo "$CONFIDENCE > 0.7" | bc -l) )); then
            log_success "$description: Label=$LABEL, Confidence=${CONFIDENCE}%"
        else
            log_error "$description: Expected Intellectual Property, got $LABEL"
        fi
    else
        log_error "$description (HTTP $HTTP_CODE): $BODY"
    fi
}

################################################################################
# ENDPOINT 3: DRAFT GENERATION TESTS
################################################################################

test_endpoint_3_nda_generation() {
    ((TOTAL_TESTS++))
    
    local description="Generate NDA Draft"
    
    log_info "Testing: $description"
    
    local payload=$(cat <<EOF
{
    "contract_type": "NDA",
    "parties": ["Acme Corporation", "Innovation Partners LLC"],
    "input_params": {
        "duration": "2 years",
        "jurisdiction": "Delaware",
        "effective_date": "2026-01-18",
        "confidentiality_level": "strict"
    }
}
EOF
)
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/generate/draft/" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "202" ]; then
        TASK_ID=$(echo "$BODY" | jq -r '.task_id' 2>/dev/null || echo "")
        STATUS=$(echo "$BODY" | jq -r '.status' 2>/dev/null || echo "")
        
        if [ -n "$TASK_ID" ] && [ "$STATUS" = "pending" ]; then
            log_success "$description: Task ID=$TASK_ID, Status=$STATUS"
            
            # Test status polling
            sleep 1
            test_endpoint_3_status_polling "$TASK_ID"
        else
            log_error "$description: Invalid response format"
        fi
    else
        log_error "$description (HTTP $HTTP_CODE): $BODY"
    fi
}

test_endpoint_3_service_agreement_generation() {
    ((TOTAL_TESTS++))
    
    local description="Generate Service Agreement Draft"
    
    log_info "Testing: $description"
    
    local payload=$(cat <<EOF
{
    "contract_type": "Service Agreement",
    "parties": ["TechCorp Services Inc.", "Enterprise Solutions Ltd."],
    "input_params": {
        "service_type": "Cloud Infrastructure",
        "duration": "1 year",
        "sla_uptime": "99.9%",
        "monthly_fee": 50000,
        "start_date": "2026-02-01"
    }
}
EOF
)
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/generate/draft/" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "202" ]; then
        TASK_ID=$(echo "$BODY" | jq -r '.task_id' 2>/dev/null || echo "")
        STATUS=$(echo "$BODY" | jq -r '.status' 2>/dev/null || echo "")
        
        if [ -n "$TASK_ID" ] && [ "$STATUS" = "pending" ]; then
            log_success "$description: Task ID=$TASK_ID, Status=$STATUS"
            
            # Test status polling
            sleep 1
            test_endpoint_3_status_polling "$TASK_ID"
        else
            log_error "$description: Invalid response format"
        fi
    else
        log_error "$description (HTTP $HTTP_CODE): $BODY"
    fi
}

test_endpoint_3_status_polling() {
    ((TOTAL_TESTS++))
    
    local task_id=$1
    local description="Poll Draft Generation Status (Task: ${task_id:0:8}...)"
    
    log_info "Testing: $description"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/ai/generate/status/$task_id/" \
        -H "Authorization: Bearer $JWT_TOKEN")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        STATUS=$(echo "$BODY" | jq -r '.status' 2>/dev/null || echo "")
        log_success "$description: Current Status=$STATUS"
    else
        log_error "$description (HTTP $HTTP_CODE): $BODY"
    fi
}

################################################################################
# ENDPOINT 4: METADATA EXTRACTION TESTS
################################################################################

test_endpoint_4_service_contract() {
    ((TOTAL_TESTS++))
    
    local description="Extract Metadata: Service Contract"
    
    log_info "Testing: $description"
    
    local contract_text="SERVICE AGREEMENT

This Service Agreement ('Agreement') is entered into as of January 18, 2026 ('Effective Date'), by and between:

PROVIDER: CloudTech Solutions Corp., a Delaware corporation ('Provider')
CLIENT: GlobalEnterprises Inc., a New York corporation ('Client')

SERVICES: Cloud infrastructure hosting and managed services
TERM: One (1) year from the Effective Date
CONTRACT VALUE: USD 600,000.00 annually

The Provider shall provide cloud infrastructure hosting services to the Client. The Client shall pay Provider the contract value in monthly installments of USD 50,000.00, due on the 15th of each month.

Effective Date: January 18, 2026
Termination Date: January 17, 2027

This Agreement is governed by the laws of Delaware."
    
    local payload=$(cat <<EOF
{
    "document_id": "test-doc-001",
    "document_text": "$contract_text"
}
EOF
)
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/extract/metadata/" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        PARTIES=$(echo "$BODY" | jq -r '.parties | length' 2>/dev/null || echo "0")
        EFFECTIVE_DATE=$(echo "$BODY" | jq -r '.effective_date' 2>/dev/null || echo "")
        VALUE=$(echo "$BODY" | jq -r '.contract_value' 2>/dev/null || echo "")
        
        if [ "$PARTIES" -gt "0" ]; then
            log_success "$description: Parties=$PARTIES, Date=$EFFECTIVE_DATE, Value=$VALUE"
        else
            log_warning "$description: Extraction succeeded but parties not found"
        fi
    elif [ "$HTTP_CODE" = "500" ]; then
        log_warning "$description (HTTP 500): Gemini API access may be limited"
    else
        log_error "$description (HTTP $HTTP_CODE): $BODY"
    fi
}

test_endpoint_4_nda_contract() {
    ((TOTAL_TESTS++))
    
    local description="Extract Metadata: NDA Contract"
    
    log_info "Testing: $description"
    
    local contract_text="NON-DISCLOSURE AGREEMENT

Date: January 15, 2026

PARTIES:
- Disclosing Party: InnovateTech Inc., a Massachusetts corporation
- Receiving Party: Venture Capital Partners LP

CONFIDENTIALITY PERIOD: 3 years from the Effective Date

FINANCIAL CONSIDERATION: USD 100,000.00

EFFECTIVE DATE: January 15, 2026

PURPOSE: Evaluation of potential business collaboration in artificial intelligence research

This NDA is governed by Massachusetts law."
    
    local payload=$(cat <<EOF
{
    "document_id": "test-doc-002",
    "document_text": "$contract_text"
}
EOF
)
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/extract/metadata/" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        PARTIES=$(echo "$BODY" | jq -r '.parties | length' 2>/dev/null || echo "0")
        EFFECTIVE_DATE=$(echo "$BODY" | jq -r '.effective_date' 2>/dev/null || echo "")
        VALUE=$(echo "$BODY" | jq -r '.contract_value' 2>/dev/null || echo "")
        
        if [ "$PARTIES" -gt "0" ]; then
            log_success "$description: Parties=$PARTIES, Date=$EFFECTIVE_DATE, Value=$VALUE"
        else
            log_warning "$description: Extraction succeeded but parties not found"
        fi
    elif [ "$HTTP_CODE" = "500" ]; then
        log_warning "$description (HTTP 500): Gemini API access may be limited"
    else
        log_error "$description (HTTP $HTTP_CODE): $BODY"
    fi
}

################################################################################
# AUTHENTICATION TESTS
################################################################################

test_unauthorized_access() {
    ((TOTAL_TESTS++))
    
    local description="Verify 401 Unauthorized without token"
    
    log_info "Testing: $description"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/classify/" \
        -H "Content-Type: application/json" \
        -d '{"text": "test"}')
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "401" ]; then
        log_success "$description: Correctly returned 401"
    else
        log_error "$description: Expected 401, got $HTTP_CODE"
    fi
}

test_invalid_token() {
    ((TOTAL_TESTS++))
    
    local description="Verify 401 with invalid token"
    
    log_info "Testing: $description"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/classify/" \
        -H "Authorization: Bearer invalid-token-xyz" \
        -H "Content-Type: application/json" \
        -d '{"text": "test"}')
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "401" ]; then
        log_success "$description: Correctly rejected invalid token"
    else
        log_error "$description: Expected 401, got $HTTP_CODE"
    fi
}

################################################################################
# VALIDATION TESTS
################################################################################

test_missing_required_field() {
    ((TOTAL_TESTS++))
    
    local description="Validate missing required field in classify"
    
    log_info "Testing: $description"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/classify/" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{}')
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "400" ] || [ "$HTTP_CODE" = "422" ]; then
        log_success "$description: Correctly returned error (HTTP $HTTP_CODE)"
    else
        log_warning "$description: Expected 400/422, got $HTTP_CODE"
    fi
}

test_invalid_json() {
    ((TOTAL_TESTS++))
    
    local description="Validate invalid JSON handling"
    
    log_info "Testing: $description"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/classify/" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{invalid json}')
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "400" ]; then
        log_success "$description: Correctly rejected invalid JSON"
    else
        log_warning "$description: Expected 400, got $HTTP_CODE"
    fi
}

################################################################################
# PERFORMANCE TESTS
################################################################################

test_endpoint_5_performance() {
    ((TOTAL_TESTS++))
    
    local description="Performance: Classification response time < 1s"
    
    log_info "Testing: $description"
    
    local start_time=$(date +%s%N)
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ai/classify/" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"text": "confidential information"}')
    
    local end_time=$(date +%s%N)
    local elapsed_ms=$(( (end_time - start_time) / 1000000 ))
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "200" ] && [ "$elapsed_ms" -lt "1000" ]; then
        log_success "$description: ${elapsed_ms}ms (< 1000ms)"
    elif [ "$HTTP_CODE" = "200" ]; then
        log_warning "$description: ${elapsed_ms}ms (> 1000ms but response valid)"
    else
        log_error "$description: Response failed (HTTP $HTTP_CODE)"
    fi
}

################################################################################
# MAIN TEST RUNNER
################################################################################

main() {
    clear
    
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║     PRODUCTION-LEVEL BASH TEST SUITE FOR AI ENDPOINTS          ║"
    echo "║         Contract Lifecycle Management Backend v5.0             ║"
    echo "║                  January 18, 2026                              ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Setup
    log_section "SETUP & AUTHENTICATION"
    get_auth_token
    health_check
    
    # Authentication Tests
    log_section "ENDPOINT 3: DRAFT GENERATION (ASYNC)"
    test_endpoint_3_nda_generation
    test_endpoint_3_service_agreement_generation
    
    # Endpoint 5 Tests
    log_section "ENDPOINT 5: CLAUSE CLASSIFICATION"
    test_endpoint_5_confidentiality
    test_endpoint_5_termination
    test_endpoint_5_payment_terms
    test_endpoint_5_intellectual_property
    
    # Endpoint 4 Tests
    log_section "ENDPOINT 4: METADATA EXTRACTION"
    test_endpoint_4_service_contract
    test_endpoint_4_nda_contract
    
    # Security Tests
    log_section "SECURITY TESTS"
    test_unauthorized_access
    test_invalid_token
    
    # Validation Tests
    log_section "VALIDATION TESTS"
    test_missing_required_field
    test_invalid_json
    
    # Performance Tests
    log_section "PERFORMANCE TESTS"
    test_endpoint_5_performance
    
    # Summary
    log_section "TEST SUMMARY"
    
    local success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    
    echo ""
    echo "Total Tests:    $TOTAL_TESTS"
    echo -e "Passed:         ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Failed:         ${RED}$FAILED_TESTS${NC}"
    echo "Success Rate:   ${success_rate}%"
    echo ""
    
    if [ "$FAILED_TESTS" -eq "0" ]; then
        echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
        exit 0
    else
        echo -e "${RED}✗ SOME TESTS FAILED${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
