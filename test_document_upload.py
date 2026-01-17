#!/usr/bin/env python
"""
Test document upload and processing endpoints
Tests the complete document ingestion pipeline
"""

import requests
import json
import sys
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def login():
    """Login as admin and get auth token"""
    print_section("Step 1: Admin Login")
    
    login_data = {
        "email": "admin@clm.local",
        "password": "Admin@123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login/",
        json=login_data
    )
    
    print(f"Login URL: POST {BASE_URL}/api/auth/login/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        token = response.json().get("access")
        print(f"✓ Login successful - Token: {token[:20]}...")
        return token
    else:
        print(f"✗ Login failed")
        return None

def create_test_pdf():
    """Create a sample PDF file for testing"""
    print_section("Step 2: Creating Test Files")
    
    # Create a simple text file
    txt_file = "/tmp/sample_contract.txt"
    with open(txt_file, "w") as f:
        f.write("""
SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into as of January 1, 2024, 
between ABC Corporation ("Service Provider") and XYZ Industries ("Client").

PARTIES:
- Service Provider: ABC Corporation, Address: 123 Business St, New York, NY 10001
- Client: XYZ Industries, Address: 456 Industry Ave, Los Angeles, CA 90001
- Contact Email: contact@xyindustries.com
- Phone: +1-555-0123

CONTRACT VALUE: $500,000 USD per annum

EFFECTIVE DATE: January 1, 2024
EXPIRATION DATE: December 31, 2025

KEY TERMS AND CONDITIONS:

1. SERVICE DELIVERY
   - Services shall be delivered within 5 business days
   - Uptime guarantee: 99.9%
   - Response time: 24 hours for critical issues

2. PAYMENT TERMS
   - Payment due within 30 days of invoice
   - Late payment penalty: 1.5% per month

3. CONFIDENTIALITY
   - All information marked as confidential must be protected
   - Non-disclosure obligations continue for 3 years post-termination

4. LIABILITY LIMITATIONS
   - Maximum liability: Contract value * 1.5
   - Excludes indirect or consequential damages

5. TERMINATION CLAUSE
   - Either party may terminate with 90 days written notice
   - Immediate termination for material breach

OBLIGATIONS:
- Service Provider: Maintain service quality, provide 24/7 support, quarterly reporting
- Client: Timely payment, access provision, feedback communication

RISK ASSESSMENT:
- Low risk: Standard commercial terms
- No unusual liabilities
- Standard payment terms (30 days)

SIGNATURES:
_________________________          _________________________
ABC Corporation                    XYZ Industries
CEO: John Smith                    CEO: Jane Doe
Date: January 1, 2024            Date: January 1, 2024
""")
    print(f"✓ Created test file: {txt_file}")
    return txt_file

def upload_document(token, file_path):
    """Upload document and test processing pipeline"""
    print_section("Step 3: Document Upload & Processing")
    
    file_name = Path(file_path).name
    
    with open(file_path, "rb") as f:
        files = {
            "file": (file_name, f, "text/plain")
        }
        data = {
            "document_type": "contract",
            "description": "Sample service agreement for testing"
        }
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/ingest/",
            files=files,
            data=data,
            headers=headers
        )
    
    print(f"Upload URL: POST {BASE_URL}/api/documents/ingest/")
    print(f"File: {file_name}")
    print(f"Status Code: {response.status_code}")
    
    try:
        result = response.json()
        print(f"Response:\n{json.dumps(result, indent=2)}")
        
        if response.status_code in [200, 201]:
            print("\n✓ Upload successful")
            return result
        else:
            print("\n✗ Upload failed")
            return None
    except:
        print(f"Response Text: {response.text}")
        return None

def list_documents(token):
    """List all uploaded documents"""
    print_section("Step 4: List Documents")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/documents/list/?limit=10",
        headers=headers
    )
    
    print(f"List URL: GET {BASE_URL}/api/documents/list/")
    print(f"Status Code: {response.status_code}")
    
    try:
        result = response.json()
        print(f"Response:\n{json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print(f"\n✓ Found {result.get('total', 0)} documents")
            return result
        else:
            print("\n✗ Failed to list documents")
            return None
    except:
        print(f"Response Text: {response.text}")
        return None

def download_document(token, r2_key):
    """Get presigned download URL"""
    print_section("Step 5: Download Document")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/documents/download/?key={r2_key}",
        headers=headers
    )
    
    print(f"Download URL: GET {BASE_URL}/api/documents/download/")
    print(f"R2 Key: {r2_key}")
    print(f"Status Code: {response.status_code}")
    
    try:
        result = response.json()
        print(f"Response:\n{json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print("\n✓ Presigned URL generated")
            return result
        else:
            print("\n✗ Failed to generate download URL")
            return None
    except:
        print(f"Response Text: {response.text}")
        return None

def get_metadata(token, document_id):
    """Get extracted metadata"""
    print_section("Step 6: View Extracted Metadata")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/documents/",
        headers=headers
    )
    
    print(f"Metadata URL: GET {BASE_URL}/api/documents/")
    print(f"Status Code: {response.status_code}")
    
    try:
        result = response.json()
        print(f"Response:\n{json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print("\n✓ Retrieved metadata")
            return result
        else:
            print("\n✗ Failed to retrieve metadata")
            return None
    except:
        print(f"Response Text: {response.text}")
        return None

def run_all_tests():
    """Run complete test suite"""
    print_section("Document Upload Testing Suite")
    print("Testing complete document ingestion pipeline")
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n✗ Cannot proceed without auth token")
        return False
    
    time.sleep(1)
    
    # Step 2: Create test files
    test_file = create_test_pdf()
    
    time.sleep(1)
    
    # Step 3: Upload document
    upload_result = upload_document(token, test_file)
    if not upload_result:
        print("\n✗ Upload failed")
        return False
    
    document_id = upload_result.get("document_id")
    r2_key = upload_result.get("r2_key")
    
    time.sleep(2)  # Wait for processing
    
    # Step 4: List documents
    list_result = list_documents(token)
    
    time.sleep(1)
    
    # Step 5: Download document (if R2 key available)
    if r2_key:
        download_result = download_document(token, r2_key)
    
    time.sleep(1)
    
    # Step 6: Get metadata
    if document_id:
        metadata_result = get_metadata(token, document_id)
    
    print_section("Test Summary")
    print("✓ All tests completed")
    print(f"Document ID: {document_id}")
    print(f"R2 Key: {r2_key}")
    print(f"Status: Processing")
    print("\nNext steps:")
    print("1. Check /api/documents/list/ to see processed documents")
    print("2. Download using presigned URL")
    print("3. View extracted metadata (parties, dates, values, clauses)")
    
    return True

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
