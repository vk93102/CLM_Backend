#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all endpoints in the CLM Backend API
"""

import requests
import json
from datetime import datetime
import uuid

# Base configuration
BASE_URL = "http://127.0.0.1:8888/api"
HEADERS = {"Content-Type": "application/json"}

# Test results
results = {
    "api_version": "v1",
    "base_url": BASE_URL,
    "test_date": datetime.utcnow().isoformat() + "Z",
    "endpoints": {},
    "summary": {"total": 0, "passed": 0, "failed": 0}
}

# Test user credentials
test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
test_password = "TestPassword123!"
access_token = None
refresh_token = None
user_id = None
tenant_id = None

def test_endpoint(name, method, endpoint, request_body=None, auth=False, description=""):
    """Test a single endpoint"""
    global access_token, refresh_token, user_id, tenant_id
    
    url = f"{BASE_URL}{endpoint}"
    headers = HEADERS.copy()
    
    if auth and access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"Endpoint: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"URL: {url}")
    
    try:
        if method == "POST":
            print(f"Request Body: {json.dumps(request_body, indent=2)}")
            response = requests.post(url, json=request_body, headers=headers, timeout=10)
        elif method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "PATCH":
            print(f"Request Body: {json.dumps(request_body, indent=2)}")
            response = requests.patch(url, json=request_body, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        success = 200 <= response.status_code < 300
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response (text): {response.text}")
            response_data = response.text
        
        # Extract tokens and user info for subsequent tests
        if name == "1. Register User" and success:
            print("✓ User registered successfully (but may have existed)")
        
        if name == "2. Login User" and success:
            if isinstance(response_data, dict):
                access_token = response_data.get('access')
                refresh_token = response_data.get('refresh')
                user_info = response_data.get('user', {})
                user_id = user_info.get('user_id')
                tenant_id = user_info.get('tenant_id')
                print(f"✓ Login successful")
                print(f"  - Access Token: {access_token[:50]}...")
                print(f"  - User ID: {user_id}")
                print(f"  - Tenant ID: {tenant_id}")
        
        # Store result
        results["endpoints"][name] = {
            "endpoint": endpoint,
            "method": method,
            "description": description,
            "request_body": request_body or {},
            "response": response_data,
            "status_code": response.status_code,
            "success": success
        }
        
        results["summary"]["total"] += 1
        if success:
            results["summary"]["passed"] += 1
            print(f"✓ PASSED")
        else:
            results["summary"]["failed"] += 1
            print(f"✗ FAILED")
        
        return success, response_data
        
    except requests.exceptions.RequestException as e:
        print(f"✗ ERROR: {str(e)}")
        results["endpoints"][name] = {
            "endpoint": endpoint,
            "method": method,
            "description": description,
            "error": str(e),
            "status_code": 0,
            "success": False
        }
        results["summary"]["total"] += 1
        results["summary"]["failed"] += 1
        return False, None


def main():
    """Run all endpoint tests"""
    global access_token
    
    print("\n" + "="*80)
    print("CLM BACKEND API - COMPREHENSIVE ENDPOINT TEST")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Started: {datetime.utcnow().isoformat()}Z")
    print("="*80)
    
    # ============================================================================
    # PHASE 1: AUTHENTICATION
    # ============================================================================
    print("\n\n" + "█"*80)
    print("PHASE 1: AUTHENTICATION ENDPOINTS")
    print("█"*80)
    
    # 1. Register User
    test_endpoint(
        "1. Register User",
        "POST",
        "/auth/register/",
        {
            "email": test_email,
            "password": test_password,
            "first_name": "Test",
            "last_name": "User"
        },
        auth=False,
        description="Register a new user account"
    )
    
    # 2. Login User
    success, response = test_endpoint(
        "2. Login User",
        "POST",
        "/auth/login/",
        {
            "email": test_email,
            "password": test_password
        },
        auth=False,
        description="Authenticate user and get JWT tokens"
    )
    
    if not success or not access_token:
        print("\n⚠️  WARNING: Could not obtain access token. Skipping authenticated endpoints.")
        print("Attempting to use an existing valid token for testing...")
        # Try to login with a known user that might exist
        test_endpoint(
            "2b. Login with Existing User",
            "POST",
            "/auth/login/",
            {
                "email": "test@example.com",
                "password": "password123"
            },
            auth=False,
            description="Login with existing test user"
        )
    
    # 3. Get Current User
    if access_token:
        test_endpoint(
            "3. Get Current User",
            "GET",
            "/auth/me/",
            auth=True,
            description="Get current authenticated user information"
        )
    
    # ============================================================================
    # PHASE 2: CONTRACT ENDPOINTS
    # ============================================================================
    print("\n\n" + "█"*80)
    print("PHASE 2: CONTRACT MANAGEMENT ENDPOINTS")
    print("█"*80)
    
    if access_token:
        # 4. List Contracts
        test_endpoint(
            "4. List Contracts",
            "GET",
            "/contracts/",
            auth=True,
            description="List all contracts for the authenticated user's tenant"
        )
        
        # 5. Get Contract Statistics
        test_endpoint(
            "5. Get Contract Statistics",
            "GET",
            "/contracts/statistics/",
            auth=True,
            description="Get contract statistics and monthly trends"
        )
        
        # 6. Get Recent Contracts
        test_endpoint(
            "6. Get Recent Contracts",
            "GET",
            "/contracts/recent/",
            auth=True,
            description="Get recently created contracts"
        )
        
        # 7. Create Contract (without file)
        test_endpoint(
            "7. Create Contract",
            "POST",
            "/contracts/",
            {
                "title": f"Test Contract {uuid.uuid4().hex[:6]}",
                "contract_type": "service_agreement",
                "status": "draft",
                "counterparty": "Test Company Inc."
            },
            auth=True,
            description="Create a new contract"
        )
    
    # ============================================================================
    # PHASE 3: CONTRACT GENERATION ENDPOINTS
    # ============================================================================
    print("\n\n" + "█"*80)
    print("PHASE 3: CONTRACT GENERATION & TEMPLATES ENDPOINTS")
    print("█"*80)
    
    if access_token:
        # 8. List Contract Templates
        test_endpoint(
            "8. List Contract Templates",
            "GET",
            "/contract-templates/",
            auth=True,
            description="List all available contract templates"
        )
        
        # 9. List Clauses
        test_endpoint(
            "9. List Clauses",
            "GET",
            "/clauses/",
            auth=True,
            description="List all available clauses"
        )
        
        # 10. List Generation Jobs
        test_endpoint(
            "10. List Generation Jobs",
            "GET",
            "/generation-jobs/",
            auth=True,
            description="List all contract generation jobs"
        )
    
    # ============================================================================
    # SUMMARY AND RESULTS
    # ============================================================================
    print("\n\n" + "█"*80)
    print("TEST SUMMARY")
    print("█"*80)
    
    print(f"\nTotal Tests: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']} ✓")
    print(f"Failed: {results['summary']['failed']} ✗")
    
    if results['summary']['total'] > 0:
        success_rate = (results['summary']['passed'] / results['summary']['total']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    # ============================================================================
    # SAVE RESULTS
    # ============================================================================
    print("\n\n" + "█"*80)
    print("SAVING TEST RESULTS")
    print("█"*80)
    
    results_file = "/Users/vishaljha/Desktop/CLM_Backend/test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✓ Results saved to: {results_file}")
    
    # Print endpoint summary table
    print("\n\n" + "█"*80)
    print("ENDPOINT SUMMARY TABLE")
    print("█"*80)
    print(f"\n{'Endpoint':<40} {'Method':<8} {'Status':<10} {'Result':<10}")
    print("-"*70)
    
    for name, data in results['endpoints'].items():
        endpoint = data.get('endpoint', 'N/A')
        method = data.get('method', 'N/A')
        status = data.get('status_code', 'ERROR')
        success = "✓ PASSED" if data.get('success', False) else "✗ FAILED"
        print(f"{endpoint:<40} {method:<8} {str(status):<10} {success:<10}")
    
    print("\n" + "="*80)
    print(f"Test Completed: {datetime.utcnow().isoformat()}Z")
    print("="*80)


if __name__ == "__main__":
    main()
