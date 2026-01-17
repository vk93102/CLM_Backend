import subprocess
import json
import sys
import time

def get_auth_token():
    """Read the JWT token from file"""
    try:
        with open("/tmp/auth_token.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("✗ ERROR: No auth token found. Run setup first.")
        sys.exit(1)

def get_tenant_id():
    """Read the tenant ID from file"""
    try:
        with open("/tmp/tenant_id.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def run_curl(method, url, data=None, token=None):
    """Run curl command with optional authentication"""
    cmd = ["curl", "-s", "-w", "\n%{http_code}"]
    
    if method == 'POST':
        cmd.extend(["-X", "POST"])
        cmd.extend(["-H", "Content-Type: application/json"])
        if data:
            cmd.extend(["-d", json.dumps(data)])
    elif method == 'GET':
        cmd.extend(["-X", "GET"])
    
    if token:
        cmd.extend(["-H", f"Authorization: Bearer {token}"])
    
    cmd.append(url)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        lines = result.stdout.strip().split('\n')
        status = lines[-1]
        body = '\n'.join(lines[:-1])
        
        return int(status), body
    except Exception as e:
        return None, str(e)

def test_endpoint_5_classification(token):
    """Test Endpoint 5: Clause Classification"""
    print("\n" + "="*70)
    print("ENDPOINT 5: CLAUSE CLASSIFICATION")
    print("="*70)
    
    base_url = "http://localhost:11000/api/v1"
    
    test_cases = [
        {
            "name": "Confidentiality Clause",
            "text": "Both parties agree to keep all proprietary information and trade secrets confidential and not disclose to third parties."
        },
        {
            "name": "Termination Clause",
            "text": "Either party may terminate this agreement with 30 days written notice."
        },
        {
            "name": "Payment Terms",
            "text": "Payment shall be made within 30 days of invoice receipt."
        },
        {
            "name": "IP Protection",
            "text": "All intellectual property developed by either party shall remain the property of that party."
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n[TEST] {test['name']}")
        payload = {"text": test['text']}
        
        status, body = run_curl('POST', f"{base_url}/ai/classify/", payload, token)
        
        if status is None:
            print(f"  ✗ FAILED - Connection error: {body}")
            failed += 1
            continue
        
        print(f"  Status: {status}")
        
        if status == 200:
            try:
                data = json.loads(body)
                print(f"  ✓ PASSED")
                print(f"    - Label: {data.get('label', 'N/A')}")
                print(f"    - Category: {data.get('category', 'N/A')}")
                print(f"    - Confidence: {data.get('confidence', 'N/A'):.2%}")
                passed += 1
            except json.JSONDecodeError:
                print(f"  ✗ FAILED - Invalid JSON response")
                print(f"    Response: {body[:100]}")
                failed += 1
        elif status == 401:
            print(f"  ✗ FAILED - Unauthorized (token may be invalid)")
            print(f"    Response: {body[:100]}")
            failed += 1
        else:
            print(f"  ✗ FAILED - Status {status}")
            print(f"    Response: {body[:200]}")
            failed += 1
    
    print(f"\nEndpoint 5 Results: {passed}/{passed+failed} passed")
    return passed, failed

def test_endpoint_4_metadata(token):
    """Test Endpoint 4: Metadata Extraction"""
    print("\n" + "="*70)
    print("ENDPOINT 4: METADATA EXTRACTION")
    print("="*70)
    
    base_url = "http://localhost:11000/api/v1"
    
    test_cases = [
        {
            "name": "Full Contract Document",
            "document_id": 1,
            "text": "SERVICE AGREEMENT\n\nBetween: ABC Corporation, a corporation organized under the laws of Delaware, and XYZ Inc., a corporation organized under the laws of California.\n\nEffective Date: January 15, 2024\n\nContract Value: USD 250,000\n\nThis agreement defines the terms and conditions of services to be provided."
        },
        {
            "name": "Simple NDA",
            "document_id": 2,
            "text": "NDA AGREEMENT\n\nParties: Tech Startup LLC and Innovation Partners Corp\n\nDate: February 1, 2024\n\nAmount: $50,000 annual fee\n\nTerms: 2 years"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n[TEST] {test['name']}")
        payload = {
            "document_id": test['document_id'],
            "document_text": test['text']
        }
        
        status, body = run_curl('POST', f"{base_url}/ai/extract/metadata/", payload, token)
        
        if status is None:
            print(f"  ✗ FAILED - Connection error: {body}")
            failed += 1
            continue
        
        print(f"  Status: {status}")
        
        if status == 200:
            try:
                data = json.loads(body)
                print(f"  ✓ PASSED")
                print(f"    - Parties: {data.get('parties', [])}")
                print(f"    - Date: {data.get('effective_date', 'N/A')}")
                print(f"    - Value: {data.get('contract_value', 'N/A')}")
                passed += 1
            except json.JSONDecodeError:
                print(f"  ✗ FAILED - Invalid JSON response")
                print(f"    Response: {body[:100]}")
                failed += 1
        elif status == 401:
            print(f"  ✗ FAILED - Unauthorized (token may be invalid)")
            print(f"    Response: {body[:100]}")
            failed += 1
        else:
            print(f"  ✗ FAILED - Status {status}")
            print(f"    Response: {body[:200]}")
            failed += 1
    
    print(f"\nEndpoint 4 Results: {passed}/{passed+failed} passed")
    return passed, failed

def test_endpoint_3_draft_generation(token):
    """Test Endpoint 3: Draft Generation (Async)"""
    print("\n" + "="*70)
    print("ENDPOINT 3: DRAFT GENERATION (ASYNC)")
    print("="*70)
    
    base_url = "http://localhost:11000/api/v1"
    
    test_cases = [
        {
            "name": "NDA Draft Generation",
            "contract_type": "NDA",
            "parties": ["TechCorp", "ConsultantLLC"],
            "input_params": {"duration": "2 years", "jurisdiction": "Delaware"}
        },
        {
            "name": "Service Agreement Draft",
            "contract_type": "Service Agreement",
            "parties": ["Service Provider Inc", "Client Company"],
            "input_params": {"duration": "1 year", "service_type": "Consulting"}
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n[TEST] {test['name']}")
        payload = {
            "contract_type": test['contract_type'],
            "parties": test['parties'],
            "input_params": test['input_params']
        }
        
        status, body = run_curl('POST', f"{base_url}/ai/generate/draft/", payload, token)
        
        if status is None:
            print(f"  ✗ FAILED - Connection error: {body}")
            failed += 1
            continue
        
        print(f"  Status: {status}")
        
        if status in [200, 201, 202]:
            try:
                data = json.loads(body)
                task_id = data.get('task_id')
                print(f"  ✓ PASSED - Task created")
                print(f"    - Task ID: {task_id}")
                print(f"    - Status: {data.get('status', 'N/A')}")
                print(f"    - Contract Type: {data.get('contract_type', 'N/A')}")
                
                # Try to poll status
                if task_id:
                    print(f"\n  [POLLING STATUS]")
                    time.sleep(1)
                    status_code, status_body = run_curl(
                        'GET', 
                        f"{base_url}/ai/generate/status/{task_id}/",
                        None,
                        token
                    )
                    print(f"    Status Code: {status_code}")
                    if status_code == 200:
                        status_data = json.loads(status_body)
                        print(f"    - Current Status: {status_data.get('status', 'N/A')}")
                
                passed += 1
            except json.JSONDecodeError:
                print(f"  ✗ FAILED - Invalid JSON response")
                print(f"    Response: {body[:100]}")
                failed += 1
        elif status == 401:
            print(f"  ✗ FAILED - Unauthorized (token may be invalid)")
            print(f"    Response: {body[:100]}")
            failed += 1
        else:
            print(f"  ✗ FAILED - Status {status}")
            print(f"    Response: {body[:200]}")
            failed += 1
    
    print(f"\nEndpoint 3 Results: {passed}/{passed+failed} passed")
    return passed, failed

def main():
    print("\n" + "="*70)
    print("AUTHENTICATED AI ENDPOINTS TEST - PORT 11000")
    print("="*70)
    
    # Get authentication token
    token = get_auth_token()
    tenant_id = get_tenant_id()
    
    print(f"\n✓ Using Authentication Token")
    print(f"  Token: {token[:40]}...{token[-10:]}")
    print(f"  Tenant: {tenant_id}")
    
    # Run all tests
    total_passed = 0
    total_failed = 0
    
    # Test Endpoint 5
    p5, f5 = test_endpoint_5_classification(token)
    total_passed += p5
    total_failed += f5
    
    # Test Endpoint 4
    p4, f4 = test_endpoint_4_metadata(token)
    total_passed += p4
    total_failed += f4
    
    # Test Endpoint 3
    p3, f3 = test_endpoint_3_draft_generation(token)
    total_passed += p3
    total_failed += f3
    
    # Summary
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"\nEndpoint 3 (Draft Generation):  {p3}/{p3+f3} PASSED")
    print(f"Endpoint 4 (Metadata Extract): {p4}/{p4+f4} PASSED")
    print(f"Endpoint 5 (Classification):   {p5}/{p5+f5} PASSED")
    print(f"\nTOTAL: {total_passed}/{total_passed+total_failed} tests PASSED")
    
    if total_failed == 0:
        print(f"\n✅ ALL AUTHENTICATED TESTS PASSED\n")
        return 0
    else:
        print(f"\n❌ {total_failed} tests FAILED\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
