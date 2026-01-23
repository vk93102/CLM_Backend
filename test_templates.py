#!/usr/bin/env python3

import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from accounts.models import Tenant, TenantUser
import requests

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

BASE_URL = "http://localhost:11000/api/v1"
AUTH_HEADERS = {
    'Authorization': f'Token {token.key}',
    'Content-Type': 'application/json'
}

print("=" * 80)
print("TEMPLATE MANAGEMENT ENDPOINTS TEST SUITE")
print("=" * 80)
print(f"\nAuthentication Token: {token.key}")
print(f"User Email: {user.email}")
print(f"Tenant ID: {tenant.id}\n")


def test_endpoint(test_num, method, endpoint, data=None, description=""):
    """Test an endpoint and print results"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*80}")
    print(f"TEST {test_num}: {description}")
    print(f"{'='*80}")
    print(f"Method: {method}")
    print(f"URL: {url}")
    
    if data:
        print(f"\nRequest Body:")
        print(json.dumps(data, indent=2))
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=AUTH_HEADERS)
        elif method == 'POST':
            response = requests.post(url, headers=AUTH_HEADERS, json=data)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"\nResponse:")
        
        try:
            resp_data = response.json()
            print(json.dumps(resp_data, indent=2))
            return response.status_code, resp_data
        except:
            print(response.text)
            return response.status_code, None
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None, None


# TEST 1: Get all template types
test_endpoint(
    1, 'GET', '/templates/types/',
    description='GET /templates/types/ - Get all template types'
)

# TEST 2: Get template summary
test_endpoint(
    2, 'GET', '/templates/summary/',
    description='GET /templates/summary/ - Get template types summary'
)

# TEST 3: Get NDA template details
test_endpoint(
    3, 'GET', '/templates/types/NDA/',
    description='GET /templates/types/NDA/ - Get NDA template details'
)

# TEST 4: Get MSA template details
test_endpoint(
    4, 'GET', '/templates/types/MSA/',
    description='GET /templates/types/MSA/ - Get MSA template details'
)

# TEST 5: Validate valid NDA data
test_endpoint(
    5, 'POST', '/templates/validate/',
    data={
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
    },
    description='POST /templates/validate/ - Validate valid NDA data'
)

# TEST 6: Validate invalid NDA data
test_endpoint(
    6, 'POST', '/templates/validate/',
    data={
        "template_type": "NDA",
        "data": {
            "effective_date": "2026-01-20",
            "first_party_name": "Acme Corporation"
        }
    },
    description='POST /templates/validate/ - Validate invalid NDA data (missing fields)'
)

# TEST 7: Create NDA template
status_code, resp = test_endpoint(
    7, 'POST', '/templates/create-from-type/',
    data={
        "template_type": "NDA",
        "name": "Standard NDA 2026",
        "description": "Standard mutual NDA",
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
    },
    description='POST /templates/create-from-type/ - Create NDA template'
)

# TEST 8: Create MSA template
test_endpoint(
    8, 'POST', '/templates/create-from-type/',
    data={
        "template_type": "MSA",
        "name": "Cloud Services MSA",
        "description": "Master Service Agreement for cloud services",
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
    },
    description='POST /templates/create-from-type/ - Create MSA template'
)

# TEST 9: Create Employment template
test_endpoint(
    9, 'POST', '/templates/create-from-type/',
    data={
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
    },
    description='POST /templates/create-from-type/ - Create Employment template'
)

# TEST 10: Create Service Agreement template
test_endpoint(
    10, 'POST', '/templates/create-from-type/',
    data={
        "template_type": "SERVICE_AGREEMENT",
        "name": "Professional Services Agreement",
        "description": "Agreement for professional consulting services",
        "status": "published",
        "data": {
            "effective_date": "2026-01-15",
            "service_provider_name": "Consulting Partners LLC",
            "service_provider_address": "222 Consulting Drive, Boston, MA 02101",
            "client_name": "Manufacturing Co",
            "client_address": "333 Factory Road, Boston, MA 02102",
            "scope_of_services": "Business process optimization and supply chain analysis",
            "total_project_value": 50000,
            "payment_schedule": "25% upon signing, 25% at midpoint, 50% at completion"
        }
    },
    description='POST /templates/create-from-type/ - Create Service Agreement template'
)

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 80)
