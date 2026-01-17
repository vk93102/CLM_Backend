#!/bin/bash

# Production-Level Testing Script for AI Endpoints
# Port: 11000
# This script demonstrates all endpoints with real examples

set -e

BASE_URL="http://localhost:11000/api/v1"
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Test tracking
TESTS_PASSED=0
TESTS_FAILED=0

test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    echo -ne "${CYAN}Testing: $name...${NC} "
    
    local response
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
          -H "Content-Type: application/json" \
          -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" \
          -H "Content-Type: application/json")
    fi
    
    local body=$(echo "$response" | sed '$d')
    local status=$(echo "$response" | tail -1)
    
    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} ($status)"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} (Expected $expected_status, got $status)"
        echo "  Response: $body"
        ((TESTS_FAILED++))
        return 1
    fi
}

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_section() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ============================================================================
# MAIN TEST SUITE
# ============================================================================

print_header "PRODUCTION AI ENDPOINTS - COMPREHENSIVE TEST SUITE"

echo "Server: $BASE_URL"
echo "Testing: Port 11000"
echo "Date: $(date)"
echo ""

# ============================================================================
# PHASE 1: ENDPOINT 5 - CLAUSE CLASSIFICATION
# ============================================================================

print_section "PHASE 1: ENDPOINT 5 - CLAUSE CLASSIFICATION"

test_endpoint \
    "Classification: Confidentiality" \
    "POST" \
    "/ai/classify/" \
    '{"text": "The parties agree to maintain the confidentiality of all non-public information disclosed in connection with this Agreement including but not limited to technical data, business plans, customer lists, and financial information. Each party agrees not to disclose this information without prior written consent except as required by law."}' \
    "200"

test_endpoint \
    "Classification: Payment Terms" \
    "POST" \
    "/ai/classify/" \
    '{"text": "Client shall pay Provider the sum of fifty thousand dollars USD according to the following schedule: 50 percent upon execution of this Agreement and 50 percent upon delivery and acceptance. Payments shall be made within 30 days of invoice. Late payments shall accrue interest at 1.5 percent per month."}' \
    "200"

test_endpoint \
    "Classification: Termination" \
    "POST" \
    "/ai/classify/" \
    '{"text": "This Agreement may be terminated by either party upon 30 days written notice for material breach that is not cured within 15 days of receipt of notice. Either party may also terminate immediately upon written notice if the other party becomes insolvent or files for bankruptcy."}' \
    "200"

test_endpoint \
    "Validation: Empty text" \
    "POST" \
    "/ai/classify/" \
    '{"text": ""}' \
    "400"

test_endpoint \
    "Validation: Missing text field" \
    "POST" \
    "/ai/classify/" \
    '{}' \
    "400"

test_endpoint \
    "Validation: Text too short" \
    "POST" \
    "/ai/classify/" \
    '{"text": "short"}' \
    "400"

# ============================================================================
# PHASE 2: ENDPOINT 4 - METADATA EXTRACTION
# ============================================================================

print_section "PHASE 2: ENDPOINT 4 - METADATA EXTRACTION"

test_endpoint \
    "Validation: Missing document_id" \
    "POST" \
    "/ai/extract/metadata/" \
    '{}' \
    "400"

test_endpoint \
    "Validation: Invalid document_id (non-existent)" \
    "POST" \
    "/ai/extract/metadata/" \
    '{"document_id": "00000000-0000-0000-0000-000000000000"}' \
    "404"

# ============================================================================
# PHASE 3: ENDPOINT 3 - DRAFT GENERATION
# ============================================================================

print_section "PHASE 3: ENDPOINT 3 - DRAFT GENERATION (ASYNC)"

test_endpoint \
    "Validation: Missing contract_type" \
    "POST" \
    "/ai/generate/draft/" \
    '{"input_params": {}}' \
    "400"

test_endpoint \
    "Validation: Invalid input_params type" \
    "POST" \
    "/ai/generate/draft/" \
    '{"contract_type": "NDA", "input_params": "invalid"}' \
    "400"

# Create a valid draft task
echo -ne "${CYAN}Creating draft generation task...${NC} "

DRAFT_RESPONSE=$(curl -s -X POST "$BASE_URL/ai/generate/draft/" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_type": "Service Agreement",
    "input_params": {
      "parties": ["Acme Corporation", "Widget Industries"],
      "contract_value": 100000,
      "currency": "USD",
      "start_date": "2024-02-01",
      "end_date": "2025-02-01",
      "scope": "Cloud infrastructure services including deployment and support"
    }
  }')

TASK_ID=$(echo "$DRAFT_RESPONSE" | jq -r '.id // empty' 2>/dev/null)
TASK_STATUS=$(echo "$DRAFT_RESPONSE" | jq -r '.status // empty' 2>/dev/null)

if [ ! -z "$TASK_ID" ] && [ "$TASK_STATUS" = "pending" ]; then
    echo -e "${GREEN}✓${NC}"
    echo "  Task ID: $TASK_ID"
    ((TESTS_PASSED++))
    
    # Test status polling
    echo ""
    echo -ne "${CYAN}Polling task status...${NC} "
    
    STATUS_RESPONSE=$(curl -s -X GET "$BASE_URL/ai/generate/status/$TASK_ID/" \
      -H "Content-Type: application/json")
    
    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // empty' 2>/dev/null)
    
    if [ ! -z "$STATUS" ] && [ "$STATUS" != "null" ]; then
        echo -e "${GREEN}✓${NC}"
        echo "  Status: $STATUS"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}✗${NC}"
    echo "  Response: $DRAFT_RESPONSE"
    ((TESTS_FAILED++))
fi

# ============================================================================
# PHASE 4: DATABASE VERIFICATION
# ============================================================================

print_section "PHASE 4: DATABASE VERIFICATION"

echo -ne "${CYAN}Checking anchor clauses in database...${NC} "

ANCHOR_COUNT=$(python3 << 'PYEOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()
from ai.models import ClauseAnchor
print(ClauseAnchor.objects.filter(is_active=True).count())
PYEOF
)

if [ "$ANCHOR_COUNT" = "14" ]; then
    echo -e "${GREEN}✓${NC}"
    echo "  Found: $ANCHOR_COUNT anchor clauses"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    echo "  Expected 14, found: $ANCHOR_COUNT"
    ((TESTS_FAILED++))
fi

if [ ! -z "$TASK_ID" ]; then
    echo -ne "${CYAN}Checking draft task in database...${NC} "
    
    TASK_EXISTS=$(python3 << PYEOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()
from ai.models import DraftGenerationTask
task = DraftGenerationTask.objects.filter(id='$TASK_ID').first()
print("1" if task else "0")
PYEOF
)
    
    if [ "$TASK_EXISTS" = "1" ]; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
    fi
fi

# ============================================================================
# SUMMARY
# ============================================================================

print_section "TEST SUMMARY"

TOTAL=$((TESTS_PASSED + TESTS_FAILED))
PASS_RATE=$((TESTS_PASSED * 100 / TOTAL))

echo "Total Tests: $TOTAL"
echo "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo "Failed: ${RED}$TESTS_FAILED${NC}"
echo "Pass Rate: ${CYAN}$PASS_RATE%${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED - PRODUCTION READY${NC}"
    echo ""
else
    echo -e "${RED}✗ SOME TESTS FAILED - REVIEW REQUIRED${NC}"
    echo ""
fi

# ============================================================================
# NEXT STEPS
# ============================================================================

print_section "NEXT STEPS"

echo "1. Start Celery Worker for Draft Generation:"
echo "   ${CYAN}celery -A clm_backend worker -l info${NC}"
echo ""

echo "2. Test Full Draft Generation Workflow:"
echo "   ${CYAN}curl -X POST http://localhost:11000/api/v1/ai/generate/draft/ \\${NC}"
echo "   ${CYAN}  -H 'Content-Type: application/json' \\${NC}"
echo "   ${CYAN}  -d '{ ... }' # See AI_ENDPOINTS_COMPLETE.md${NC}"
echo ""

echo "3. Upload Documents for Metadata Extraction:"
echo "   ${CYAN}POST /api/v1/documents/upload/${NC}"
echo ""

echo "4. Review Documentation:"
echo "   • AI_ENDPOINTS_COMPLETE.md - Full API reference"
echo "   • TEST_RESULTS_PRODUCTION.md - Detailed test report"
echo "   • AI_SETUP_DEPLOYMENT.md - Setup and deployment"
echo ""

echo "5. Production Deployment:"
echo "   ${CYAN}gunicorn -c gunicorn_config.py clm_backend.wsgi:application${NC}"
echo ""

echo -e "${BLUE}All endpoints available at: http://localhost:11000/api/v1/${NC}"
echo ""
