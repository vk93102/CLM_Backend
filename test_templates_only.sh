#!/bin/bash

# Test Templates Endpoints - Real Working Response

API_URL="http://127.0.0.1:11000/api/v1"
DB_PATH="/Users/vishaljha/CLM_Backend"

echo "════════════════════════════════════════"
echo "Testing Template Endpoints"
echo "════════════════════════════════════════"
echo ""

# Get JWT token
echo "Getting JWT token..."
cd "$DB_PATH"

TOKEN=$(python3 << 'PYTHON_EOF'
import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CLM_Backend.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

try:
    user = User.objects.get(email='admin@example.com')
    refresh = RefreshToken.for_user(user)
    print(str(refresh.access_token))
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_EOF
)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token"
    exit 1
fi

echo "✅ Token obtained: ${TOKEN:0:20}..."
echo ""

# Test 1: GET /templates/types/
echo "1️⃣  Testing GET /templates/types/"
echo "────────────────────────────────────"
RESPONSE=$(curl -s -X GET "$API_URL/templates/types/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json")

echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 2: GET /templates/types/NDA/
echo "2️⃣  Testing GET /templates/types/NDA/"
echo "────────────────────────────────────"
RESPONSE=$(curl -s -X GET "$API_URL/templates/types/NDA/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json")

echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 3: GET /templates/summary/
echo "3️⃣  Testing GET /templates/summary/"
echo "────────────────────────────────────"
RESPONSE=$(curl -s -X GET "$API_URL/templates/summary/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json")

echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 4: POST /templates/validate/
echo "4️⃣  Testing POST /templates/validate/"
echo "────────────────────────────────────"
RESPONSE=$(curl -s -X POST "$API_URL/templates/validate/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "template_type": "NDA",
        "data": {
            "effective_date": "2026-01-20",
            "first_party_name": "Acme Corp",
            "first_party_address": "123 Main St",
            "second_party_name": "Tech Co",
            "second_party_address": "456 Tech Ave",
            "agreement_type": "Mutual",
            "governing_law": "California"
        }
    }')

echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 5: POST /templates/create-from-type/
echo "5️⃣  Testing POST /templates/create-from-type/"
echo "────────────────────────────────────"
RESPONSE=$(curl -s -X POST "$API_URL/templates/create-from-type/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "template_type": "NDA",
        "name": "Test NDA Template",
        "description": "Standard NDA for testing",
        "status": "published",
        "data": {
            "effective_date": "2026-01-20",
            "first_party_name": "Acme Corporation",
            "first_party_address": "123 Business Ave, San Francisco, CA",
            "second_party_name": "Tech Innovations Inc",
            "second_party_address": "456 Innovation Blvd, Palo Alto, CA",
            "agreement_type": "Mutual",
            "governing_law": "California"
        }
    }')

echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
echo ""

echo "════════════════════════════════════════"
echo "✅ All Template Endpoints Tested"
echo "════════════════════════════════════════"
