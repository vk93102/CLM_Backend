#!/bin/bash

# Complete CURL Commands Reference for CLM Backend Admin API
# Copy-paste ready commands for testing all endpoints

BASE_URL="http://localhost:8000/api"
ADMIN_EMAIL="rahuljha996886@gmail.com"
ADMIN_PASSWORD="Rahuljha@123"

echo "============================================================================"
echo "CLM BACKEND - ADMIN API CURL COMMANDS REFERENCE"
echo "============================================================================"
echo ""

# ============================================================================
# AUTHENTICATION
# ============================================================================
echo "STEP 1: GET AUTHENTICATION TOKEN"
echo "============================================================================"
echo ""
echo "Command to get auth token:"
echo ""

cat <<'EOF'
# Get Token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rahuljha996886@gmail.com",
    "password": "Rahuljha@123"
  }' | python -c "import sys, json; print(json.load(sys.stdin)['access'])")

echo "Token: $TOKEN"
EOF

echo ""
echo ""

# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================
echo "STEP 2: PUBLIC ENDPOINTS (No Authentication Required)"
echo "============================================================================"
echo ""

echo "2.1 - GET ALL ROLES"
echo "-------------------"
cat <<'EOF'
curl -s http://localhost:8000/api/roles/ | python -m json.tool

# or with jq (if installed)
curl -s http://localhost:8000/api/roles/ | jq
EOF
echo ""
echo ""

echo "2.2 - GET ALL PERMISSIONS"
echo "-------------------------"
cat <<'EOF'
curl -s http://localhost:8000/api/permissions/ | python -m json.tool

# or with jq
curl -s http://localhost:8000/api/permissions/ | jq
EOF
echo ""
echo ""

echo "2.3 - GET ALL USERS (Paginated)"
echo "--------------------------------"
cat <<'EOF'
# Get first 50 users
curl -s "http://localhost:8000/api/users/?limit=50&offset=0" | python -m json.tool

# Get next page
curl -s "http://localhost:8000/api/users/?limit=50&offset=50" | python -m json.tool

# Get first 10 users only
curl -s "http://localhost:8000/api/users/?limit=10&offset=0" | python -m json.tool
EOF
echo ""
echo ""

# ============================================================================
# ADMIN ENDPOINTS - WITH TOKEN
# ============================================================================
echo "STEP 3: ADMIN ENDPOINTS (Authentication Required)"
echo "============================================================================"
echo ""
echo "First, get the token and save it:"
echo ""
cat <<'EOF'
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rahuljha996886@gmail.com",
    "password": "Rahuljha@123"
  }' | python -c "import sys, json; print(json.load(sys.stdin)['access'])")
EOF
echo ""
echo "Then use the token in the following commands:"
echo ""
echo ""

echo "3.1 - ADMIN DASHBOARD"
echo "--------------------"
cat <<'EOF'
curl -s http://localhost:8000/api/admin/dashboard/ \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
EOF
echo ""
echo ""

echo "3.2 - ADMIN GET USERS (Paginated)"
echo "---------------------------------"
cat <<'EOF'
# Get first 20 users
curl -s "http://localhost:8000/api/admin/get_users/?limit=20&offset=0" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# Get next page
curl -s "http://localhost:8000/api/admin/get_users/?limit=20&offset=20" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# Get first 5 users
curl -s "http://localhost:8000/api/admin/get_users/?limit=5&offset=0" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
EOF
echo ""
echo ""

echo "3.3 - ADMIN GET ROLES"
echo "--------------------"
cat <<'EOF'
curl -s http://localhost:8000/api/admin/get_roles/ \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
EOF
echo ""
echo ""

echo "3.4 - ADMIN GET PERMISSIONS"
echo "---------------------------"
cat <<'EOF'
curl -s http://localhost:8000/api/admin/get_permissions/ \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
EOF
echo ""
echo ""

echo "3.5 - ADMIN GET TENANTS"
echo "----------------------"
cat <<'EOF'
curl -s http://localhost:8000/api/admin/get_tenants/ \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
EOF
echo ""
echo ""

echo "3.6 - ADMIN GET AUDIT LOGS (Paginated)"
echo "-------------------------------------"
cat <<'EOF'
# Get first 50 audit logs
curl -s "http://localhost:8000/api/admin/get_audit_logs/?limit=50&offset=0" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# Get next page
curl -s "http://localhost:8000/api/admin/get_audit_logs/?limit=50&offset=50" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# Get first 10 audit logs
curl -s "http://localhost:8000/api/admin/get_audit_logs/?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
EOF
echo ""
echo ""

echo "3.7 - ADMIN GET SLA RULES"
echo "------------------------"
cat <<'EOF'
curl -s http://localhost:8000/api/admin/get_sla_rules/ \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
EOF
echo ""
echo ""

echo "3.8 - ADMIN GET SLA BREACHES"
echo "----------------------------"
cat <<'EOF'
curl -s http://localhost:8000/api/admin/get_sla_breaches/ \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
EOF
echo ""
echo ""

# ============================================================================
# QUICK COMMAND EXAMPLES
# ============================================================================
echo "QUICK START - Copy Paste Ready"
echo "============================================================================"
echo ""
echo "Run all these commands in sequence:"
echo ""

cat <<'QUICKSTART'
#!/bin/bash

BASE_URL="http://localhost:8000/api"

echo "1. Getting authentication token..."
TOKEN=$(curl -s -X POST $BASE_URL/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rahuljha996886@gmail.com",
    "password": "Rahuljha@123"
  }' | python -c "import sys, json; print(json.load(sys.stdin)['access'])")

echo "Token: $TOKEN"
echo ""

echo "2. Testing public endpoints..."
echo "   - Roles:"
curl -s $BASE_URL/roles/ | python -m json.tool | head -15
echo ""

echo "   - Permissions:"
curl -s $BASE_URL/permissions/ | python -m json.tool | head -15
echo ""

echo "   - Users:"
curl -s "$BASE_URL/users/?limit=5" | python -m json.tool | head -30
echo ""

echo "3. Testing admin endpoints..."
echo "   - Dashboard:"
curl -s $BASE_URL/admin/dashboard/ \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool | head -30
echo ""

echo "   - Admin Users:"
curl -s "$BASE_URL/admin/get_users/?limit=5" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool | head -40
echo ""

echo "   - Admin Roles:"
curl -s $BASE_URL/admin/get_roles/ \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

echo "   - Admin Tenants:"
curl -s $BASE_URL/admin/get_tenants/ \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

echo "All endpoints tested!"
QUICKSTART

echo ""
echo ""

# ============================================================================
# TESTING WITH DIFFERENT CREDENTIALS
# ============================================================================
echo "TESTING WITH DIFFERENT USER ACCOUNTS"
echo "============================================================================"
echo ""

cat <<'EOF'
# Test with Admin User
curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clm.local",
    "password": "admin123"
  }' | python -m json.tool

# Test with Standard User
curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@clm.local",
    "password": "user123"
  }' | python -m json.tool

# Test with Another Standard User
curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.smith@clm.local",
    "password": "user123"
  }' | python -m json.tool
EOF

echo ""
echo ""

# ============================================================================
# ADVANCED TESTING
# ============================================================================
echo "ADVANCED TESTING OPTIONS"
echo "============================================================================"
echo ""

cat <<'EOF'
# 1. Test with response headers
curl -s -i http://localhost:8000/api/roles/ | head -20

# 2. Test with timing information
curl -s -w "\nTime: %{time_total}s\n" http://localhost:8000/api/roles/

# 3. Test and save response to file
curl -s http://localhost:8000/api/admin/dashboard/ \
  -H "Authorization: Bearer $TOKEN" > dashboard_response.json

# 4. Pretty print saved response
python -m json.tool < dashboard_response.json

# 5. Count users
curl -s "http://localhost:8000/api/users/?limit=1" \
  -H "Content-Type: application/json" | \
  python -c "import sys, json; print('Total Users:', json.load(sys.stdin)['total'])"

# 6. Count roles
curl -s http://localhost:8000/api/roles/ | \
  python -c "import sys, json; print('Total Roles:', json.load(sys.stdin)['count'])"

# 7. Check if endpoint is working (HTTP status code only)
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/roles/

# 8. Test with custom headers
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Custom-Header: test" \
  http://localhost:8000/api/admin/dashboard/ | python -m json.tool | head -20
EOF

echo ""
echo "============================================================================"
echo "Documentation saved to: CURL_COMMANDS_REFERENCE.md"
echo "============================================================================"
echo ""
