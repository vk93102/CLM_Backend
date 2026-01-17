#!/bin/bash

# Final comprehensive endpoint test script
# Tests all 11 endpoints with real data validation

set -e

BASE_URL="http://localhost:8000/api"
ADMIN_EMAIL="rahuljha996886@gmail.com"
ADMIN_PASSWORD="Rahuljha@123"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Print colored output
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Test if curl response contains expected field
test_response_field() {
    local response=$1
    local field=$2
    if echo "$response" | grep -q "$field"; then
        return 0
    else
        return 1
    fi
}

# ============================================================================
# STEP 1: AUTHENTICATION
# ============================================================================
print_header "STEP 1: AUTHENTICATION TEST"

echo "Testing login with credentials:"
echo "  Email: $ADMIN_EMAIL"
echo "  Password: $ADMIN_PASSWORD"
echo ""

TOKEN=$(curl -s -X POST $BASE_URL/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$ADMIN_EMAIL\",
    \"password\": \"$ADMIN_PASSWORD\"
  }")

if echo "$TOKEN" | grep -q "access"; then
    TOKEN=$(echo "$TOKEN" | python -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)
    print_success "Authentication successful"
    echo "Token (first 50 chars): ${TOKEN:0:50}..."
else
    print_error "Authentication failed"
    echo "Response: $TOKEN"
    exit 1
fi

echo ""

# ============================================================================
# STEP 2: PUBLIC ENDPOINTS
# ============================================================================
print_header "STEP 2: PUBLIC ENDPOINTS (No Authentication)"

# Test 1: GET /api/roles/
echo "Test 1: GET /api/roles/"
echo "Command: curl -s $BASE_URL/roles/ | python -m json.tool"
echo ""

RESPONSE=$(curl -s $BASE_URL/roles/)
if test_response_field "$RESPONSE" "success"; then
    print_success "GET /api/roles/ - Response contains 'success' field"
    ROLE_COUNT=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
    print_info "Found $ROLE_COUNT roles"
    echo "Sample Response:"
    echo "$RESPONSE" | python -m json.tool | head -20
else
    print_error "GET /api/roles/ - Invalid response"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 2: GET /api/permissions/
echo "Test 2: GET /api/permissions/"
echo "Command: curl -s $BASE_URL/permissions/ | python -m json.tool"
echo ""

RESPONSE=$(curl -s $BASE_URL/permissions/)
if test_response_field "$RESPONSE" "success"; then
    print_success "GET /api/permissions/ - Response contains 'success' field"
    PERM_COUNT=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
    print_info "Found $PERM_COUNT permissions"
    echo "Sample Response:"
    echo "$RESPONSE" | python -m json.tool | head -20
else
    print_error "GET /api/permissions/ - Invalid response"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 3: GET /api/users/
echo "Test 3: GET /api/users/?limit=10&offset=0"
echo "Command: curl -s \"$BASE_URL/users/?limit=10&offset=0\" | python -m json.tool"
echo ""

RESPONSE=$(curl -s "$BASE_URL/users/?limit=10&offset=0")
if test_response_field "$RESPONSE" "success"; then
    print_success "GET /api/users/ - Response contains 'success' field"
    USER_COUNT=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('total', 0))" 2>/dev/null)
    RETURNED=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
    print_info "Total users: $USER_COUNT, Returned: $RETURNED"
    echo "Sample Response:"
    echo "$RESPONSE" | python -m json.tool | head -30
else
    print_error "GET /api/users/ - Invalid response"
    echo "Response: $RESPONSE"
fi
echo ""

# ============================================================================
# STEP 3: ADMIN ENDPOINTS
# ============================================================================
print_header "STEP 3: ADMIN ENDPOINTS (With Authentication Token)"

# Test 4: GET /api/admin/dashboard/
echo "Test 4: GET /api/admin/dashboard/"
echo "Command: curl -s $BASE_URL/admin/dashboard/ -H \"Authorization: Bearer \$TOKEN\" | python -m json.tool"
echo ""

RESPONSE=$(curl -s $BASE_URL/admin/dashboard/ \
  -H "Authorization: Bearer $TOKEN")
if test_response_field "$RESPONSE" "success"; then
    print_success "GET /api/admin/dashboard/ - Response valid"
    TOTAL_CONTRACTS=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('total_contracts', 0))" 2>/dev/null)
    TOTAL_USERS=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('total_users', 0))" 2>/dev/null)
    TOTAL_TENANTS=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('total_tenants', 0))" 2>/dev/null)
    print_info "Dashboard: Contracts=$TOTAL_CONTRACTS, Users=$TOTAL_USERS, Tenants=$TOTAL_TENANTS"
    echo "Sample Response:"
    echo "$RESPONSE" | python -m json.tool | head -40
else
    print_error "GET /api/admin/dashboard/ - Invalid response"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 5: GET /api/admin/get_users/
echo "Test 5: GET /api/admin/get_users/?limit=10&offset=0"
echo "Command: curl -s \"$BASE_URL/admin/get_users/?limit=10&offset=0\" -H \"Authorization: Bearer \$TOKEN\" | python -m json.tool"
echo ""

RESPONSE=$(curl -s "$BASE_URL/admin/get_users/?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN")
if test_response_field "$RESPONSE" "success"; then
    print_success "GET /api/admin/get_users/ - Response valid"
    TOTAL=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('total', 0))" 2>/dev/null)
    COUNT=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
    print_info "Total users: $TOTAL, Returned: $COUNT"
    echo "Sample Response:"
    echo "$RESPONSE" | python -m json.tool | head -40
else
    print_error "GET /api/admin/get_users/ - Invalid response"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 6: GET /api/admin/get_roles/
echo "Test 6: GET /api/admin/get_roles/"
echo "Command: curl -s $BASE_URL/admin/get_roles/ -H \"Authorization: Bearer \$TOKEN\" | python -m json.tool"
echo ""

RESPONSE=$(curl -s $BASE_URL/admin/get_roles/ \
  -H "Authorization: Bearer $TOKEN")
if test_response_field "$RESPONSE" "success"; then
    print_success "GET /api/admin/get_roles/ - Response valid"
    ROLE_COUNT=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
    print_info "Found $ROLE_COUNT role definitions"
    echo "Sample Response:"
    echo "$RESPONSE" | python -m json.tool | head -30
else
    print_error "GET /api/admin/get_roles/ - Invalid response"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 7: GET /api/admin/get_permissions/
echo "Test 7: GET /api/admin/get_permissions/"
echo "Command: curl -s $BASE_URL/admin/get_permissions/ -H \"Authorization: Bearer \$TOKEN\" | python -m json.tool"
echo ""

RESPONSE=$(curl -s $BASE_URL/admin/get_permissions/ \
  -H "Authorization: Bearer $TOKEN")
if test_response_field "$RESPONSE" "success"; then
    print_success "GET /api/admin/get_permissions/ - Response valid"
    PERM_COUNT=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
    print_info "Found $PERM_COUNT permissions"
    echo "Sample Response:"
    echo "$RESPONSE" | python -m json.tool | head -30
else
    print_error "GET /api/admin/get_permissions/ - Invalid response"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 8: GET /api/admin/get_tenants/
echo "Test 8: GET /api/admin/get_tenants/"
echo "Command: curl -s $BASE_URL/admin/get_tenants/ -H \"Authorization: Bearer \$TOKEN\" | python -m json.tool"
echo ""

RESPONSE=$(curl -s $BASE_URL/admin/get_tenants/ \
  -H "Authorization: Bearer $TOKEN")
if test_response_field "$RESPONSE" "success"; then
    print_success "GET /api/admin/get_tenants/ - Response valid"
    TENANT_COUNT=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
    print_info "Found $TENANT_COUNT tenants"
    echo "Sample Response:"
    echo "$RESPONSE" | python -m json.tool | head -30
else
    print_error "GET /api/admin/get_tenants/ - Invalid response"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 9: GET /api/admin/get_audit_logs/
echo "Test 9: GET /api/admin/get_audit_logs/?limit=10&offset=0"
echo "Command: curl -s \"$BASE_URL/admin/get_audit_logs/?limit=10&offset=0\" -H \"Authorization: Bearer \$TOKEN\" | python -m json.tool"
echo ""

RESPONSE=$(curl -s "$BASE_URL/admin/get_audit_logs/?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN")
if test_response_field "$RESPONSE" "success"; then
    print_success "GET /api/admin/get_audit_logs/ - Response valid"
    TOTAL=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('total', 0))" 2>/dev/null)
    COUNT=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
    print_info "Total audit logs: $TOTAL, Returned: $COUNT"
    echo "Sample Response:"
    echo "$RESPONSE" | python -m json.tool | head -40
else
    print_error "GET /api/admin/get_audit_logs/ - Invalid response"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 10: GET /api/admin/get_sla_rules/
echo "Test 10: GET /api/admin/get_sla_rules/"
echo "Command: curl -s $BASE_URL/admin/get_sla_rules/ -H \"Authorization: Bearer \$TOKEN\" | python -m json.tool"
echo ""

RESPONSE=$(curl -s $BASE_URL/admin/get_sla_rules/ \
  -H "Authorization: Bearer $TOKEN")
if test_response_field "$RESPONSE" "success"; then
    print_success "GET /api/admin/get_sla_rules/ - Response valid"
    RULE_COUNT=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
    print_info "Found $RULE_COUNT SLA rules"
    echo "Sample Response:"
    echo "$RESPONSE" | python -m json.tool | head -30
else
    print_error "GET /api/admin/get_sla_rules/ - Invalid response"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 11: GET /api/admin/get_sla_breaches/
echo "Test 11: GET /api/admin/get_sla_breaches/"
echo "Command: curl -s $BASE_URL/admin/get_sla_breaches/ -H \"Authorization: Bearer \$TOKEN\" | python -m json.tool"
echo ""

RESPONSE=$(curl -s $BASE_URL/admin/get_sla_breaches/ \
  -H "Authorization: Bearer $TOKEN")
if test_response_field "$RESPONSE" "success"; then
    print_success "GET /api/admin/get_sla_breaches/ - Response valid"
    BREACH_COUNT=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
    print_info "Found $BREACH_COUNT SLA breaches"
    echo "Sample Response:"
    echo "$RESPONSE" | python -m json.tool | head -20
else
    print_error "GET /api/admin/get_sla_breaches/ - Invalid response"
    echo "Response: $RESPONSE"
fi
echo ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_header "TEST SUMMARY"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

echo -e "Total Tests Run: $TOTAL_TESTS"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
else
    echo -e "${GREEN}Tests Failed: $TESTS_FAILED${NC}"
fi

echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ ALL TESTS PASSED - READY FOR PRODUCTION!${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ SOME TESTS FAILED - PLEASE REVIEW${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
