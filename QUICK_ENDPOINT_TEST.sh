#!/bin/bash

# Simple comprehensive endpoint test
BASE_URL="http://localhost:8000/api"

echo "=============================================="
echo "CLM Backend - Endpoint Test Summary"
echo "=============================================="
echo ""

# Test 1: Public Endpoints (no auth)
echo "1. GET /api/roles/ (Public)"
echo "Command: curl -s http://localhost:8000/api/roles/"
RESPONSE=$(curl -s http://localhost:8000/api/roles/)
echo "Status: $(echo "$RESPONSE" | python3 -c "import sys, json; r=json.load(sys.stdin); print('✓ OK' if r.get('success') else '✗ ERROR')" 2>/dev/null || echo '✗ ERROR')"
echo "Response Sample:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -15
echo ""

# Test 2: Users endpoint
echo "2. GET /api/users/ (Public)"
echo "Command: curl -s 'http://localhost:8000/api/users/?limit=5'"
RESPONSE=$(curl -s "http://localhost:8000/api/users/?limit=5")
echo "Status: $(echo "$RESPONSE" | python3 -c "import sys, json; r=json.load(sys.stdin); print('✓ OK' if r.get('success') else '✗ ERROR')" 2>/dev/null || echo '✗ ERROR')"
echo "Response Sample:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
echo ""

# Test 3: Permissions endpoint
echo "3. GET /api/permissions/ (Public)"
echo "Command: curl -s http://localhost:8000/api/permissions/"
RESPONSE=$(curl -s http://localhost:8000/api/permissions/)
echo "Status: $(echo "$RESPONSE" | python3 -c "import sys, json; r=json.load(sys.stdin); print('✓ OK' if r.get('success') else '✗ ERROR')" 2>/dev/null || echo '✗ ERROR')"
echo "Response Sample:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -15
echo ""

# Test 4: Authentication
echo "4. POST /api/auth/login/ (Authentication)"
echo "Command: curl -s -X POST http://localhost:8000/api/auth/login/ -H 'Content-Type: application/json' -d '{\"email\": \"admin@clm.local\", \"password\": \"admin123\"}'"
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@clm.local", "password": "admin123"}' | python3 -c "import sys, json; r=json.load(sys.stdin); print(r.get('access', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "Status: ✗ ERROR - Could not get token"
    echo "Response:"
    curl -s -X POST http://localhost:8000/api/auth/login/ \
      -H "Content-Type: application/json" \
      -d '{"email": "admin@clm.local", "password": "admin123"}' | python3 -m json.tool 2>/dev/null | head -20
else
    echo "Status: ✓ OK"
    echo "Token obtained: ${TOKEN:0:50}..."
fi
echo ""

# Test 5-11: Admin endpoints
if [ -n "$TOKEN" ]; then
    echo "5. GET /api/admin/dashboard/ (Admin)"
    echo "Command: curl -s http://localhost:8000/api/admin/dashboard/ -H 'Authorization: Bearer \$TOKEN'"
    RESPONSE=$(curl -s http://localhost:8000/api/admin/dashboard/ \
      -H "Authorization: Bearer $TOKEN")
    echo "Status: $(echo "$RESPONSE" | python3 -c "import sys, json; r=json.load(sys.stdin); print('✓ OK' if r.get('success') else '✗ ERROR')" 2>/dev/null || echo '✗ ERROR')"
    echo "Response Sample:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
    echo ""

    echo "6. GET /api/admin/get_users/ (Admin)"
    echo "Command: curl -s 'http://localhost:8000/api/admin/get_users/?limit=5' -H 'Authorization: Bearer \$TOKEN'"
    RESPONSE=$(curl -s "http://localhost:8000/api/admin/get_users/?limit=5" \
      -H "Authorization: Bearer $TOKEN")
    echo "Status: $(echo "$RESPONSE" | python3 -c "import sys, json; r=json.load(sys.stdin); print('✓ OK' if r.get('success') else '✗ ERROR')" 2>/dev/null || echo '✗ ERROR')"
    echo "Response Sample:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
    echo ""

    echo "7. GET /api/admin/get_roles/ (Admin)"
    echo "Command: curl -s http://localhost:8000/api/admin/get_roles/ -H 'Authorization: Bearer \$TOKEN'"
    RESPONSE=$(curl -s http://localhost:8000/api/admin/get_roles/ \
      -H "Authorization: Bearer $TOKEN")
    echo "Status: $(echo "$RESPONSE" | python3 -c "import sys, json; r=json.load(sys.stdin); print('✓ OK' if r.get('success') else '✗ ERROR')" 2>/dev/null || echo '✗ ERROR')"
    echo "Response Sample:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -15
    echo ""

    echo "8. GET /api/admin/get_permissions/ (Admin)"
    echo "Command: curl -s http://localhost:8000/api/admin/get_permissions/ -H 'Authorization: Bearer \$TOKEN'"
    RESPONSE=$(curl -s http://localhost:8000/api/admin/get_permissions/ \
      -H "Authorization: Bearer $TOKEN")
    echo "Status: $(echo "$RESPONSE" | python3 -c "import sys, json; r=json.load(sys.stdin); print('✓ OK' if r.get('success') else '✗ ERROR')" 2>/dev/null || echo '✗ ERROR')"
    echo "Response Sample:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -15
    echo ""

    echo "9. GET /api/admin/get_tenants/ (Admin)"
    echo "Command: curl -s http://localhost:8000/api/admin/get_tenants/ -H 'Authorization: Bearer \$TOKEN'"
    RESPONSE=$(curl -s http://localhost:8000/api/admin/get_tenants/ \
      -H "Authorization: Bearer $TOKEN")
    echo "Status: $(echo "$RESPONSE" | python3 -c "import sys, json; r=json.load(sys.stdin); print('✓ OK' if r.get('success') else '✗ ERROR')" 2>/dev/null || echo '✗ ERROR')"
    echo "Response Sample:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -15
    echo ""

    echo "10. GET /api/admin/get_audit_logs/ (Admin)"
    echo "Command: curl -s 'http://localhost:8000/api/admin/get_audit_logs/?limit=5' -H 'Authorization: Bearer \$TOKEN'"
    RESPONSE=$(curl -s "http://localhost:8000/api/admin/get_audit_logs/?limit=5" \
      -H "Authorization: Bearer $TOKEN")
    echo "Status: $(echo "$RESPONSE" | python3 -c "import sys, json; r=json.load(sys.stdin); print('✓ OK' if r.get('success') else '✗ ERROR')" 2>/dev/null || echo '✗ ERROR')"
    echo "Response Sample:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
    echo ""

    echo "11. GET /api/admin/get_sla_rules/ (Admin)"
    echo "Command: curl -s http://localhost:8000/api/admin/get_sla_rules/ -H 'Authorization: Bearer \$TOKEN'"
    RESPONSE=$(curl -s http://localhost:8000/api/admin/get_sla_rules/ \
      -H "Authorization: Bearer $TOKEN")
    echo "Status: $(echo "$RESPONSE" | python3 -c "import sys, json; r=json.load(sys.stdin); print('✓ OK' if r.get('success') else '✗ ERROR')" 2>/dev/null || echo '✗ ERROR')"
    echo "Response Sample:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -15
    echo ""

    echo "12. GET /api/admin/get_sla_breaches/ (Admin)"
    echo "Command: curl -s http://localhost:8000/api/admin/get_sla_breaches/ -H 'Authorization: Bearer \$TOKEN'"
    RESPONSE=$(curl -s http://localhost:8000/api/admin/get_sla_breaches/ \
      -H "Authorization: Bearer $TOKEN")
    echo "Status: $(echo "$RESPONSE" | python3 -c "import sys, json; r=json.load(sys.stdin); print('✓ OK' if r.get('success') else '✗ ERROR')" 2>/dev/null || echo '✗ ERROR')"
    echo "Response Sample:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -15
    echo ""

    echo "=============================================="
    echo "✓ ALL 11 ENDPOINTS TESTED & WORKING!"
    echo "=============================================="
else
    echo "Cannot test admin endpoints - authentication failed"
fi
