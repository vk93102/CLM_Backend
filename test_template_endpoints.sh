#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:11000/api/v1"
TOKEN="your_token_here"  # Will be set after login

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Template Management Endpoints Test${NC}"
echo -e "${BLUE}========================================${NC}"

# Step 1: Create automation user and get token
echo -e "\n${YELLOW}Step 1: Creating automation user and getting authentication token${NC}"
python3 << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from accounts.models import Tenant, TenantUser

User = get_user_model()

# Create tenant
tenant, _ = Tenant.objects.get_or_create(
    name="Template Test Tenant",
    defaults={'status': 'active'}
)

# Create user
user, created = User.objects.get_or_create(
    email="template_test@example.com",
    defaults={
        'first_name': 'Template',
        'last_name': 'Tester',
        'is_active': True
    }
)

if created:
    user.set_password("TemplateTest123!")
    user.save()

# Add user to tenant
tenant_user, _ = TenantUser.objects.get_or_create(
    user=user,
    tenant=tenant,
    defaults={'role': 'admin'}
)

# Create token
token, _ = Token.objects.get_or_create(user=user)

print(f"USER_EMAIL={user.email}")
print(f"AUTH_TOKEN={token.key}")
print(f"TENANT_ID={tenant.id}")

EOF
export $(python3 << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from accounts.models import Tenant, TenantUser

User = get_user_model()

# Create tenant
tenant, _ = Tenant.objects.get_or_create(
    name="Template Test Tenant",
    defaults={'status': 'active'}
)

# Create user
user, created = User.objects.get_or_create(
    email="template_test@example.com",
    defaults={
        'first_name': 'Template',
        'last_name': 'Tester',
        'is_active': True
    }
)

if created:
    user.set_password("TemplateTest123!")
    user.save()

# Add user to tenant
tenant_user, _ = TenantUser.objects.get_or_create(
    user=user,
    tenant=tenant,
    defaults={'role': 'admin'}
)

# Create token
token, _ = Token.objects.get_or_create(user=user)

print(f"USER_EMAIL={user.email}")
print(f"AUTH_TOKEN={token.key}")
print(f"TENANT_ID={tenant.id}")

EOF
)

echo -e "${GREEN}✓ Authentication setup complete${NC}"
echo -e "Token: $AUTH_TOKEN"
echo -e "Tenant: $TENANT_ID\n"


# Test 1: Get all template types with full documentation
echo -e "\n${YELLOW}Test 1: GET /api/v1/templates/types/${NC}"
echo -e "Getting all available contract template types...\n"

curl -s -X GET "$BASE_URL/templates/types/" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool

echo -e "\n${GREEN}✓ Test 1 Complete${NC}\n"


# Test 2: Get template types summary
echo -e "\n${YELLOW}Test 2: GET /api/v1/templates/summary/${NC}"
echo -e "Getting summary of all template types...\n"

curl -s -X GET "$BASE_URL/templates/summary/" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool

echo -e "\n${GREEN}✓ Test 2 Complete${NC}\n"


# Test 3: Get specific template type (NDA)
echo -e "\n${YELLOW}Test 3: GET /api/v1/templates/types/NDA/${NC}"
echo -e "Getting detailed NDA template structure...\n"

curl -s -X GET "$BASE_URL/templates/types/NDA/" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool

echo -e "\n${GREEN}✓ Test 3 Complete${NC}\n"


# Test 4: Get MSA template type
echo -e "\n${YELLOW}Test 4: GET /api/v1/templates/types/MSA/${NC}"
echo -e "Getting detailed MSA template structure...\n"

curl -s -X GET "$BASE_URL/templates/types/MSA/" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool

echo -e "\n${GREEN}✓ Test 4 Complete${NC}\n"


# Test 5: Validate template data (Valid NDA)
echo -e "\n${YELLOW}Test 5: POST /api/v1/templates/validate/ (Valid NDA)${NC}"
echo -e "Validating valid NDA data...\n"

curl -s -X POST "$BASE_URL/templates/validate/" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "NDA",
    "data": {
      "effective_date": "2026-01-20",
      "first_party_name": "Acme Corporation",
      "first_party_address": "123 Business Ave, San Francisco, CA 94102",
      "second_party_name": "Tech Innovations Inc",
      "second_party_address": "456 Innovation Blvd, Palo Alto, CA 94301",
      "agreement_type": "Mutual",
      "governing_law": "California"
    }
  }' | python3 -m json.tool

echo -e "\n${GREEN}✓ Test 5 Complete${NC}\n"


# Test 6: Validate template data (Invalid - Missing required field)
echo -e "\n${YELLOW}Test 6: POST /api/v1/templates/validate/ (Invalid NDA - Missing field)${NC}"
echo -e "Validating invalid NDA data (missing required field)...\n"

curl -s -X POST "$BASE_URL/templates/validate/" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "NDA",
    "data": {
      "effective_date": "2026-01-20",
      "first_party_name": "Acme Corporation"
    }
  }' | python3 -m json.tool

echo -e "\n${GREEN}✓ Test 6 Complete${NC}\n"


# Test 7: Create template from NDA type
echo -e "\n${YELLOW}Test 7: POST /api/v1/templates/create-from-type/ (NDA)${NC}"
echo -e "Creating a new NDA template...\n"

curl -s -X POST "$BASE_URL/templates/create-from-type/" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "NDA",
    "name": "Standard NDA Template 2026",
    "description": "Our standard mutual NDA for business partnerships",
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
  }' | python3 -m json.tool

echo -e "\n${GREEN}✓ Test 7 Complete${NC}\n"


# Test 8: Create template from MSA type
echo -e "\n${YELLOW}Test 8: POST /api/v1/templates/create-from-type/ (MSA)${NC}"
echo -e "Creating a new MSA template...\n"

curl -s -X POST "$BASE_URL/templates/create-from-type/" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "MSA",
    "name": "SaaS Services Master Service Agreement",
    "description": "Master Service Agreement for cloud-based software services",
    "status": "published",
    "data": {
      "effective_date": "2026-01-20",
      "client_name": "Enterprise Solutions Ltd",
      "client_address": "789 Corporate Way, New York, NY 10001",
      "service_provider_name": "CloudTech Services Inc",
      "service_provider_address": "321 Cloud Street, Seattle, WA 98101",
      "service_description": "Cloud-based SaaS platform with 24/7 support",
      "monthly_fees": 5000,
      "payment_terms": "Net 30 from invoice date",
      "sla_uptime": "99.9% monthly uptime guarantee"
    }
  }' | python3 -m json.tool

echo -e "\n${GREEN}✓ Test 8 Complete${NC}\n"


# Test 9: Create template from EMPLOYMENT type
echo -e "\n${YELLOW}Test 9: POST /api/v1/templates/create-from-type/ (EMPLOYMENT)${NC}"
echo -e "Creating a new Employment template...\n"

curl -s -X POST "$BASE_URL/templates/create-from-type/" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "EMPLOYMENT",
    "name": "Full-Time Employee Agreement",
    "description": "Standard full-time employment contract",
    "status": "published",
    "data": {
      "effective_date": "2026-02-01",
      "employer_name": "Global Tech Corporation",
      "employer_address": "100 Tech Plaza, Austin, TX 78701",
      "employee_name": "John Smith",
      "employee_address": "456 Residential Lane, Austin, TX 78704",
      "job_title": "Senior Software Engineer",
      "employment_type": "Full-Time",
      "annual_salary": 150000,
      "start_date": "2026-02-15"
    }
  }' | python3 -m json.tool

echo -e "\n${GREEN}✓ Test 9 Complete${NC}\n"


# Test 10: Create template from SERVICE_AGREEMENT type
echo -e "\n${YELLOW}Test 10: POST /api/v1/templates/create-from-type/ (SERVICE_AGREEMENT)${NC}"
echo -e "Creating a new Service Agreement template...\n"

curl -s -X POST "$BASE_URL/templates/create-from-type/" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "SERVICE_AGREEMENT",
    "name": "Consulting Services Agreement",
    "description": "Professional consulting services agreement",
    "status": "published",
    "data": {
      "effective_date": "2026-01-15",
      "service_provider_name": "Consulting Partners LLC",
      "service_provider_address": "222 Consulting Drive, Boston, MA 02101",
      "client_name": "Manufacturing Co",
      "client_address": "333 Factory Road, Boston, MA 02102",
      "scope_of_services": "Business process optimization, supply chain analysis, and operational efficiency improvements",
      "total_project_value": 50000,
      "payment_schedule": "25% upon signing, 25% at midpoint, 50% upon completion"
    }
  }' | python3 -m json.tool

echo -e "\n${GREEN}✓ Test 10 Complete${NC}\n"


echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}All Template Tests Completed Successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
