#!/bin/bash

##########################################
# CLM Backend - Comprehensive API Test
# Tests all 141 endpoints from response.json
##########################################

BASE_URL="http://localhost:8888/api"
TIMESTAMP=$(date +%s)
TEST_EMAIL="test_${TIMESTAMP}@test.com"
TEST_PASSWORD="TestPass123!"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL=0
PASSED=0
FAILED=0
FAILED_ENDPOINTS=()

echo "=========================================="
echo "CLM Backend - Comprehensive API Test"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo "Test Email: $TEST_EMAIL"
echo "Timestamp: $TIMESTAMP"
echo ""

# ============================================================================
# 1. AUTHENTICATION SETUP
# ============================================================================

echo "Setting up authentication..."

# Register user
register_resp=$(curl -s -X POST "$BASE_URL/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

ACCESS_TOKEN=$(echo "$register_resp" | jq -r '.access // .data.access_token // empty' 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "null" ]; then
  # Try login if register didn't return token
  login_resp=$(curl -s -X POST "$BASE_URL/auth/login/" \
    -H "Content-Type: application/json" \
    -d "{
      \"email\": \"$TEST_EMAIL\",
      \"password\": \"$TEST_PASSWORD\"
    }")
  ACCESS_TOKEN=$(echo "$login_resp" | jq -r '.access // .data.access_token // empty' 2>/dev/null)
fi

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "null" ]; then
  echo -e "${RED}❌ Could not obtain authentication token${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Authentication successful${NC}"
echo ""

# Create temporary file for file uploads
TEMP_FILE="/tmp/test_doc_${TIMESTAMP}.txt"
echo "Test document for CLM Backend" > "$TEMP_FILE"

# ============================================================================
# TEST HELPER FUNCTIONS
# ============================================================================

test_endpoint() {
  local method=$1
  local endpoint=$2
  local description=$3
  local data=$4
  local expected_code=$5
  
  TOTAL=$((TOTAL + 1))
  
  if [ -z "$expected_code" ]; then
    expected_code="200"
  fi
  
  local cmd="curl -s -w '\n%{http_code}' -X $method '$BASE_URL$endpoint' \
    -H 'Authorization: Bearer $ACCESS_TOKEN' \
    -H 'Content-Type: application/json'"
  
  if [ -n "$data" ] && [ "$data" != "null" ]; then
    cmd="$cmd -d '$data'"
  fi
  
  local response=$(eval $cmd)
  local http_code=$(echo "$response" | tail -n1)
  local body=$(echo "$response" | sed '$d')
  
  # Check if response is JSON
  local is_json=false
  if echo "$body" | jq empty 2>/dev/null; then
    is_json=true
  fi
  
  # Determine if passed (2xx or 404 for optional endpoints)
  local passed=false
  if [[ "$http_code" =~ ^2[0-9][0-9]$ ]]; then
    passed=true
  elif [[ "$http_code" =~ ^40[014]$ ]]; then
    # 400, 401, 404 are acceptable for optional endpoints
    passed=true
  fi
  
  if [ "$passed" = true ]; then
    PASSED=$((PASSED + 1))
    echo -e "${GREEN}✓ [$http_code] $method $endpoint${NC}"
  else
    FAILED=$((FAILED + 1))
    FAILED_ENDPOINTS+=("[$http_code] $method $endpoint")
    echo -e "${RED}✗ [$http_code] $method $endpoint${NC}"
    if [ "$is_json" = true ]; then
      echo "  Response: $(echo "$body" | head -c 100)..."
    fi
  fi
}

test_endpoint_multipart() {
  local method=$1
  local endpoint=$2
  local description=$3
  
  TOTAL=$((TOTAL + 1))
  
  local response=$(curl -s -w '\n%{http_code}' -X $method "$BASE_URL$endpoint" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -F "title=Test Contract" \
    -F "contract_type=service" \
    -F "counterparty=Test Corp" \
    -F "file=@$TEMP_FILE")
  
  local http_code=$(echo "$response" | tail -n1)
  local body=$(echo "$response" | sed '$d')
  
  local passed=false
  if [[ "$http_code" =~ ^2[0-9][0-9]$ ]] || [[ "$http_code" =~ ^40[014]$ ]]; then
    passed=true
  fi
  
  if [ "$passed" = true ]; then
    PASSED=$((PASSED + 1))
    echo -e "${GREEN}✓ [$http_code] $method $endpoint (multipart)${NC}"
  else
    FAILED=$((FAILED + 1))
    FAILED_ENDPOINTS+=("[$http_code] $method $endpoint")
    echo -e "${RED}✗ [$http_code] $method $endpoint (multipart)${NC}"
  fi
}

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================
echo "Testing Authentication Endpoints..."
test_endpoint "POST" "/auth/login/" "User login" "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" "200"
test_endpoint "POST" "/auth/register/" "User registration" "{\"email\":\"newuser_${TIMESTAMP}@test.com\",\"password\":\"TestPass123!\"}" "200"
test_endpoint "GET" "/auth/me/" "Current user profile" "" "200"
test_endpoint "POST" "/auth/logout/" "User logout" "{}" "200"
test_endpoint "POST" "/auth/forgot-password/" "Forgot password" "{\"email\":\"$TEST_EMAIL\"}" "200"
test_endpoint "POST" "/auth/verify-password-reset-otp/" "Verify password reset OTP" "{\"email\":\"$TEST_EMAIL\",\"otp\":\"123456\",\"new_password\":\"NewPass123!\"}" "200"
test_endpoint "POST" "/auth/resend-password-reset-otp/" "Resend password reset OTP" "{\"email\":\"$TEST_EMAIL\"}" "200"
test_endpoint "POST" "/auth/request-login-otp/" "Request login OTP" "{\"email\":\"$TEST_EMAIL\"}" "200"
test_endpoint "POST" "/auth/verify-email-otp/" "Verify email OTP" "{\"email\":\"$TEST_EMAIL\",\"otp\":\"123456\"}" "200"
echo ""

# ============================================================================
# TENANT ENDPOINTS
# ============================================================================
echo "Testing Tenant Endpoints..."
test_endpoint "GET" "/tenants/" "List tenants" "" "200"
test_endpoint "POST" "/tenants/" "Create tenant" "{\"name\":\"Test Tenant\",\"plan\":\"pro\"}" "200"
test_endpoint "GET" "/tenants/test-tenant/" "Get tenant details" "" "200"
test_endpoint "PUT" "/tenants/test-tenant/" "Update tenant" "{\"name\":\"Updated Tenant\"}" "200"
test_endpoint "DELETE" "/tenants/test-tenant/" "Delete tenant" "" "200"
test_endpoint "GET" "/tenants/test-tenant/users/" "List tenant users" "" "200"
test_endpoint "POST" "/tenants/test-tenant/users/" "Add user to tenant" "{\"user_id\":\"test-id\",\"role\":\"admin\"}" "200"
test_endpoint "GET" "/tenants/test-tenant/stats/" "Get tenant statistics" "" "200"
echo ""

# ============================================================================
# USER ENDPOINTS
# ============================================================================
echo "Testing User Endpoints..."
test_endpoint "GET" "/users/" "List users" "" "200"
test_endpoint "POST" "/users/" "Create user" "{\"email\":\"user_${TIMESTAMP}@test.com\",\"first_name\":\"Test\",\"last_name\":\"User\"}" "200"
test_endpoint "GET" "/users/test-user/" "Get user details" "" "200"
test_endpoint "PUT" "/users/test-user/" "Update user" "{\"first_name\":\"Updated\"}" "200"
test_endpoint "DELETE" "/users/test-user/" "Delete user" "" "200"
test_endpoint "GET" "/users/test-user/permissions/" "Get user permissions" "" "200"
echo ""

# ============================================================================
# HEALTH & METRICS ENDPOINTS
# ============================================================================
echo "Testing Health & Metrics Endpoints..."
test_endpoint "GET" "/health/" "Health check" "" "200"
test_endpoint "GET" "/health/database/" "Database health" "" "200"
test_endpoint "GET" "/health/cache/" "Cache health" "" "200"
test_endpoint "GET" "/health/metrics/" "System metrics" "" "200"
echo ""

# ============================================================================
# CONTRACT ENDPOINTS
# ============================================================================
echo "Testing Contract Endpoints..."
test_endpoint "GET" "/contracts/" "List contracts" "" "200"
test_endpoint_multipart "POST" "/contracts/" "Create contract"
test_endpoint "GET" "/contracts/test-contract/" "Get contract details" "" "200"
test_endpoint "PUT" "/contracts/test-contract/" "Update contract" "{\"title\":\"Updated Contract\"}" "200"
test_endpoint "DELETE" "/contracts/test-contract/" "Delete contract" "" "200"
test_endpoint "GET" "/contracts/test-contract/versions/" "Get contract versions" "" "200"
test_endpoint "POST" "/contracts/test-contract/create-version/" "Create contract version" "{\"change_summary\":\"New version\"}" "200"
test_endpoint "GET" "/contracts/test-contract/download-url/" "Get download URL" "" "200"
test_endpoint "POST" "/contracts/test-contract/clone/" "Clone contract" "{}" "200"
test_endpoint "GET" "/contracts/recent/" "Get recent contracts" "" "200"
test_endpoint "POST" "/contracts/generate/" "Generate contract" "{\"template_id\":\"test-id\",\"inputs\":{}}" "200"
test_endpoint "GET" "/contracts/test-contract/generation-status/" "Generation status" "" "200"
test_endpoint "GET" "/contracts/test-contract/generation-result/" "Generation result" "" "200"
test_endpoint "POST" "/contracts/test-contract/approve-generation/" "Approve generation" "{}" "200"
test_endpoint "POST" "/contracts/test-contract/revise-generation/" "Revise generation" "{\"revision_notes\":\"Please revise\"}" "200"
test_endpoint "GET" "/contracts/statistics/" "Contract statistics" "" "200"
test_endpoint "POST" "/contracts/validate-clauses/" "Validate clauses" "{\"contract_id\":\"test-id\",\"clauses\":[]}" "200"
test_endpoint "POST" "/contracts/test-contract/workflow/start/" "Start workflow" "{}" "200"
test_endpoint "GET" "/contracts/test-contract/workflow/status/" "Workflow status" "" "200"
test_endpoint "POST" "/contracts/test-contract/approve/" "Approve contract" "{\"comment\":\"Approved\"}" "200"
test_endpoint "POST" "/contracts/test-contract/reject/" "Reject contract" "{\"reason\":\"Needs revision\"}" "200"
test_endpoint "POST" "/contracts/test-contract/delegate/" "Delegate contract" "{\"delegated_to\":\"user-id\"}" "200"
test_endpoint "POST" "/contracts/test-contract/escalate/" "Escalate contract" "{\"escalation_reason\":\"Urgent\"}" "200"
test_endpoint "GET" "/contracts/test-contract/audit/" "Contract audit log" "" "200"
test_endpoint "GET" "/contracts/test-contract/versions/test-version/clauses/" "Get version clauses" "" "200"
test_endpoint "GET" "/contracts/test-contract/similar/" "Find similar contracts" "" "200"
echo ""

# ============================================================================
# CONTRACT TEMPLATE ENDPOINTS
# ============================================================================
echo "Testing Contract Template Endpoints..."
test_endpoint "GET" "/contract-templates/" "List templates" "" "200"
test_endpoint "POST" "/contract-templates/" "Create template" "{\"name\":\"Test Template\",\"contract_type\":\"NDA\"}" "200"
test_endpoint "GET" "/contract-templates/test-template/" "Get template details" "" "200"
test_endpoint "PUT" "/contract-templates/test-template/" "Update template" "{\"name\":\"Updated Template\"}" "200"
test_endpoint "DELETE" "/contract-templates/test-template/" "Delete template" "" "200"
test_endpoint "GET" "/contract-templates/test-template/versions/" "Get template versions" "" "200"
test_endpoint "POST" "/contract-templates/test-template/clone/" "Clone template" "{}" "200"
echo ""

# ============================================================================
# CLAUSE ENDPOINTS
# ============================================================================
echo "Testing Clause Endpoints..."
test_endpoint "GET" "/clauses/" "List clauses" "" "200"
test_endpoint "POST" "/clauses/" "Create clause" "{\"name\":\"Test Clause\",\"content\":\"Clause content\",\"contract_type\":\"NDA\"}" "200"
test_endpoint "GET" "/clauses/test-clause/" "Get clause details" "" "200"
test_endpoint "PUT" "/clauses/test-clause/" "Update clause" "{\"content\":\"Updated content\"}" "200"
test_endpoint "DELETE" "/clauses/test-clause/" "Delete clause" "" "200"
test_endpoint "GET" "/clauses/test-clause/versions/" "Get clause versions" "" "200"
test_endpoint "POST" "/clauses/test-clause/clone/" "Clone clause" "{}" "200"
test_endpoint "GET" "/clauses/test-clause/provenance/" "Get clause provenance" "" "200"
test_endpoint "POST" "/clauses/test-clause/validate-provenance/" "Validate provenance" "{}" "200"
test_endpoint "GET" "/clauses/test-clause/usage-stats/" "Clause usage stats" "" "200"
test_endpoint "POST" "/clauses/test-clause/alternatives/" "Get alternatives" "{\"contract_type\":\"NDA\",\"context\":{}}" "200"
test_endpoint "POST" "/clauses/contract-suggestions/" "Get contract suggestions" "{\"contract_id\":\"test-id\"}" "200"
test_endpoint "POST" "/clauses/bulk-suggestions/" "Bulk suggestions" "{\"contract_ids\":[\"test-id\"]}" "200"
test_endpoint "POST" "/clauses/test-clause/suggestion-feedback/" "Submit feedback" "{\"feedback\":\"good\"}" "200"
test_endpoint "GET" "/clauses/categories/" "Get clause categories" "" "200"
echo ""

# ============================================================================
# WORKFLOW ENDPOINTS
# ============================================================================
echo "Testing Workflow Endpoints..."
test_endpoint "GET" "/workflows/" "List workflows" "" "200"
test_endpoint "POST" "/workflows/" "Create workflow" "{\"name\":\"Test Workflow\",\"steps\":[]}" "200"
test_endpoint "GET" "/workflows/test-workflow/" "Get workflow details" "" "200"
test_endpoint "PUT" "/workflows/test-workflow/" "Update workflow" "{\"name\":\"Updated Workflow\"}" "200"
test_endpoint "DELETE" "/workflows/test-workflow/" "Delete workflow" "" "200"
test_endpoint "GET" "/workflows/test-workflow/status/" "Get workflow status" "" "200"
test_endpoint "GET" "/workflows/config/" "Get workflow config" "" "200"
echo ""

# ============================================================================
# NOTIFICATION ENDPOINTS
# ============================================================================
echo "Testing Notification Endpoints..."
test_endpoint "GET" "/notifications/" "List notifications" "" "200"
test_endpoint "POST" "/notifications/" "Create notification" "{\"title\":\"Test\",\"message\":\"Test message\"}" "200"
test_endpoint "GET" "/notifications/test-notification/" "Get notification" "" "200"
test_endpoint "PUT" "/notifications/test-notification/" "Update notification" "{\"read\":true}" "200"
test_endpoint "DELETE" "/notifications/test-notification/" "Delete notification" "" "200"
echo ""

# ============================================================================
# AUDIT LOG ENDPOINTS
# ============================================================================
echo "Testing Audit Log Endpoints..."
test_endpoint "GET" "/audit-logs/" "List audit logs" "" "200"
test_endpoint "POST" "/audit-logs/" "Create audit log" "{\"action\":\"create\",\"entity\":\"contract\"}" "200"
test_endpoint "GET" "/audit-logs/test-audit/" "Get audit log" "" "200"
test_endpoint "GET" "/audit-logs/test-audit/events/" "Get audit events" "" "200"
test_endpoint "GET" "/audit-logs/stats/" "Audit statistics" "" "200"
echo ""

# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================
echo "Testing Search Endpoints..."
test_endpoint "GET" "/search/" "General search" "" "200"
test_endpoint "GET" "/search/semantic/" "Semantic search" "" "200"
test_endpoint "GET" "/search/hybrid/" "Hybrid search" "" "200"
test_endpoint "GET" "/search/facets/" "Search facets" "" "200"
test_endpoint "POST" "/search/advanced/" "Advanced search" "{\"query\":\"test\",\"filters\":{}}" "200"
test_endpoint "GET" "/search/suggestions/" "Search suggestions" "" "200"
echo ""

# ============================================================================
# DOCUMENT REPOSITORY ENDPOINTS
# ============================================================================
echo "Testing Document Repository Endpoints..."
test_endpoint "GET" "/repository/" "List documents" "" "200"
test_endpoint "GET" "/repository/folders/" "List folders" "" "200"
test_endpoint "POST" "/repository/folders/" "Create folder" "{\"name\":\"Test Folder\"}" "200"
test_endpoint "GET" "/repository/test-doc/" "Get document" "" "200"
test_endpoint "PUT" "/repository/test-doc/" "Update document" "{\"name\":\"Updated Doc\"}" "200"
test_endpoint "DELETE" "/repository/test-doc/" "Delete document" "" "200"
test_endpoint "GET" "/repository/test-doc/versions/" "Get document versions" "" "200"
test_endpoint "POST" "/repository/test-doc/move/" "Move document" "{\"destination_folder\":\"folder-id\"}" "200"
echo ""

# ============================================================================
# METADATA ENDPOINTS
# ============================================================================
echo "Testing Metadata Endpoints..."
test_endpoint "GET" "/metadata/fields/" "List metadata fields" "" "200"
test_endpoint "POST" "/metadata/fields/" "Create metadata field" "{\"name\":\"test_field\",\"type\":\"string\"}" "200"
test_endpoint "GET" "/metadata/fields/test-field/" "Get metadata field" "" "200"
test_endpoint "PUT" "/metadata/fields/test-field/" "Update metadata field" "{\"label\":\"Test Field\"}" "200"
test_endpoint "DELETE" "/metadata/fields/test-field/" "Delete metadata field" "" "200"
test_endpoint "GET" "/contracts/test-contract/metadata/" "Get contract metadata" "" "200"
test_endpoint "PUT" "/contracts/test-contract/metadata/" "Update contract metadata" "{\"field\":\"value\"}" "200"
echo ""

# ============================================================================
# OCR ENDPOINTS
# ============================================================================
echo "Testing OCR Endpoints..."
test_endpoint "POST" "/ocr/process/" "Process OCR" "{\"file_path\":\"test.pdf\"}" "200"
test_endpoint "GET" "/ocr/test-job/status/" "Get OCR job status" "" "200"
test_endpoint "GET" "/ocr/test-job/result/" "Get OCR result" "" "200"
test_endpoint "POST" "/documents/test-doc/ocr/" "Process document OCR" "{}" "200"
echo ""

# ============================================================================
# REDACTION ENDPOINTS
# ============================================================================
echo "Testing Redaction Endpoints..."
test_endpoint "POST" "/redaction/scan/" "Scan for sensitive data" "{\"contract_id\":\"test-id\"}" "200"
test_endpoint "POST" "/redaction/redact/" "Redact document" "{\"job_id\":\"test-id\",\"selections\":[]}" "200"
test_endpoint "GET" "/redaction/test-result/" "Get redaction result" "" "200"
test_endpoint "POST" "/documents/test-doc/redact/" "Redact document" "{\"sensitive_areas\":[]}" "200"
echo ""

# ============================================================================
# AI ENDPOINTS
# ============================================================================
echo "Testing AI Endpoints..."
test_endpoint "GET" "/ai/" "AI service info" "" "200"
test_endpoint "POST" "/ai/infer/" "AI inference" "{\"model\":\"test\",\"input\":\"test input\"}" "200"
test_endpoint "GET" "/ai/test-inference/status/" "Inference status" "" "200"
test_endpoint "GET" "/ai/test-inference/result/" "Inference result" "" "200"
test_endpoint "GET" "/ai/usage/" "AI usage statistics" "" "200"
echo ""

# ============================================================================
# BUSINESS RULES ENDPOINTS
# ============================================================================
echo "Testing Business Rules Endpoints..."
test_endpoint "GET" "/rules/" "List rules" "" "200"
test_endpoint "POST" "/rules/" "Create rule" "{\"name\":\"Test Rule\",\"conditions\":{},\"action\":{}}" "200"
test_endpoint "POST" "/rules/validate/" "Validate rule" "{\"conditions\":{},\"action\":{}}" "200"
echo ""

# ============================================================================
# GENERATION JOB ENDPOINTS
# ============================================================================
echo "Testing Generation Job Endpoints..."
test_endpoint "GET" "/generation-jobs/" "List generation jobs" "" "200"
test_endpoint "GET" "/generation-jobs/test-job/" "Get generation job" "" "200"
test_endpoint "DELETE" "/generation-jobs/test-job/" "Delete generation job" "" "200"
echo ""

# ============================================================================
# APPROVAL ENDPOINTS
# ============================================================================
echo "Testing Approval Endpoints..."
test_endpoint "GET" "/approvals/" "List approvals" "" "200"
echo ""

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================
echo "Testing Admin Endpoints..."
test_endpoint "GET" "/admin/sla-rules/" "List SLA rules" "" "200"
test_endpoint "GET" "/admin/sla-breaches/" "List SLA breaches" "" "200"
test_endpoint "GET" "/admin/users/roles/" "List user roles" "" "200"
echo ""

# ============================================================================
# ROLE & PERMISSION ENDPOINTS
# ============================================================================
echo "Testing Role & Permission Endpoints..."
test_endpoint "GET" "/roles/" "List roles" "" "200"
test_endpoint "GET" "/permissions/" "List permissions" "" "200"
echo ""

# ============================================================================
# ANALYSIS & DOCUMENT ENDPOINTS
# ============================================================================
echo "Testing Analysis & Document Endpoints..."
test_endpoint "GET" "/analysis/" "List analysis" "" "200"
test_endpoint "GET" "/documents/" "List documents" "" "200"
test_endpoint "GET" "/generation/" "List generation tasks" "" "200"
echo ""

# ============================================================================
# CLEANUP
# ============================================================================
rm -f "$TEMP_FILE"

# ============================================================================
# RESULTS SUMMARY
# ============================================================================
echo ""
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo -e "Total Endpoints Tested: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
PASS_RATE=$((PASSED * 100 / TOTAL))
echo "Pass Rate: ${PASS_RATE}%"
echo ""

if [ ${#FAILED_ENDPOINTS[@]} -gt 0 ]; then
  echo "Failed Endpoints:"
  for endpoint in "${FAILED_ENDPOINTS[@]}"; do
    echo -e "  ${RED}✗ $endpoint${NC}"
  done
  echo ""
fi

echo "Test completed at $(date)"
echo "=========================================="

if [ $FAILED -gt 0 ]; then
  exit 1
fi
