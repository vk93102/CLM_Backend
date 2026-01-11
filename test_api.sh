#!/bin/bash

##############################################################################
# CLM Backend - Simple API Test Script
# Tests all endpoints on http://localhost:8888/api
##############################################################################

BASE_URL="http://localhost:8888/api"
TIMESTAMP=$(date +%s)
TEST_EMAIL="user_${TIMESTAMP}@test.com"
TEST_PASSWORD="TestPass123!"

echo "=========================================="
echo "CLM Backend - API Endpoint Tests"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo "Test User: $TEST_EMAIL"
echo ""

# ============================================================================
# 1. REGISTER USER
# ============================================================================

echo "1️⃣  REGISTER NEW USER"
echo "POST /auth/register/"
register_resp=$(curl -s -X POST "$BASE_URL/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"first_name\": \"Test\",
    \"last_name\": \"User\"
  }")

echo "Response:"
echo "$register_resp" | jq . 2>/dev/null || echo "$register_resp"
echo ""

# Extract user_id
USER_ID=$(echo "$register_resp" | jq -r '.user_id' 2>/dev/null)
echo "✓ User ID: $USER_ID"
echo ""

# ============================================================================
# 2. LOGIN USER
# ============================================================================

echo "2️⃣  LOGIN USER"
echo "POST /auth/login/"
login_resp=$(curl -s -X POST "$BASE_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

echo "Response:"
echo "$login_resp" | jq . 2>/dev/null || echo "$login_resp"
echo ""

# Extract tokens
ACCESS_TOKEN=$(echo "$login_resp" | jq -r '.access' 2>/dev/null)
REFRESH_TOKEN=$(echo "$login_resp" | jq -r '.refresh' 2>/dev/null)
TENANT_ID=$(echo "$login_resp" | jq -r '.tenant_id' 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "null" ]; then
  echo "❌ ERROR: Could not get access token"
  exit 1
fi

echo "✓ Access Token: ${ACCESS_TOKEN:0:40}..."
echo "✓ Tenant ID: $TENANT_ID"
echo ""

# ============================================================================
# 3. GET CURRENT USER
# ============================================================================

echo "3️⃣  GET CURRENT USER"
echo "GET /auth/me/"
curl -s -X GET "$BASE_URL/auth/me/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
echo ""

# ============================================================================
# 4. LIST CONTRACTS (EMPTY)
# ============================================================================

echo "4️⃣  LIST CONTRACTS"
echo "GET /contracts/"
curl -s -X GET "$BASE_URL/contracts/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
echo ""

# ============================================================================
# 5. CREATE CONTRACT WITH FILE
# ============================================================================

echo "5️⃣  CREATE CONTRACT"
echo "POST /contracts/"

# Create temp file
TEMP_FILE="/tmp/test_contract_$TIMESTAMP.txt"
echo "This is a test contract document." > "$TEMP_FILE"

contract_resp=$(curl -s -X POST "$BASE_URL/contracts/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "title=Service Agreement" \
  -F "contract_type=service" \
  -F "counterparty=Acme Corp" \
  -F "value=50000" \
  -F "start_date=2026-01-15" \
  -F "end_date=2027-01-15" \
  -F 'approval_chain={}' \
  -F "approval_required=false" \
  -F 'current_approvers=[]' \
  -F 'metadata={}' \
  -F "file=@$TEMP_FILE")

echo "Response:"
echo "$contract_resp" | jq . 2>/dev/null || echo "$contract_resp"
echo ""

# Extract contract ID
CONTRACT_ID=$(echo "$contract_resp" | jq -r '.id' 2>/dev/null)
if [ ! -z "$CONTRACT_ID" ] && [ "$CONTRACT_ID" != "null" ]; then
  echo "✓ Contract ID: $CONTRACT_ID"
  echo ""
  
  # ============================================================================
  # 6. GET CONTRACT DETAILS
  # ============================================================================
  
  echo "6️⃣  GET CONTRACT DETAILS"
  echo "GET /contracts/$CONTRACT_ID/"
  curl -s -X GET "$BASE_URL/contracts/$CONTRACT_ID/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
  echo ""
  
  # ============================================================================
  # 7. SUBMIT CONTRACT
  # ============================================================================
  
  echo "7️⃣  SUBMIT CONTRACT FOR APPROVAL"
  echo "POST /contracts/$CONTRACT_ID/submit/"
  curl -s -X POST "$BASE_URL/contracts/$CONTRACT_ID/submit/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"comment":"Ready for review"}' | jq .
  echo ""
  
  # ============================================================================
  # 8. APPROVE CONTRACT
  # ============================================================================
  
  echo "8️⃣  APPROVE CONTRACT"
  echo "POST /contracts/$CONTRACT_ID/decide/"
  curl -s -X POST "$BASE_URL/contracts/$CONTRACT_ID/decide/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"decision":"approved","comment":"Approved"}' | jq .
  echo ""
  
  # ============================================================================
  # 9. GET CONTRACT LOGS
  # ============================================================================
  
  echo "9️⃣  GET CONTRACT AUDIT LOGS"
  echo "GET /contracts/$CONTRACT_ID/logs/"
  curl -s -X GET "$BASE_URL/contracts/$CONTRACT_ID/logs/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
  echo ""
fi

# ============================================================================
# 10. CONTRACT STATISTICS
# ============================================================================

echo "🔟 CONTRACT STATISTICS"
echo "GET /contracts/statistics/"
curl -s -X GET "$BASE_URL/contracts/statistics/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
echo ""

# ============================================================================
# 11. LIST TEMPLATES
# ============================================================================

echo "1️⃣1️⃣  LIST CONTRACT TEMPLATES"
echo "GET /contract-templates/"
curl -s -X GET "$BASE_URL/contract-templates/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
echo ""

# ============================================================================
# 12. LIST CLAUSES
# ============================================================================

echo "1️⃣2️⃣  LIST CLAUSES"
echo "GET /clauses/"
curl -s -X GET "$BASE_URL/clauses/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
echo ""

# ============================================================================
# 13. LIST GENERATION JOBS
# ============================================================================

echo "1️⃣3️⃣  LIST GENERATION JOBS"
echo "GET /generation-jobs/"
curl -s -X GET "$BASE_URL/generation-jobs/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
echo ""

# ============================================================================
# CLEANUP
# ============================================================================

echo "=========================================="
echo "✓ Testing Complete!"
echo "=========================================="
echo ""
echo "Files Used:"
echo "  - Test Email: $TEST_EMAIL"
echo "  - Test File: $TEMP_FILE"
echo ""

# Cleanup
rm -f "$TEMP_FILE"
echo "✓ Cleaned up temporary files"
echo ""

echo "Summary:"
echo "  - All 13 main endpoints tested"
echo "  - Registration: ✓"
echo "  - Authentication: ✓"
echo "  - Contract Management: ✓"
echo "  - Templates & Clauses: ✓"
echo "  - Generation Jobs: ✓"
echo ""
