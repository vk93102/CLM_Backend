#!/bin/bash

###############################################################################
# Real-Time Endpoint Testing with cURL
# Tests all template and PDF generation endpoints with proper JWT authentication
# Run: bash test_real_endpoints.sh
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="http://127.0.0.1:11000/api/v1"
ADMIN_EMAIL="${TEST_EMAIL:-admin@example.com}"
ADMIN_PASSWORD="${TEST_PASSWORD:-admin12345}"

# Database location (for direct token extraction)
DB_PATH="/Users/vishaljha/CLM_Backend"
PYTHON_EXEC="python3"

# Function to print colored output
print_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_test() {
    echo -e "${YELLOW}🧪 $1${NC}"
}

# Step 1: Get JWT Token
print_header "Step 1: Obtaining JWT Authentication Token"

cd "$DB_PATH"

# Extract token using Django management
JWT_TOKEN=$($PYTHON_EXEC -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CLM_Backend.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

try:
    # Try to get existing user
    user = User.objects.get(email='$ADMIN_EMAIL')
except User.DoesNotExist:
    print('User not found. Please ensure admin user exists.')
    exit(1)

# Generate token
refresh = RefreshToken.for_user(user)
print(str(refresh.access_token))
" 2>/dev/null || echo "")

if [ -z "$JWT_TOKEN" ]; then
    print_error "Failed to generate JWT token. Attempting with curl token endpoint..."
    
    # Try to get token via API
    TOKEN_RESPONSE=$(curl -s -X POST "$API_BASE_URL/token/" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$ADMIN_EMAIL\",
            \"password\": \"$ADMIN_PASSWORD\"
        }")
    
    JWT_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access":"[^"]*' | cut -d'"' -f4)
fi

if [ -z "$JWT_TOKEN" ]; then
    print_error "Could not obtain JWT token. Exiting."
    exit 1
fi

print_success "JWT Token obtained: ${JWT_TOKEN:0:20}..."
echo ""

# Step 2: Test Template Endpoints
print_header "Step 2: Testing Template Management Endpoints"

# Test 2.1: GET /templates/types/
print_test "GET /templates/types/ - Retrieve all template types"
RESPONSE=$(curl -s -X GET "$API_BASE_URL/templates/types/" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json")

STATUS=$(echo "$RESPONSE" | jq -r '.success // "error"' 2>/dev/null)
if [ "$STATUS" == "true" ]; then
    print_success "Retrieved template types"
    TYPES_COUNT=$(echo "$RESPONSE" | jq '.total_types' 2>/dev/null)
    echo -e "  Total template types: ${BLUE}$TYPES_COUNT${NC}"
    echo "$RESPONSE" | jq '.template_types | keys[]' 2>/dev/null | head -3 | while read type; do
        echo "    - $type"
    done
else
    print_error "Failed to retrieve template types"
    echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
fi
echo ""

# Test 2.2: GET /templates/summary/
print_test "GET /templates/summary/ - Retrieve template summary"
RESPONSE=$(curl -s -X GET "$API_BASE_URL/templates/summary/" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json")

STATUS=$(echo "$RESPONSE" | jq -r '.success // "error"' 2>/dev/null)
if [ "$STATUS" == "true" ]; then
    print_success "Retrieved template summary"
    echo "$RESPONSE" | jq '.summary' 2>/dev/null | head -5
else
    print_error "Failed to retrieve template summary"
fi
echo ""

# Test 2.3: GET /templates/types/{NDA}/
print_test "GET /templates/types/NDA/ - Retrieve NDA template details"
RESPONSE=$(curl -s -X GET "$API_BASE_URL/templates/types/NDA/" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json")

TEMPLATE_TYPE=$(echo "$RESPONSE" | jq -r '.template_type // "error"' 2>/dev/null)
if [ "$TEMPLATE_TYPE" == "NDA" ]; then
    print_success "Retrieved NDA template details"
    REQ_FIELDS=$(echo "$RESPONSE" | jq '.required_fields | length' 2>/dev/null)
    OPT_FIELDS=$(echo "$RESPONSE" | jq '.optional_fields | length' 2>/dev/null)
    echo -e "  Required fields: ${BLUE}$REQ_FIELDS${NC}"
    echo -e "  Optional fields: ${BLUE}$OPT_FIELDS${NC}"
else
    print_error "Failed to retrieve NDA template"
fi
echo ""

# Test 2.4: POST /templates/validate/ - Valid data
print_test "POST /templates/validate/ - Validate NDA with valid data"
RESPONSE=$(curl -s -X POST "$API_BASE_URL/templates/validate/" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "template_type": "NDA",
        "data": {
            "effective_date": "2026-01-20",
            "first_party_name": "Acme Corp",
            "first_party_address": "123 Main St, San Francisco, CA",
            "second_party_name": "Tech Innovations",
            "second_party_address": "456 Market St, Palo Alto, CA",
            "agreement_type": "Mutual",
            "governing_law": "California"
        }
    }')

IS_VALID=$(echo "$RESPONSE" | jq -r '.is_valid // "error"' 2>/dev/null)
if [ "$IS_VALID" == "true" ]; then
    print_success "NDA validation passed"
else
    print_error "NDA validation failed"
    echo "$RESPONSE" | jq '.missing_fields // .error' 2>/dev/null
fi
echo ""

# Test 2.5: POST /templates/validate/ - Invalid data (missing fields)
print_test "POST /templates/validate/ - Validate with incomplete data"
RESPONSE=$(curl -s -X POST "$API_BASE_URL/templates/validate/" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "template_type": "NDA",
        "data": {
            "effective_date": "2026-01-20"
        }
    }')

IS_VALID=$(echo "$RESPONSE" | jq -r '.is_valid // "error"' 2>/dev/null)
if [ "$IS_VALID" == "false" ]; then
    print_success "Correctly identified missing fields"
    MISSING=$(echo "$RESPONSE" | jq '.missing_fields | length' 2>/dev/null)
    echo -e "  Missing fields count: ${BLUE}$MISSING${NC}"
else
    print_warning "Expected validation to fail for incomplete data"
fi
echo ""

# Step 3: Test Template Creation
print_header "Step 3: Testing Contract Template Creation"

print_test "POST /templates/create-from-type/ - Create NDA template"
RESPONSE=$(curl -s -X POST "$API_BASE_URL/templates/create-from-type/" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "template_type": "NDA",
        "name": "Test NDA 2026",
        "description": "Standard Non-Disclosure Agreement for testing",
        "status": "published",
        "data": {
            "effective_date": "2026-01-20",
            "first_party_name": "Acme Corporation",
            "first_party_address": "123 Business Ave, San Francisco, CA 94102",
            "second_party_name": "Tech Innovations Inc",
            "second_party_address": "456 Innovation Blvd, Palo Alto, CA 94301",
            "agreement_type": "Mutual",
            "governing_law": "California"
        }
    }')

SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false' 2>/dev/null)
if [ "$SUCCESS" == "true" ]; then
    print_success "NDA template created successfully"
    TEMPLATE_ID=$(echo "$RESPONSE" | jq -r '.template_id' 2>/dev/null)
    echo -e "  Template ID: ${BLUE}$TEMPLATE_ID${NC}"
    echo -e "  Merge fields count: $(echo "$RESPONSE" | jq '.merge_fields | length' 2>/dev/null)"
    
    # Save template ID for later use
    echo "$TEMPLATE_ID" > /tmp/template_id.txt
else
    print_error "Failed to create NDA template"
    echo "$RESPONSE" | jq '.error // .' 2>/dev/null
fi
echo ""

# Step 4: Test PDF Generation Status
print_header "Step 4: Checking PDF Generation Capabilities"

print_test "GET /pdf-generation-status/ - Check available PDF methods"
RESPONSE=$(curl -s -X GET "$API_BASE_URL/pdf-generation-status/" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json")

echo "$RESPONSE" | jq '.' 2>/dev/null | while IFS= read -r line; do
    if [[ $line == *"available"* ]]; then
        if [[ $line == *"true"* ]]; then
            echo -e "${GREEN}${line}${NC}"
        else
            echo -e "${RED}${line}${NC}"
        fi
    else
        echo "$line"
    fi
done
echo ""

# Step 5: Test PDF Download (if template was created)
print_header "Step 5: Testing PDF Download Endpoint"

if [ -f /tmp/template_id.txt ]; then
    TEMPLATE_ID=$(cat /tmp/template_id.txt)
    
    print_test "GET /{template_id}/download-pdf/?method=auto - Download template as PDF"
    
    PDF_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_BASE_URL/$TEMPLATE_ID/download-pdf/?method=auto" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -o /tmp/contract.pdf)
    
    HTTP_CODE=$(echo "$PDF_RESPONSE" | tail -n 1)
    
    if [ "$HTTP_CODE" == "200" ]; then
        print_success "PDF downloaded successfully"
        FILE_SIZE=$(ls -lh /tmp/contract.pdf | awk '{print $5}')
        echo -e "  File size: ${BLUE}$FILE_SIZE${NC}"
        echo -e "  Location: ${BLUE}/tmp/contract.pdf${NC}"
    else
        print_error "Failed to download PDF (HTTP $HTTP_CODE)"
    fi
else
    print_warning "Skipping PDF download test (no template ID available)"
fi
echo ""

# Step 6: Summary
print_header "Test Summary"

echo -e "${GREEN}✅ All endpoint tests completed!${NC}"
echo ""
echo -e "API Base URL: ${BLUE}$API_BASE_URL${NC}"
echo -e "Authentication: ${GREEN}Bearer Token${NC}"
echo ""
echo "Endpoint Summary:"
echo "  1. GET  /templates/types/              - List all template types"
echo "  2. GET  /templates/types/{type}/       - Get template type details"
echo "  3. GET  /templates/summary/             - Get template summary"
echo "  4. POST /templates/validate/            - Validate template data"
echo "  5. POST /templates/create-from-type/    - Create template from type"
echo "  6. GET  /pdf-generation-status/         - Check PDF capabilities"
echo "  7. GET  /{id}/download-pdf/             - Download template as PDF"
echo "  8. POST /batch-generate-pdf/            - Generate PDFs in batch"
echo ""

# Additional curl examples
print_header "Quick Reference: cURL Examples"

echo -e "${YELLOW}Get all template types:${NC}"
echo "curl -H 'Authorization: Bearer \$TOKEN' \\
  http://127.0.0.1:11000/api/v1/templates/types/"
echo ""

echo -e "${YELLOW}Get NDA template details:${NC}"
echo "curl -H 'Authorization: Bearer \$TOKEN' \\
  http://127.0.0.1:11000/api/v1/templates/types/NDA/"
echo ""

echo -e "${YELLOW}Create template from type:${NC}"
echo "curl -X POST -H 'Authorization: Bearer \$TOKEN' \\
  -H 'Content-Type: application/json' \\
  http://127.0.0.1:11000/api/v1/templates/create-from-type/ \\
  -d '{\"template_type\":\"NDA\",\"name\":\"My NDA\",\"status\":\"published\",\"data\":{...}}'"
echo ""

echo -e "${YELLOW}Download PDF:${NC}"
echo "curl -H 'Authorization: Bearer \$TOKEN' \\
  -o contract.pdf \\
  http://127.0.0.1:11000/api/v1/{template_id}/download-pdf/?method=weasyprint"
echo ""

print_success "Test script completed successfully!"
