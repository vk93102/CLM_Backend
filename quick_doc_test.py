#!/usr/bin/env python
"""
Test document upload endpoint
"""
import requests
import json

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4NzIzNzE1LCJpYXQiOjE3Njg2MzczMTUsImp0aSI6IjU1OTU2MDJmMmU2ODQwMjFhMTU3YmVkY2EzM2YxNzZkIiwidXNlcl9pZCI6IjQzYzFkNDQyLWQ2N2UtNGUyNS1iYTM2LTkwNmU4Nzk3NzAwNSJ9.9URtf_ZgiTNrllW071ulW8fcjdRRpHDv4sQy5sX9ZaA"
BASE_URL = "http://localhost:8000"

# Create test file
print("Creating test contract file...")
test_content = """SERVICE AGREEMENT

Between ABC Corporation and XYZ Industries.

VALUE: $500,000 USD
DATE: January 1, 2024
TERMS: 2 years

PARTIES:
- ABC Corp: contact@abc.com, 123 Business St, New York
- XYZ Industries: contact@xyz.com, 456 Industry Ave, Los Angeles

KEY CLAUSES:
1. Payment due within 30 days
2. 99.9% uptime SLA
3. Confidentiality for 3 years
4. Termination with 90 days notice

RISK: Low
"""

file_path = "/tmp/sample_contract.txt"
with open(file_path, "w") as f:
    f.write(test_content)

print(f"✓ Created {file_path} ({len(test_content)} bytes)")

# Test upload
print("\nTesting document upload...")
headers = {"Authorization": f"Bearer {TOKEN}"}

with open(file_path, "rb") as f:
    files = {"file": (file_path.split("/")[-1], f, "text/plain")}
    data = {
        "document_type": "contract",
        "description": "Test service agreement"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/documents/ingest/",
        files=files,
        data=data,
        headers=headers
    )

print(f"Status: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")

if response.status_code in [200, 201]:
    result = response.json()
    doc_id = result.get("document_id")
    r2_key = result.get("r2_key")
    
    print(f"\n✓ Upload successful")
    print(f"  Document ID: {doc_id}")
    print(f"  R2 Key: {r2_key}")
    print(f"  Chunks: {result.get('chunk_count')}")
    
    # List documents
    print("\nListing documents...")
    list_response = requests.get(
        f"{BASE_URL}/api/documents/list/",
        headers=headers
    )
    
    print(f"Status: {list_response.status_code}")
    list_data = list_response.json()
    print(f"Total documents: {list_data.get('total')}")
    print(f"Documents:\n{json.dumps(list_data.get('documents', [])[:1], indent=2)}")
else:
    print(f"\n✗ Upload failed")
    print(f"Error: {response.text}")
