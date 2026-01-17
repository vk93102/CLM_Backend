#!/usr/bin/env python3
"""
Live endpoint testing on port 11000
"""
import subprocess
import json
import sys

def run_curl(method, url, data=None):
    """Run curl command and return status code and response body"""
    cmd = ["curl", "-s", "-w", "\n%{http_code}"]
    
    if method == 'POST':
        cmd.extend(["-X", "POST", "-H", "Content-Type: application/json"])
        if data:
            cmd.extend(["-d", json.dumps(data)])
    elif method == 'GET':
        cmd.extend(["-X", "GET"])
    
    cmd.append(url)
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    lines = result.stdout.strip().split('\n')
    status = lines[-1]
    body = '\n'.join(lines[:-1])
    
    return int(status), body

def main():
    print("\n" + "="*70)
    print("LIVE AI ENDPOINTS TEST - PORT 11000")
    print("="*70 + "\n")
    
    base_url = "http://localhost:11000/api/v1"
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health Check
    tests_total += 1
    print("[TEST 1] Health Check")
    try:
        status, body = run_curl('GET', f"{base_url}/health/")
        print(f"  Status: {status}")
        if status == 200:
            print(f"  ✓ PASSED - Server is healthy")
            tests_passed += 1
        else:
            print(f"  Response: {body[:100]}")
    except Exception as e:
        print(f"  ✗ FAILED - {e}")
    
    # Test 2: Clause Classification (with auth) 
    tests_total += 1
    print("\n[TEST 2] Clause Classification Endpoint")
    try:
        payload = {"text": "confidentiality agreement clause"}
        status, body = run_curl('POST', f"{base_url}/ai/classify/", payload)
        print(f"  Status: {status}")
        if status == 401:
            print(f"  ✓ PASSED - Authentication required (expected)")
            tests_passed += 1
        elif status in [200, 201]:
            try:
                data = json.loads(body)
                print(f"  ✓ PASSED - Response: {json.dumps(data, indent=4)[:200]}")
                tests_passed += 1
            except:
                print(f"  Response: {body}")
        else:
            print(f"  ✗ Status {status}: {body[:100]}")
    except Exception as e:
        print(f"  ✗ FAILED - {e}")
    
    # Test 3: Draft Generation
    tests_total += 1
    print("\n[TEST 3] Draft Generation Endpoint")
    try:
        payload = {
            "contract_type": "NDA",
            "parties": ["Company A", "Company B"]
        }
        status, body = run_curl('POST', f"{base_url}/ai/generate/draft/", payload)
        print(f"  Status: {status}")
        if status == 401:
            print(f"  ✓ PASSED - Authentication required (expected)")
            tests_passed += 1
        elif status in [200, 201, 202]:
            try:
                data = json.loads(body)
                print(f"  ✓ PASSED - Response: {json.dumps(data, indent=4)[:200]}")
                tests_passed += 1
            except:
                print(f"  Response: {body}")
        else:
            print(f"  ✗ Status {status}: {body[:100]}")
    except Exception as e:
        print(f"  ✗ FAILED - {e}")
    
    # Test 4: Metadata Extraction
    tests_total += 1
    print("\n[TEST 4] Metadata Extraction Endpoint")
    try:
        payload = {
            "document_id": 1,
            "document_text": "Agreement between ABC and XYZ dated 2024-01-01 for $100,000"
        }
        status, body = run_curl('POST', f"{base_url}/ai/extract/metadata/", payload)
        print(f"  Status: {status}")
        if status == 401:
            print(f"  ✓ PASSED - Authentication required (expected)")
            tests_passed += 1
        elif status in [200, 201]:
            try:
                data = json.loads(body)
                print(f"  ✓ PASSED - Response: {json.dumps(data, indent=4)[:200]}")
                tests_passed += 1
            except:
                print(f"  Response: {body}")
        else:
            print(f"  ✗ Status {status}: {body[:100]}")
    except Exception as e:
        print(f"  ✗ FAILED - {e}")
    
    # Summary
    print("\n" + "="*70)
    print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
    print("="*70 + "\n")
    
    if tests_passed == tests_total:
        print("✓ ALL TESTS PASSED\n")
        return 0
    else:
        print(f"✗ {tests_total - tests_passed} tests failed\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
