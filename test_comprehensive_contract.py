#!/usr/bin/env python
"""
Comprehensive contract upload test with real metadata extraction
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Get fresh token
print("="*70)
print("COMPREHENSIVE CONTRACT UPLOAD TEST")
print("="*70)

print("\n[1] Getting auth token...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login/",
    json={"email": "admin@clm.local", "password": "Admin@123"}
)

if login_response.status_code != 200:
    print(f"✗ Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access"]
print(f"✓ Authenticated")

# Create comprehensive test contract
print("\n[2] Creating comprehensive test contract...")
contract_content = """SERVICE AND SUPPORT AGREEMENT

This Service Agreement ("Agreement") is entered into effective as of January 15, 2024 ("Effective Date"), and expires December 31, 2025 ("Expiration Date"), between:

PARTIES:
"Service Provider": TechCorp Solutions Inc., a Delaware corporation with principal offices at 1500 Technology Boulevard, San Francisco, California 94107, USA
"Client": Global Industries Ltd., a United Kingdom corporation with principal offices at 2000 Oxford Street, London, England, United Kingdom

CONTRACT TERMS:

1. SERVICES AND SCOPE
   Client engages Service Provider to provide software development, cloud infrastructure management, and 24/7 technical support services.

2. PAYMENT TERMS
   - Total Contract Value: USD 750,000 for the two-year term
   - Annual Payment: USD 375,000 per year
   - Currency: US Dollars (USD)
   - Payment Schedule: Quarterly in advance (USD 93,750 per quarter)
   - Payment Due Date: Within 30 days of invoice
   - Late Payment Penalty: 1.5% per month compounded
   - Discounts: 5% discount if payment made within 15 days

3. SERVICE LEVELS
   - System Uptime Guarantee: 99.99%
   - Response Time: Critical issues within 2 hours, Standard within 8 hours
   - Monthly Availability Report required

4. CONFIDENTIALITY AND DATA PROTECTION
   - All information marked as confidential or proprietary
   - Non-disclosure obligations continue for 3 years after termination
   - GDPR and CCPA compliant data handling
   - Annual compliance audit required

5. LIABILITY AND INDEMNIFICATION
   - Maximum liability limited to contract value (USD 750,000)
   - Excludes indirect, incidental, consequential damages
   - Service Provider indemnifies Client for third-party IP claims
   - Client indemnifies Service Provider for data provided by Client

6. INTELLECTUAL PROPERTY RIGHTS
   - All pre-existing IP remains with owner
   - Custom work developed under this Agreement: 50% ownership each party
   - Client retains right to use software for business purposes

7. TERM AND TERMINATION
   - Initial term: 2 years from Effective Date
   - Auto-renewal: 1-year periods unless terminated
   - Either party may terminate with 90 days written notice
   - Immediate termination for material breach without cure period
   - Termination fee: 90 days service cost if terminated early

8. INSURANCE AND RISK MANAGEMENT
   - Service Provider maintains professional liability insurance (USD 2,000,000)
   - Service Provider maintains cyber liability insurance (USD 5,000,000)
   - Client responsible for backup and disaster recovery

9. DISPUTE RESOLUTION
   - Governed by laws of Delaware, USA
   - Binding arbitration in San Francisco, California
   - Prevailing party recovers reasonable attorney fees

10. FORCE MAJEURE
    - Neither party liable for events beyond reasonable control
    - Includes acts of God, war, natural disasters, pandemics

SPECIAL TERMS:
- Dedicated Account Manager: Yes
- 24/7 Technical Support: Yes
- Monthly Business Reviews: Required
- Annual ROI Assessment: Required

RISK ASSESSMENT:
- Overall Risk Level: Low-Medium (mostly standard commercial terms)
- Key Risks: Data security compliance, uptime guarantee costs
- Mitigation: Insurance coverage, audit trails, monitoring

SIGNATURES:
Service Provider: TechCorp Solutions Inc.
Authorized Representative: Sarah Johnson, VP of Sales
Date: January 15, 2024

Client: Global Industries Ltd.
Authorized Representative: Michael Chen, Chief Operations Officer
Date: January 15, 2024

AMENDMENT 1 (Dated March 1, 2024):
- Increased uptime guarantee from 99.9% to 99.99%
- Additional monthly compliance reporting required
"""

file_path = "/tmp/comprehensive_contract.txt"
with open(file_path, "w") as f:
    f.write(contract_content)

print(f"✓ Created contract file ({len(contract_content)} bytes)")

# Upload contract
print("\n[3] Uploading contract to system...")
headers = {"Authorization": f"Bearer {token}"}

with open(file_path, "rb") as f:
    files = {"file": ("comprehensive_contract.txt", f, "text/plain")}
    data = {
        "document_type": "contract",
        "description": "Comprehensive service agreement with full terms"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/documents/ingest/",
        files=files,
        data=data,
        headers=headers
    )

print(f"\n✓ Upload Status: {response.status_code}")

if response.status_code in [200, 201]:
    result = response.json()
    
    print("\n" + "="*70)
    print("UPLOAD RESULT")
    print("="*70)
    print(f"Document ID: {result.get('document_id')}")
    print(f"Filename: {result.get('filename')}")
    print(f"Status: {result.get('status')}")
    print(f"R2 Key: {result.get('r2_key')}")
    print(f"Chunks Created: {result.get('chunks_created')}")
    
    metadata = result.get('extracted_metadata', {})
    
    print("\n" + "="*70)
    print("EXTRACTED METADATA")
    print("="*70)
    
    # Parties
    parties = metadata.get('parties', [])
    print(f"\nParties ({len(parties)}):")
    for party in parties:
        print(f"  • {party}")
    
    # Contract Value
    contract_value = metadata.get('contract_value')
    currency = metadata.get('currency', 'USD')
    if contract_value:
        print(f"\nContract Value: {currency} {contract_value:,}")
    else:
        print(f"\nContract Value: NOT EXTRACTED")
    
    # Dates
    print(f"\nDates:")
    effective_date = metadata.get('effective_date')
    expiration_date = metadata.get('expiration_date')
    print(f"  Effective: {effective_date if effective_date else 'NOT EXTRACTED'}")
    print(f"  Expiration: {expiration_date if expiration_date else 'NOT EXTRACTED'}")
    
    # Clauses
    clauses = metadata.get('identified_clauses', [])
    print(f"\nIdentified Clauses ({len(clauses)}):")
    for clause in clauses:
        print(f"  • {clause}")
    
    # Summary
    summary = metadata.get('summary', '')
    print(f"\nSummary:")
    print(f"  {summary}")
    
    # Risk Score
    risk_score = metadata.get('risk_score')
    print(f"\nRisk Score: {risk_score if risk_score is not None else 'NOT EXTRACTED'}/100")
    
    # Redaction Summary
    redactions = metadata.get('redaction_counts', {})
    print(f"\nPII Redacted:")
    if redactions:
        for pii_type, count in redactions.items():
            print(f"  • {pii_type.upper()}: {count} instances")
    else:
        print(f"  • None detected")
    
    print("\n" + "="*70)
    print("FULL METADATA RESPONSE")
    print("="*70)
    print(json.dumps(metadata, indent=2))
    
    # Check for null values
    print("\n" + "="*70)
    print("VALIDATION")
    print("="*70)
    
    null_fields = []
    for field, value in metadata.items():
        if value is None or (isinstance(value, list) and len(value) == 0):
            null_fields.append(field)
    
    if null_fields:
        print(f"⚠ Fields with no extracted values: {', '.join(null_fields)}")
    else:
        print("✓ All fields successfully extracted with values!")
    
    # Test download
    print("\n[4] Testing document download...")
    r2_key = result.get('r2_key')
    if r2_key:
        dl_response = requests.get(
            f"{BASE_URL}/api/documents/download/?key={r2_key}",
            headers=headers
        )
        if dl_response.status_code == 200:
            dl_data = dl_response.json()
            presigned_url = dl_data.get('presigned_url')
            if presigned_url:
                print(f"✓ Presigned URL generated")
                print(f"  Expires: {dl_data.get('expires_in')} seconds")
            else:
                print(f"✗ No presigned URL in response: {dl_data}")
        else:
            print(f"✗ Download failed: {dl_response.status_code}")
    
    print("\n" + "="*70)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*70)
else:
    print(f"✗ Upload failed: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
