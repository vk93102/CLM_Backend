#!/usr/bin/env python3
"""
Production Test Suite for AI Endpoints
Real contract data - CLM Backend v5.0
"""
import requests
import json
import os
from pathlib import Path

# Configuration
API_URL = "http://localhost:11000/api/v1"
AUTH_TOKEN = open("/tmp/auth_token.txt").read().strip()

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
RESET = '\033[0m'

# Counters
tests_passed = 0
tests_failed = 0

def log_test(name, passed, details=""):
    global tests_passed, tests_failed
    if passed:
        print(f"{GREEN}[✓ PASS]{RESET} {name}")
        tests_passed += 1
    else:
        print(f"{RED}[✗ FAIL]{RESET} {name}")
        if details:
            print(f"  {details}")
        tests_failed += 1

def header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(text)
    print(f"{BLUE}{'='*70}{RESET}")

# Headers
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

header("PRODUCTION AI ENDPOINTS TEST SUITE - REAL CONTRACT DATA")
print(f"Auth Token: {AUTH_TOKEN[:40]}...\n")

# Test Health
try:
    resp = requests.get(f"{API_URL}/health/", headers=headers, timeout=5)
    log_test("Server Health Check", resp.status_code == 200, f"Status: {resp.status_code}")
except Exception as e:
    log_test("Server Health Check", False, f"Error: {str(e)}")

# ENDPOINT 5: CLAUSE CLASSIFICATION
header("ENDPOINT 5: CLAUSE CLASSIFICATION")

test_cases_e5 = [
    {
        "name": "Classify Confidentiality Clause",
        "text": "Both parties agree to maintain strict confidentiality of all proprietary information, trade secrets, and technical data shared during the term of this agreement and for a period of five (5) years thereafter."
    },
    {
        "name": "Classify Termination Clause",
        "text": "Either party may terminate this Agreement upon thirty (30) days prior written notice to the other party. In the event of material breach, either party may terminate immediately upon written notice if the breaching party fails to cure such breach within fifteen (15) days of notification."
    },
    {
        "name": "Classify Payment Terms",
        "text": "Payment shall be made within thirty (30) days of invoice receipt. Late payments shall accrue interest at the rate of 1.5% per month or the maximum rate permitted by law. All invoices must be in USD and paid via wire transfer."
    },
    {
        "name": "Classify Intellectual Property",
        "text": "All intellectual property rights, including patents, copyrights, and trademarks developed by Service Provider shall remain exclusive property of Service Provider. Client retains all rights to pre-existing intellectual property."
    }
]

for test in test_cases_e5:
    try:
        resp = requests.post(
            f"{API_URL}/ai/classify/",
            headers=headers,
            json={"text": test["text"]},
            timeout=10
        )
        has_label = "label" in resp.text
        log_test(test["name"], resp.status_code == 200 and has_label, 
                f"Status: {resp.status_code}, Response: {resp.text[:100]}")
    except Exception as e:
        log_test(test["name"], False, f"Error: {str(e)}")

# ENDPOINT 3: DRAFT GENERATION
header("ENDPOINT 3: DRAFT DOCUMENT GENERATION")

test_cases_e3 = [
    {
        "name": "Generate NDA Draft",
        "data": {
            "contract_type": "NDA",
            "input_params": {
                "parties": ["Acme Corporation", "Innovation Partners LLC"],
                "jurisdiction": "Delaware",
                "duration_years": 2
            }
        }
    },
    {
        "name": "Generate Service Agreement",
        "data": {
            "contract_type": "Service Agreement",
            "input_params": {
                "parties": ["TechCorp Services Inc.", "Enterprise Solutions Ltd."],
                "service_type": "Cloud Infrastructure Management",
                "monthly_fee": "50000",
                "sla_uptime": "99.9%",
                "jurisdiction": "New York"
            }
        }
    }
]

for test in test_cases_e3:
    try:
        resp = requests.post(
            f"{API_URL}/ai/generate/draft/",
            headers=headers,
            json=test["data"],
            timeout=30
        )
        log_test(test["name"], resp.status_code == 202, 
                f"Status: {resp.status_code}")
    except Exception as e:
        log_test(test["name"], False, f"Error: {str(e)}")

# ENDPOINT 4: METADATA EXTRACTION
header("ENDPOINT 4: METADATA EXTRACTION")

test_cases_e4 = [
    {
        "name": "Extract Service Contract Metadata",
        "text": "SERVICE AGREEMENT EFFECTIVE DATE: January 15, 2026 EXPIRATION DATE: January 14, 2027 This Service Agreement is entered into by CloudTech Solutions Corp., Delaware corporation, and GlobalEnterprises Inc., California corporation. Monthly service fee of $600,000.00 USD, payable within thirty days of invoice. Service Provider guarantees 99.95% uptime availability. JURISDICTION: State of New York"
    },
    {
        "name": "Extract NDA Metadata",
        "text": "MUTUAL NON-DISCLOSURE AGREEMENT PARTIES: InnovateTech Inc., Massachusetts corporation and Venture Capital Partners LP, Delaware limited partnership. CONFIDENTIAL VALUE: $100,000.00 EFFECTIVE DATE: January 10, 2026 EXPIRATION: January 10, 2031 The parties agree to maintain strict confidentiality of all proprietary information. GOVERNING LAW: Commonwealth of Massachusetts"
    }
]

for test in test_cases_e4:
    try:
        resp = requests.post(
            f"{API_URL}/ai/extract/metadata/",
            headers=headers,
            json={"document_text": test["text"]},
            timeout=30
        )
        log_test(test["name"], resp.status_code == 200, 
                f"Status: {resp.status_code}")
    except Exception as e:
        log_test(test["name"], False, f"Error: {str(e)}")

# SECURITY TESTS
header("SECURITY & VALIDATION TESTS")

# Missing required field
try:
    resp = requests.post(
        f"{API_URL}/ai/classify/",
        headers=headers,
        json={"text": ""},
        timeout=10
    )
    log_test("Missing Required Field Validation", resp.status_code == 400,
            f"Status: {resp.status_code}")
except Exception as e:
    log_test("Missing Required Field Validation", False, f"Error: {str(e)}")

# Invalid token
try:
    bad_headers = {
        "Authorization": "Bearer invalid_token_xyz",
        "Content-Type": "application/json"
    }
    resp = requests.post(
        f"{API_URL}/ai/classify/",
        headers=bad_headers,
        json={"text": "test clause"},
        timeout=10
    )
    log_test("Invalid Token - 401 Unauthorized", resp.status_code == 401,
            f"Status: {resp.status_code}")
except Exception as e:
    log_test("Invalid Token - 401 Unauthorized", False, f"Error: {str(e)}")

# No auth header
try:
    resp = requests.post(
        f"{API_URL}/ai/classify/",
        headers={"Content-Type": "application/json"},
        json={"text": "test clause"},
        timeout=10
    )
    log_test("No Auth Header - 401 Unauthorized", resp.status_code == 401,
            f"Status: {resp.status_code}")
except Exception as e:
    log_test("No Auth Header - 401 Unauthorized", False, f"Error: {str(e)}")

# SUMMARY
header("TEST SUMMARY")
total = tests_passed + tests_failed
pass_rate = (tests_passed / total * 100) if total > 0 else 0
print(f"Total Tests:   {total}")
print(f"Passed:        {GREEN}{tests_passed}{RESET}")
print(f"Failed:        {RED}{tests_failed}{RESET}")
print(f"Pass Rate:     {YELLOW}{pass_rate:.0f}%{RESET}")
print()

if tests_failed == 0:
    print(f"{GREEN}✓ ALL TESTS PASSED - PRODUCTION READY{RESET}")
else:
    print(f"{YELLOW}⚠ {tests_passed}/{total} TESTS PASSED{RESET}")
