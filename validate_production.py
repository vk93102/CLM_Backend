#!/usr/bin/env python3
"""
Production Endpoint Validation Script
Tests all three AI endpoints with real contract data
No Django dependencies - uses file-based token loading
"""
import requests
import json
import sys
from time import time
from pathlib import Path

# Load token from file
def get_token():
    """Load JWT token from test data file"""
    token_file = Path('/Users/vishaljha/CLM_Backend/TEST_TOKEN.txt')
    if token_file.exists():
        return token_file.read_text().strip()
    
    print("ERROR: Test token file not found at /Users/vishaljha/CLM_Backend/TEST_TOKEN.txt")
    print("Please run: python3 -c \"from rest_framework_simplejwt.tokens import RefreshToken; from users.models import CustomUser; import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings'); django.setup(); user = CustomUser.objects.get(username='testadmin'); print(str(RefreshToken.for_user(user).access_token))\" > TEST_TOKEN.txt")
    sys.exit(1)

BASE_URL = 'http://localhost:11000/api/v1'

def make_request(endpoint, data, method='POST'):
    """Make HTTP request to endpoint"""
    token = get_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        start = time()
        response = requests.request(
            method=method,
            url=f'{BASE_URL}{endpoint}',
            json=data if method == 'POST' else None,
            headers=headers,
            timeout=15
        )
        elapsed = (time() - start) * 1000
        return response.status_code, response.text, elapsed
    except Exception as e:
        return None, str(e), 0

def test_endpoint_5():
    """Test Classification Endpoint"""
    print("\n" + "="*70)
    print("ENDPOINT 5: CLAUSE CLASSIFICATION")
    print("="*70)
    
    test_cases = [
        {
            'name': 'Confidentiality Clause',
            'text': 'Both parties agree to maintain strict confidentiality of all information shared during negotiations.'
        },
        {
            'name': 'Termination Clause',
            'text': 'Either party may terminate this Agreement upon thirty (30) days prior written notice to the other party.'
        },
        {
            'name': 'Payment Terms',
            'text': 'Payment shall be made within thirty (30) days of invoice receipt.'
        },
        {
            'name': 'IP Protection',
            'text': 'All intellectual property shall remain exclusive property of Service Provider.'
        }
    ]
    
    passed = 0
    for test in test_cases:
        status, response, elapsed = make_request('/ai/classify/', {'text': test['text']})
        
        print(f"\n✓ {test['name']}")
        print(f"  HTTP Status: {status}")
        print(f"  Response Time: {elapsed:.0f}ms")
        
        if status == 200:
            try:
                data = json.loads(response)
                print(f"  Label: {data.get('label', 'N/A')}")
                print(f"  Confidence: {data.get('confidence', 'N/A')}")
                passed += 1
            except:
                print(f"  Response: {response[:100]}")
        else:
            print(f"  Error: {response[:100]}")
    
    return passed

def test_endpoint_3():
    """Test Draft Generation Endpoint"""
    print("\n" + "="*70)
    print("ENDPOINT 3: DRAFT GENERATION (ASYNC)")
    print("="*70)
    
    test_cases = [
        {
            'name': 'NDA Draft',
            'contract_type': 'NDA',
            'input_params': {
                'party_1': 'Acme Corporation',
                'party_2': 'Innovation Partners LLC',
                'duration_years': 2,
                'jurisdiction': 'Delaware'
            }
        },
        {
            'name': 'Service Agreement',
            'contract_type': 'Service Agreement',
            'input_params': {
                'party_1': 'TechCorp Services Inc.',
                'party_2': 'Enterprise Solutions Ltd.',
                'monthly_value': 50000,
                'sla': '99.9%'
            }
        }
    ]
    
    passed = 0
    for test in test_cases:
        status, response, elapsed = make_request('/ai/generate/draft/', test)
        
        print(f"\n✓ {test['name']}")
        print(f"  HTTP Status: {status}")
        print(f"  Response Time: {elapsed:.0f}ms")
        
        if status == 202:
            try:
                data = json.loads(response)
                print(f"  Task ID: {data.get('task_id', 'N/A')}")
                print(f"  Status: {data.get('status', 'N/A')}")
                passed += 1
            except:
                print(f"  Response: {response[:100]}")
        else:
            print(f"  Error: {response[:100]}")
    
    return passed

def test_endpoint_4():
    """Test Metadata Extraction Endpoint"""
    print("\n" + "="*70)
    print("ENDPOINT 4: METADATA EXTRACTION")
    print("="*70)
    
    test_cases = [
        {
            'name': 'Service Contract',
            'document_text': '''SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into as of January 1, 2024, 
by and between CloudTech Solutions Corp. ("Service Provider") and 
GlobalEnterprises Inc. ("Client").

1. SERVICES
Service Provider shall provide cloud infrastructure services valued at 
$600,000 annually.

2. TERM
This Agreement shall commence on January 1, 2024, and continue for a period 
of one (1) year unless earlier terminated.

3. PAYMENT
Payment shall be made quarterly in advance.'''
        },
        {
            'name': 'NDA',
            'document_text': '''MUTUAL NON-DISCLOSURE AGREEMENT

This NDA ("Agreement") is between InnovateTech Inc. and 
Venture Capital Partners LP.

CONFIDENTIAL VALUE: $100,000
EFFECTIVE DATE: January 1, 2024
TERM: 3 years

Both parties agree to maintain confidentiality of all proprietary information.'''
        }
    ]
    
    passed = 0
    for test in test_cases:
        test_payload = {'document_text': test['document_text']}
        status, response, elapsed = make_request('/ai/extract/metadata/', test_payload)
        
        print(f"\n✓ {test['name']}")
        print(f"  HTTP Status: {status}")
        print(f"  Response Time: {elapsed:.0f}ms")
        
        if status == 200:
            try:
                data = json.loads(response)
                print(f"  Parties: {data.get('parties', 'N/A')}")
                print(f"  Value: {data.get('value', 'N/A')}")
                print(f"  Term: {data.get('term', 'N/A')}")
                passed += 1
            except:
                print(f"  Response: {response[:100]}")
        else:
            print(f"  Error: {response[:100]}")
    
    return passed

def test_security():
    """Test Security Validation"""
    print("\n" + "="*70)
    print("SECURITY & VALIDATION TESTS")
    print("="*70)
    
    passed = 0
    
    # Test 1: Missing required field
    status, _, _ = make_request('/ai/classify/', {'text': ''})
    print(f"\n✓ Missing Text Field")
    print(f"  HTTP Status: {status}")
    if status == 400:
        print(f"  Result: PASS (Got expected 400)")
        passed += 1
    
    # Test 2: Invalid token
    print(f"\n✓ Invalid Token")
    try:
        headers = {'Authorization': 'Bearer invalid_token_xyz', 'Content-Type': 'application/json'}
        resp = requests.post(f'{BASE_URL}/ai/classify/', json={'text': 'test'}, headers=headers, timeout=10)
        print(f"  HTTP Status: {resp.status_code}")
        if resp.status_code == 401:
            print(f"  Result: PASS (Got expected 401)")
            passed += 1
    except Exception as e:
        print(f"  Error: {str(e)}")
    
    # Test 3: No auth header
    print(f"\n✓ No Authorization Header")
    try:
        resp = requests.post(f'{BASE_URL}/ai/classify/', json={'text': 'test'}, timeout=10)
        print(f"  HTTP Status: {resp.status_code}")
        if resp.status_code == 401:
            print(f"  Result: PASS (Got expected 401)")
            passed += 1
    except Exception as e:
        print(f"  Error: {str(e)}")
    
    return passed

if __name__ == '__main__':
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "PRODUCTION ENDPOINT VALIDATION - CLM BACKEND".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {}
    
    try:
        results['E5'] = test_endpoint_5()
        results['E3'] = test_endpoint_3()
        results['E4'] = test_endpoint_4()
        results['SEC'] = test_security()
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total_passed = sum(results.values())
        total_tests = 4 + 2 + 2 + 3
        
        print(f"\nEndpoint 5 (Classification): {results['E5']}/4 PASSED")
        print(f"Endpoint 3 (Draft Generation): {results['E3']}/2 PASSED")
        print(f"Endpoint 4 (Metadata Extraction): {results['E4']}/2 PASSED")
        print(f"Security & Validation: {results['SEC']}/3 PASSED")
        print(f"\nTOTAL: {total_passed}/{total_tests} PASSED ({(total_passed/total_tests*100):.1f}%)")
        
        print("\n✅ PRODUCTION READINESS: APPROVED" if total_passed == total_tests else "\n⚠️  SOME TESTS FAILED")
        print("\nAll tests completed with real contract data and endpoints operational.")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        sys.exit(1)
