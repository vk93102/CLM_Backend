#!/bin/bash

################################################################################
# PRODUCTION TEST SUITE - REAL RESPONSES OUTPUT
# CLM Backend AI Endpoints v5.0
#
# This script displays actual API responses, not just pass/fail labels
# Shows real JSON responses from all three endpoints
################################################################################

set -o pipefail

# Configuration
API_BASE_URL="http://localhost:11000/api/v1"
TEST_TOKEN_FILE="${HOME}/CLM_Backend/TEST_TOKEN.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get JWT Token
if [ ! -f "$TEST_TOKEN_FILE" ]; then
    echo -e "${RED}ERROR: Token file not found at $TEST_TOKEN_FILE${NC}"
    exit 1
fi

AUTH_TOKEN=$(cat "$TEST_TOKEN_FILE")

# Header
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                            ║${NC}"
echo -e "${BLUE}║         PRODUCTION API RESPONSES - CLM BACKEND AI ENDPOINTS                ║${NC}"
echo -e "${BLUE}║                        Real JSON Output                                    ║${NC}"
echo -e "${BLUE}║                                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# ENDPOINT 5: CLAUSE CLASSIFICATION
# ============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}ENDPOINT 5: CLAUSE CLASSIFICATION${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo "POST /api/v1/ai/classify/"
echo ""

# Test 1: Confidentiality Clause
echo -e "${YELLOW}Test 1: Confidentiality Clause${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Request Text:"
echo '  "Both parties agree to maintain strict confidentiality of all information shared during negotiations."'
echo ""
echo "Response:"

START_TIME=$(date +%s%N)
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${API_BASE_URL}/ai/classify/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"text":"Both parties agree to maintain strict confidentiality of all information shared during negotiations."}')
END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo -e "${GREEN}HTTP $HTTP_CODE${NC} (${ELAPSED}ms)"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

# Test 2: Termination Clause
echo -e "${YELLOW}Test 2: Termination Clause${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Request Text:"
echo '  "Either party may terminate this Agreement upon thirty (30) days prior written notice..."'
echo ""
echo "Response:"

START_TIME=$(date +%s%N)
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${API_BASE_URL}/ai/classify/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"text":"Either party may terminate this Agreement upon thirty (30) days prior written notice to the other party. In the event of material breach, either party may terminate immediately upon written notice if the breaching party fails to cure such breach within fifteen (15) days of notification."}')
END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo -e "${GREEN}HTTP $HTTP_CODE${NC} (${ELAPSED}ms)"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

# Test 3: Payment Terms Clause
echo -e "${YELLOW}Test 3: Payment Terms Clause${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Request Text:"
echo '  "Payment shall be made within thirty (30) days of invoice receipt..."'
echo ""
echo "Response:"

START_TIME=$(date +%s%N)
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${API_BASE_URL}/ai/classify/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"text":"Payment shall be made within thirty (30) days of invoice receipt. Late payments shall accrue interest at the rate of 1.5% per month or the maximum rate permitted by law, whichever is lower. All invoices must be in USD and paid via wire transfer to the account designated by Service Provider."}')
END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo -e "${GREEN}HTTP $HTTP_CODE${NC} (${ELAPSED}ms)"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

# Test 4: IP Protection Clause
echo -e "${YELLOW}Test 4: Intellectual Property Clause${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Request Text:"
echo '  "All intellectual property rights... shall remain exclusive property of Service Provider..."'
echo ""
echo "Response:"

START_TIME=$(date +%s%N)
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${API_BASE_URL}/ai/classify/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"text":"All intellectual property rights, including but not limited to patents, copyrights, trademarks, and trade secrets developed, created, or discovered by Service Provider in performance of this Agreement shall remain exclusive property of Service Provider. Client retains all rights to pre-existing intellectual property and background technology."}')
END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo -e "${GREEN}HTTP $HTTP_CODE${NC} (${ELAPSED}ms)"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

# ============================================================================
# ENDPOINT 3: DRAFT GENERATION
# ============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}ENDPOINT 3: DRAFT GENERATION (ASYNC)${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo "POST /api/v1/ai/generate/draft/"
echo ""

# Test 1: NDA Draft
echo -e "${YELLOW}Test 1: NDA Draft Generation${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Request Payload:"
echo '{
  "contract_type": "NDA",
  "input_params": {
    "party_1": "Acme Corporation",
    "party_2": "Innovation Partners LLC",
    "duration_years": 2,
    "jurisdiction": "Delaware"
  }
}'
echo ""
echo "Response:"

START_TIME=$(date +%s%N)
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${API_BASE_URL}/ai/generate/draft/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"contract_type":"NDA","input_params":{"party_1":"Acme Corporation","party_2":"Innovation Partners LLC","duration_years":2,"jurisdiction":"Delaware"}}')
END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo -e "${GREEN}HTTP $HTTP_CODE${NC} (${ELAPSED}ms)"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

# Test 2: Service Agreement Draft
echo -e "${YELLOW}Test 2: Service Agreement Draft Generation${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Request Payload:"
echo '{
  "contract_type": "Service Agreement",
  "input_params": {
    "party_1": "TechCorp Services Inc.",
    "party_2": "Enterprise Solutions Ltd.",
    "monthly_value": 50000,
    "sla": "99.9%"
  }
}'
echo ""
echo "Response:"

START_TIME=$(date +%s%N)
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${API_BASE_URL}/ai/generate/draft/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"contract_type":"Service Agreement","input_params":{"party_1":"TechCorp Services Inc.","party_2":"Enterprise Solutions Ltd.","monthly_value":50000,"sla":"99.9%"}}')
END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo -e "${GREEN}HTTP $HTTP_CODE${NC} (${ELAPSED}ms)"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

# ============================================================================
# ENDPOINT 4: METADATA EXTRACTION
# ============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}ENDPOINT 4: METADATA EXTRACTION${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo "POST /api/v1/ai/extract/metadata/"
echo ""

# Test 1: Service Contract
echo -e "${YELLOW}Test 1: Service Contract Metadata Extraction${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Request Contract Text:"
echo "  SERVICE AGREEMENT between CloudTech Solutions Corp. and GlobalEnterprises Inc."
echo "  Value: \$600,000 annually"
echo ""
echo "Response:"

CONTRACT_TEXT="SERVICE AGREEMENT

This Service Agreement (\"Agreement\") is entered into as of January 1, 2024, by and between CloudTech Solutions Corp. (\"Service Provider\") and GlobalEnterprises Inc. (\"Client\").

1. SERVICES
Service Provider shall provide cloud infrastructure services valued at \$600,000 annually.

2. TERM
This Agreement shall commence on January 1, 2024, and continue for a period of one (1) year unless earlier terminated.

3. PAYMENT
Payment shall be made quarterly in advance."

START_TIME=$(date +%s%N)
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${API_BASE_URL}/ai/extract/metadata/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"document_text\": $(echo "$CONTRACT_TEXT" | jq -Rs .)}")
END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo -e "${GREEN}HTTP $HTTP_CODE${NC} (${ELAPSED}ms)"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

# Test 2: NDA
echo -e "${YELLOW}Test 2: NDA Metadata Extraction${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Request Contract Text:"
echo "  MUTUAL NON-DISCLOSURE AGREEMENT between InnovateTech Inc. and Venture Capital Partners LP"
echo "  Confidential Value: \$100,000"
echo ""
echo "Response:"

NDA_TEXT="MUTUAL NON-DISCLOSURE AGREEMENT

This NDA (\"Agreement\") is between InnovateTech Inc. and Venture Capital Partners LP.

CONFIDENTIAL VALUE: \$100,000
EFFECTIVE DATE: January 1, 2024
TERM: 3 years

Both parties agree to maintain confidentiality of all proprietary information."

START_TIME=$(date +%s%N)
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${API_BASE_URL}/ai/extract/metadata/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"document_text\": $(echo "$NDA_TEXT" | jq -Rs .)}")
END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo -e "${GREEN}HTTP $HTTP_CODE${NC} (${ELAPSED}ms)"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

# ============================================================================
# SECURITY TESTS
# ============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}SECURITY & VALIDATION TESTS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 1: Missing Required Field
echo -e "${YELLOW}Test 1: Missing Required Field (Empty Text)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Request: Empty text field"
echo ""
echo "Response (Expected HTTP 400):"

START_TIME=$(date +%s%N)
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${API_BASE_URL}/ai/classify/" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"text":""}')
END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "400" ]; then
    echo -e "${RED}HTTP $HTTP_CODE${NC} (${ELAPSED}ms) - Validation Error"
else
    echo -e "${YELLOW}HTTP $HTTP_CODE${NC} (${ELAPSED}ms)"
fi
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

# Test 2: Invalid JWT Token
echo -e "${YELLOW}Test 2: Invalid JWT Token${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Request: Bearer token='invalid_token_xyz'"
echo ""
echo "Response (Expected HTTP 401):"

START_TIME=$(date +%s%N)
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${API_BASE_URL}/ai/classify/" \
    -H "Authorization: Bearer invalid_token_xyz" \
    -H "Content-Type: application/json" \
    -d '{"text":"test"}')
END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "401" ]; then
    echo -e "${RED}HTTP $HTTP_CODE${NC} (${ELAPSED}ms) - Unauthorized"
else
    echo -e "${YELLOW}HTTP $HTTP_CODE${NC} (${ELAPSED}ms)"
fi
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

# Test 3: No Authorization Header
echo -e "${YELLOW}Test 3: No Authorization Header${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Request: No Authorization header"
echo ""
echo "Response (Expected HTTP 401):"

START_TIME=$(date +%s%N)
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${API_BASE_URL}/ai/classify/" \
    -H "Content-Type: application/json" \
    -d '{"text":"test"}')
END_TIME=$(date +%s%N)
ELAPSED=$(( (END_TIME - START_TIME) / 1000000 ))

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "401" ]; then
    echo -e "${RED}HTTP $HTTP_CODE${NC} (${ELAPSED}ms) - Unauthorized"
else
    echo -e "${YELLOW}HTTP $HTTP_CODE${NC} (${ELAPSED}ms)"
fi
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

# Footer
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✅ API Response Testing Complete${NC}"
echo ""
echo "All responses are real-time from live APIs:"
echo "  • Gemini 2.0-Flash (classification & extraction)"
echo "  • Voyage AI Law-2 embeddings (semantic analysis)"
echo "  • PostgreSQL database (party extraction)"
echo "  • Redis/Celery (async task queue)"
echo ""
echo "No mock data - all responses are authentic API outputs"
echo ""
