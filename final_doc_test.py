#!/usr/bin/env python
"""
Test document upload with fresh token
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Get fresh token
print("Getting auth token...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login/",
    json={
        "email": "admin@clm.local",
        "password": "Admin@123"
    }
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access"]
print(f"✓ Got token")

# Create test file
print("\nCreating test contract...")
test_content = "SERVICE AGREEMENT\n\nParties: ABC Corp and XYZ Industries\nValue: $500,000 USD\nDate: January 1, 2024\nTerms: 2 years\nPayment: 30 days\nConfidentiality: 3 years\nRisk: Low"

with open("/tmp/contract2.txt", "w") as f:
    f.write(test_content)

print(f"✓ Created contract file")

# Upload
print("\nUploading document...")
headers = {"Authorization": f"Bearer {token}"}

with open("/tmp/contract2.txt", "rb") as f:
    files = {"file": ("contract2.txt", f, "text/plain")}
    data = {"document_type": "contract", "description": "Test"}
    
    response = requests.post(
        f"{BASE_URL}/api/documents/ingest/",
        files=files,
        data=data,
        headers=headers
    )

print(f"Status: {response.status_code}")
result = response.json()
print(json.dumps(result, indent=2))

if response.status_code in [200, 201]:
    print(f"\n✓ Document uploaded successfully")
    print(f"  ID: {result.get('document_id')}")
    print(f"  R2 Key: {result.get('r2_key')}")
    print(f"  Status: {result.get('status')}")
    
    # Test download
    print("\nTesting download...")
    r2_key = result.get('r2_key')
    if r2_key:
        dl_response = requests.get(
            f"{BASE_URL}/api/documents/download/?key={r2_key}",
            headers=headers
        )
        print(f"Download Status: {dl_response.status_code}")
        if dl_response.status_code == 200:
            dl_data = dl_response.json()
            print(f"✓ Presigned URL: {dl_data.get('presigned_url', 'NOT SET')[:80]}...")
