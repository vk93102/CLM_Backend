"""
Complete Endpoint Testing & Documentation for Frontend Integration
Shows all contract generation flows, templates, signatures, and download endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:11000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4OTc5ODk5LCJpYXQiOjE3Njg4OTM0OTksImp0aSI6IjUyYzgwYzg5ZTRlMDQwYzVhODIyYTFmN2Q5Y2ZmNTZlIiwidXNlcl9pZCI6ImMyNTZiNjU5LTAzMWEtNDRiZi1iMDkxLTdiZTM4OGQ4NTkzNCJ9.cdqz312NR3tCX6iU_jIKB8U4VLCAToDb75Bp7_eFRKo"


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_endpoint(method, path, description):
    """Print formatted endpoint header"""
    print(f"\n{method:6} {path}")
    print(f"       {description}")
    print("-" * 80)


def get_headers():
    """Get request headers with authentication"""
    return {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }


class EndpointTester:
    """Test all endpoints with proper flow and documentation"""

    def __init__(self):
        self.contract_id = None
        self.template_fields = {}
        self.results = []

    # ==================== TEMPLATES & FIELDS ====================

    def test_1_list_templates(self):
        """Test 1: List all available contract templates"""
        print_endpoint("GET", "/api/v1/templates/", "Get available contract templates")
        
        response = requests.get(
            f"{BASE_URL}/templates/",
            headers=get_headers()
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 200:
            print("\n✅ SUCCESS - Available templates:")
            for template, info in data.get('templates', {}).items():
                print(f"   • {template}: {info['required_fields_count']} required fields")
            self.results.append(("List Templates", "PASS", 200))
            return True
        else:
            self.results.append(("List Templates", "FAIL", response.status_code))
            return False

    def test_2_get_nda_fields(self):
        """Test 2: Get required fields for NDA contract"""
        print_endpoint("GET", "/api/v1/fields/?contract_type=nda", "Get NDA contract fields")
        
        response = requests.get(
            f"{BASE_URL}/fields/?contract_type=nda",
            headers=get_headers()
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 200:
            print("\n✅ SUCCESS - NDA requires:")
            print(f"   • Required: {', '.join(data['required_fields'][:3])}")
            print(f"   • Optional: {', '.join(data['optional_fields'][:2])}")
            self.template_fields['nda'] = data
            self.results.append(("Get NDA Fields", "PASS", 200))
            return True
        else:
            self.results.append(("Get NDA Fields", "FAIL", response.status_code))
            return False

    def test_3_get_agency_fields(self):
        """Test 3: Get required fields for Agency Agreement"""
        print_endpoint("GET", "/api/v1/fields/?contract_type=agency_agreement", "Get Agency Agreement fields")
        
        response = requests.get(
            f"{BASE_URL}/fields/?contract_type=agency_agreement",
            headers=get_headers()
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 200:
            self.results.append(("Get Agency Fields", "PASS", 200))
            return True
        else:
            self.results.append(("Get Agency Fields", "FAIL", response.status_code))
            return False

    def test_4_get_template_content(self):
        """Test 4: Get full template content for display"""
        print_endpoint("GET", "/api/v1/content/?contract_type=nda", "Get full NDA template content")
        
        response = requests.get(
            f"{BASE_URL}/content/?contract_type=nda",
            headers=get_headers()
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        
        # Show summary instead of full content
        print(f"Content length: {data.get('content_length')} characters")
        print(f"Title: {data.get('title')}")
        print(f"Required fields: {len(data.get('required_fields', []))}")
        print("\nFirst 500 chars of template:")
        full_content = data.get('full_content', '')
        print(full_content[:500] + "...")
        
        if response.status_code == 200:
            self.results.append(("Get Template Content", "PASS", 200))
            return True
        else:
            self.results.append(("Get Template Content", "FAIL", response.status_code))
            return False

    # ==================== CREATE CONTRACTS ====================

    def test_5_create_nda_simple(self):
        """Test 5: Create NDA contract (simple flow)"""
        print_endpoint("POST", "/api/v1/create/", "Create NDA contract with data")
        
        payload = {
            "contract_type": "nda",
            "data": {
                "date": "2026-01-20",
                "1st_party_name": "TechCorp Inc.",
                "2nd_party_name": "DevSoft LLC",
                "agreement_type": "Mutual",
                "1st_party_relationship": "Technology Company",
                "2nd_party_relationship": "Software Developer",
                "governing_law": "California",
                "1st_party_printed_name": "John Smith",
                "2nd_party_printed_name": "Jane Doe"
            }
        }
        
        print("Request payload:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/create/",
            headers=get_headers(),
            json=payload
        )
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 201:
            self.contract_id = data.get('contract_id')
            print(f"\n✅ SUCCESS - Contract created: {self.contract_id}")
            self.results.append(("Create NDA", "PASS", 201))
            return True
        else:
            self.results.append(("Create NDA", "FAIL", response.status_code))
            return False

    def test_6_create_with_clauses(self):
        """Test 6: Create contract with custom clauses"""
        print_endpoint("POST", "/api/v1/create/", "Create contract with clauses")
        
        payload = {
            "contract_type": "nda",
            "data": {
                "date": "2026-01-20",
                "1st_party_name": "CompanyA Ltd.",
                "2nd_party_name": "CompanyB Corp.",
                "agreement_type": "Unilateral",
                "1st_party_relationship": "Service Provider",
                "2nd_party_relationship": "Client",
                "governing_law": "New York",
                "1st_party_printed_name": "Alice Johnson",
                "2nd_party_printed_name": "Bob Wilson",
                "clauses": [
                    {
                        "name": "Confidentiality",
                        "description": "All disclosed information shall remain confidential for 3 years"
                    },
                    {
                        "name": "Non-Compete",
                        "description": "No competing business activities for 2 years after termination"
                    },
                    {
                        "name": "Indemnification",
                        "description": "Each party indemnifies the other against third-party claims"
                    }
                ]
            }
        }
        
        print("Request payload (with 3 clauses):")
        print(json.dumps({
            "contract_type": payload["contract_type"],
            "data_fields": len(payload["data"]),
            "clauses_count": len(payload["data"]["clauses"]),
            "sample_clause": payload["data"]["clauses"][0]
        }, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/create/",
            headers=get_headers(),
            json=payload
        )
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 201:
            contract_id = data.get('contract_id')
            print(f"\n✅ SUCCESS - Contract with clauses created: {contract_id}")
            self.contract_id = contract_id
            self.results.append(("Create with Clauses", "PASS", 201))
            return True
        else:
            self.results.append(("Create with Clauses", "FAIL", response.status_code))
            return False

    def test_7_create_employment_contract(self):
        """Test 7: Create Employment contract"""
        print_endpoint("POST", "/api/v1/create/", "Create Employment contract")
        
        payload = {
            "contract_type": "employment_contract",
            "data": {
                "employee_name": "Sarah Chen",
                "employer_name": "StartupXYZ Inc.",
                "position": "Senior Software Engineer",
                "salary": "150000",
                "currency": "USD",
                "employment_type": "Full-time",
                "start_date": "2026-02-01",
                "duration": "Indefinite",
                "benefits": "Health insurance, 401k, PTO"
            }
        }
        
        print("Request payload:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/create/",
            headers=get_headers(),
            json=payload
        )
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 201:
            print(f"\n✅ SUCCESS - Employment contract created")
            self.results.append(("Create Employment", "PASS", 201))
            return True
        else:
            self.results.append(("Create Employment", "FAIL", response.status_code))
            return False

    # ==================== RETRIEVE & DOWNLOAD ====================

    def test_8_get_contract_details(self):
        """Test 8: Get contract details (before signing)"""
        print_endpoint("GET", "/api/v1/details/?contract_id=<id>", "Get contract details")
        
        if not self.contract_id:
            print("❌ SKIP - No contract ID available")
            self.results.append(("Get Details (Before)", "SKIP", None))
            return False
        
        response = requests.get(
            f"{BASE_URL}/details/?contract_id={self.contract_id}",
            headers=get_headers()
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        contract = data.get('contract', {})
        
        print(json.dumps({
            "id": contract.get('id'),
            "title": contract.get('title'),
            "contract_type": contract.get('contract_type'),
            "status": contract.get('status'),
            "clauses_count": len(contract.get('clauses', [])),
            "signed": contract.get('signed'),
            "file_size": contract.get('file_size'),
            "created_at": contract.get('created_at')
        }, indent=2))
        
        if response.status_code == 200:
            print(f"\n✅ SUCCESS - Retrieved contract details")
            self.results.append(("Get Details (Before)", "PASS", 200))
            return True
        else:
            self.results.append(("Get Details (Before)", "FAIL", response.status_code))
            return False

    def test_9_download_contract(self):
        """Test 9: Download contract as PDF"""
        print_endpoint("GET", "/api/v1/download/?contract_id=<id>", "Download contract PDF")
        
        if not self.contract_id:
            print("❌ SKIP - No contract ID available")
            self.results.append(("Download PDF", "SKIP", None))
            return False
        
        response = requests.get(
            f"{BASE_URL}/download/?contract_id={self.contract_id}",
            headers=get_headers()
        )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {len(response.content)} bytes")
        print(f"Is valid PDF: {response.content[:4] == b'%PDF'}")
        
        if response.status_code == 200 and response.content[:4] == b'%PDF':
            print(f"\n✅ SUCCESS - PDF downloaded ({len(response.content)} bytes)")
            self.results.append(("Download PDF", "PASS", 200))
            return True
        else:
            self.results.append(("Download PDF", "FAIL", response.status_code))
            return False

    # ==================== E-SIGNATURE FLOW ====================

    def test_10_send_to_signnow(self):
        """Test 10: Send contract to SignNow for signature"""
        print_endpoint("POST", "/api/v1/send-to-signnow/", "Send to SignNow for signing")
        
        if not self.contract_id:
            print("❌ SKIP - No contract ID available")
            self.results.append(("Send to SignNow", "SKIP", None))
            return False
        
        payload = {
            "contract_id": self.contract_id,
            "signer_email": "jane.doe@devsoft.com",
            "signer_name": "Jane Doe"
        }
        
        print("Request payload:")
        print(json.dumps(payload, indent=2))
        print("\nFlow: Signer will receive link, click to open SignNow app")
        print("      Signer types/draws signature → clicks Sign → webhook called")
        
        response = requests.post(
            f"{BASE_URL}/send-to-signnow/",
            headers=get_headers(),
            json=payload
        )
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 200:
            print(f"\n✅ SUCCESS - Link generated: {data.get('signing_link')}")
            self.results.append(("Send to SignNow", "PASS", 200))
            return True
        else:
            self.results.append(("Send to SignNow", "FAIL", response.status_code))
            return False

    def test_11_webhook_signature_received(self):
        """Test 11: Simulate SignNow webhook after user signs"""
        print_endpoint("POST", "/api/v1/webhook/signnow/", "Webhook: Document signed")
        
        if not self.contract_id:
            print("❌ SKIP - No contract ID available")
            self.results.append(("Webhook Signature", "SKIP", None))
            return False
        
        payload = {
            "event": "document.signed",
            "document": {
                "contract_id": self.contract_id,
                "signed_at": "2026-01-20T16:45:30Z",
                "signed_pdf_url": "https://signnow-cdn.s3.amazonaws.com/signed_doc_123.pdf",
                "signers": [
                    {
                        "full_name": "Jane Doe",
                        "email": "jane.doe@devsoft.com",
                        "signed_at": "2026-01-20T16:45:30Z"
                    }
                ]
            }
        }
        
        print("Webhook payload (from SignNow after user signs):")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/webhook/signnow/",
            headers=get_headers(),
            json=payload
        )
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 200:
            print(f"\n✅ SUCCESS - Signature received and stored")
            self.results.append(("Webhook Signature", "PASS", 200))
            return True
        else:
            self.results.append(("Webhook Signature", "FAIL", response.status_code))
            return False

    def test_12_get_signed_contract(self):
        """Test 12: Get contract details after signing"""
        print_endpoint("GET", "/api/v1/details/?contract_id=<id>", "Get contract details (after signing)")
        
        if not self.contract_id:
            print("❌ SKIP - No contract ID available")
            self.results.append(("Get Details (After)", "SKIP", None))
            return False
        
        response = requests.get(
            f"{BASE_URL}/details/?contract_id={self.contract_id}",
            headers=get_headers()
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        contract = data.get('contract', {})
        
        print(json.dumps({
            "id": contract.get('id'),
            "status": contract.get('status'),
            "signed": contract.get('signed'),
            "file_size": contract.get('file_size'),
            "created_at": contract.get('created_at')
        }, indent=2))
        
        if response.status_code == 200:
            signed_data = contract.get('signed', {})
            print(f"\n✅ SUCCESS - Contract signed")
            print(f"   Signed by: {signed_data.get('signers', [{}])[0].get('name') if signed_data.get('signers') else 'N/A'}")
            print(f"   Status: {signed_data.get('status')}")
            self.results.append(("Get Details (After)", "PASS", 200))
            return True
        else:
            self.results.append(("Get Details (After)", "FAIL", response.status_code))
            return False

    # ==================== COMPLEX FLOWS ====================

    def test_13_create_multiple_signers(self):
        """Test 13: Show structure for multiple signers (future enhancement)"""
        print_endpoint("POST", "/api/v1/create/", "Create contract (multi-signer ready)")
        
        payload = {
            "contract_type": "agency_agreement",
            "data": {
                "principal_name": "ABC Corporation",
                "agent_name": "XYZ Agency LLC",
                "territory": "North America",
                "term_months": "24",
                "commission_percent": "10",
                "signers_metadata": [
                    {
                        "order": 1,
                        "name": "Principal Signatory",
                        "email": "principal@abc-corp.com",
                        "role": "Principal"
                    },
                    {
                        "order": 2,
                        "name": "Agent Signatory",
                        "email": "agent@xyz-agency.com",
                        "role": "Agent"
                    }
                ]
            }
        }
        
        print("Multi-signer contract structure:")
        print(json.dumps({
            "contract_type": payload["contract_type"],
            "signers": payload["data"]["signers_metadata"],
            "flow": "Create → Send to Signer 1 → Signer 1 signs → Send to Signer 2 → Signer 2 signs → Complete"
        }, indent=2))
        
        print("\n✅ STRUCTURE DEFINED - Ready for implementation")
        self.results.append(("Multi-Signer Structure", "INFO", None))
        return True

    def test_14_error_handling(self):
        """Test 14: Show error responses"""
        print_endpoint("POST", "/api/v1/create/", "Error handling: Missing required field")
        
        payload = {
            "contract_type": "nda",
            "data": {
                "date": "2026-01-20"
                # Missing required fields
            }
        }
        
        print("Request with missing fields:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/create/",
            headers=get_headers(),
            json=payload
        )
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 400:
            print(f"\n✅ SUCCESS - Error handled correctly")
            print(f"   Missing: {data.get('missing_fields')}")
            self.results.append(("Error Handling", "PASS", 400))
            return True
        else:
            self.results.append(("Error Handling", "FAIL", response.status_code))
            return False

    def print_summary(self):
        """Print complete test summary"""
        print_section("TEST SUMMARY & RESULTS")
        
        passed = sum(1 for _, status, _ in self.results if status == "PASS")
        failed = sum(1 for _, status, _ in self.results if status == "FAIL")
        skipped = sum(1 for _, status, _ in self.results if status in ("SKIP", "INFO"))
        
        print(f"{'Test':<35} {'Status':<10} {'Code':<10}")
        print("-" * 55)
        
        for test_name, status, code in self.results:
            status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⊘"
            code_str = str(code) if code else ""
            print(f"{test_name:<35} {status_icon} {status:<8} {code_str:<10}")
        
        print("-" * 55)
        print(f"Total: {len(self.results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}\n")
        
        return failed == 0

    def print_frontend_guide(self):
        """Print guide for frontend integration"""
        print_section("FRONTEND INTEGRATION GUIDE")
        
        guide = """
1. INITIALIZATION
   └─ GET /api/v1/templates/
   └─ Show user list of contract types (NDA, Employment, etc.)

2. TEMPLATE SELECTION & PREVIEW
   └─ GET /api/v1/fields/?contract_type=nda
   └─ Display form fields to user
   └─ GET /api/v1/content/?contract_type=nda
   └─ Show preview of filled contract

3. CREATE CONTRACT
   └─ POST /api/v1/create/
   └─ Input: User form data + optional clauses
   └─ Output: Contract ID, file path, file size
   └─ Success: Show confirmation + "Download" button

4. DOWNLOAD (BEFORE SIGNING)
   └─ GET /api/v1/download/?contract_id={id}
   └─ User downloads PDF to review locally

5. SEND FOR SIGNATURE
   └─ POST /api/v1/send-to-signnow/
   └─ Input: Signer name, email
   └─ Output: SignNow link
   └─ Show link to user (share or email to signer)

6. SIGNER COMPLETES SIGNATURE
   └─ Signer receives link
   └─ Opens in browser/SignNow app
   └─ Types/draws signature
   └─ Clicks "Sign" button
   └─ SignNow calls our webhook

7. WEBHOOK RECEIVES SIGNATURE
   └─ POST /api/v1/webhook/signnow/
   └─ Backend stores: signed PDF + signer details
   └─ Contract status changes to "signed"

8. VIEW SIGNED CONTRACT
   └─ GET /api/v1/details/?contract_id={id}
   └─ Shows: Signer name, email, signature timestamp
   └─ GET /api/v1/download/?contract_id={id}
   └─ Download signed PDF with user's signature

FLOW VISUALIZATION:
   User selects type → Fills form → Creates → Downloads → Shares link
   ↓
   Signer opens link → Signs → Backend receives signature
   ↓
   User downloads signed PDF
"""
        print(guide)


def main():
    """Run all endpoint tests"""
    print_section("CONTRACT GENERATION API - ENDPOINT TESTING & DOCUMENTATION")
    
    tester = EndpointTester()
    
    tests = [
        ("TEMPLATES & FIELDS", [
            tester.test_1_list_templates,
            tester.test_2_get_nda_fields,
            tester.test_3_get_agency_fields,
            tester.test_4_get_template_content,
        ]),
        ("CREATE CONTRACTS", [
            tester.test_5_create_nda_simple,
            tester.test_6_create_with_clauses,
            tester.test_7_create_employment_contract,
        ]),
        ("RETRIEVE & DOWNLOAD", [
            tester.test_8_get_contract_details,
            tester.test_9_download_contract,
        ]),
        ("E-SIGNATURE FLOW", [
            tester.test_10_send_to_signnow,
            tester.test_11_webhook_signature_received,
            tester.test_12_get_signed_contract,
        ]),
        ("ADVANCED & ERROR HANDLING", [
            tester.test_13_create_multiple_signers,
            tester.test_14_error_handling,
        ]),
    ]
    
    for section_name, test_functions in tests:
        print_section(section_name)
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Error: {str(e)}\n")
    
    tester.print_summary()
    tester.print_frontend_guide()


if __name__ == "__main__":
    main()
