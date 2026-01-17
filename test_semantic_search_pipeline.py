#!/usr/bin/env python
"""
Comprehensive Test Suite for Semantic Search Pipeline
Tests: Document Upload → Embedding Generation → Semantic/Keyword/Hybrid Search
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000/api"
ADMIN_CREDENTIALS = {
    "email": "admin@example.com",
    "password": "TestPassword123!"
}

# Sample contract document
SAMPLE_CONTRACT = """
SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into as of January 1, 2024, between ABC Corporation, a Delaware corporation ("Provider"), and XYZ Industries, a California corporation ("Client").

1. SERVICES AND DELIVERABLES

1.1 Provider agrees to provide comprehensive software development services including system design, implementation, testing, and deployment. The services shall include technical consulting, code review, documentation, and post-deployment support as outlined in Appendix A.

1.2 The deliverables shall include: (a) source code in version control, (b) technical documentation, (c) automated test suites with minimum 80% code coverage, and (d) deployment guides.

2. CONFIDENTIALITY AND INTELLECTUAL PROPERTY

2.1 Each party agrees to maintain the confidentiality of all proprietary information, trade secrets, and confidential business information disclosed during the term of this Agreement and for five (5) years thereafter.

2.2 All work product, code, designs, and documentation created by Provider shall be the exclusive property of Client upon full payment of fees. Provider retains ownership of pre-existing materials and tools.

2.3 Client shall not disclose Provider's confidential information to third parties without prior written consent, except as required by law.

3. TERM AND TERMINATION

3.1 This Agreement shall commence on the Effective Date and continue for an initial term of twelve (12) months, unless earlier terminated. After the initial term, this Agreement shall automatically renew for successive twelve-month periods.

3.2 Either party may terminate this Agreement for convenience upon sixty (60) days' written notice. Client shall pay for all services rendered up to the termination date.

3.3 Provider may terminate immediately if Client materially breaches any provision and fails to cure within fifteen (15) days of written notice.

3.4 Upon termination, Client shall pay all outstanding invoices and Provider shall return or destroy all Client's confidential information.

4. LIABILITY AND INDEMNIFICATION

4.1 LIMITATION OF LIABILITY: EXCEPT AS OTHERWISE PROVIDED IN THIS AGREEMENT, IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING LOST PROFITS, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

4.2 Provider's total liability under this Agreement shall not exceed the fees paid by Client in the twelve (12) months preceding the claim.

4.3 Each party shall indemnify, defend, and hold harmless the other party from any claims, damages, and costs arising from the indemnifying party's breach of this Agreement, negligence, or violation of applicable law.

4.4 Client assumes all liability for third-party claims related to Client's use of the services outside the scope authorized by Provider.

5. PAYMENT TERMS

5.1 Client shall pay Provider based on the fee schedule in Appendix B. Invoices are due within thirty (30) days of receipt.

5.2 Late payments shall accrue interest at 1.5% per month or the maximum rate allowed by law, whichever is less.

5.3 Provider may suspend services if payment is more than fifteen (15) days overdue.

6. WARRANTIES AND DISCLAIMERS

6.1 Provider warrants that services shall be performed in a professional manner consistent with industry standards.

6.2 EXCEPT AS EXPRESSLY PROVIDED, PROVIDER MAKES NO OTHER WARRANTIES, EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.

6.3 Client's exclusive remedy for any warranty breach shall be reperformance of the services.

7. DISPUTE RESOLUTION

7.1 Any disputes shall first be addressed through good faith negotiation between senior representatives of both parties.

7.2 If negotiation fails, disputes shall be submitted to binding arbitration under the American Arbitration Association (AAA) rules.

7.3 Each party shall bear its own attorneys' fees and costs, except as awarded by the arbitrator.

8. GENERAL PROVISIONS

8.1 This Agreement constitutes the entire agreement and supersedes all prior understandings.

8.2 Neither party may assign this Agreement without written consent of the other party.

8.3 This Agreement shall be governed by and construed in accordance with the laws of Delaware, without regard to conflict of law principles.

8.4 If any provision is found invalid, the remaining provisions shall continue in full force and effect.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

ABC CORPORATION

By: ___________________________
Name: _________________________
Title: __________________________
Date: ___________________________

XYZ INDUSTRIES

By: ___________________________
Name: _________________________
Title: __________________________
Date: ___________________________
"""

class SearchPipelineTester:
    def __init__(self, base_url, credentials):
        self.base_url = base_url
        self.credentials = credentials
        self.token = None
        self.document_id = None
        self.session = requests.Session()
        
    def authenticate(self):
        """Authenticate and get JWT token"""
        print("\n[TEST 1] Authenticating...")
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login/",
                json=self.credentials,
                timeout=10
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access')
                print(f"✓ Authentication successful. Token: {self.token[:20]}...")
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                })
                return True
            else:
                print(f"✗ Authentication failed: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def upload_document(self):
        """Upload contract document"""
        print("\n[TEST 2] Uploading contract document...")
        try:
            # Create a temporary file
            temp_file = "/tmp/sample_contract.txt"
            with open(temp_file, 'w') as f:
                f.write(SAMPLE_CONTRACT)
            
            files = {
                'file': ('sample_contract.txt', open(temp_file, 'rb'), 'text/plain'),
                'document_type': (None, 'SERVICE_AGREEMENT'),
                'metadata': (None, json.dumps({
                    'source': 'legal_department',
                    'importance': 'high'
                }))
            }
            
            response = self.session.post(
                f"{self.base_url}/documents/ingest/",
                files=files,
                timeout=30
            )
            
            # Close file
            files['file'][1].close()
            
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.document_id = data.get('document_id')
                print(f"✓ Document uploaded successfully")
                print(f"  Document ID: {self.document_id}")
                print(f"  Chunks created: {data.get('chunks_count', 'N/A')}")
                print(f"  Embeddings generated: {data.get('embeddings_count', 'N/A')}")
                print(f"  Metadata extracted: {data.get('metadata_extracted', False)}")
                return True
            else:
                print(f"✗ Upload failed: {response.text[:500]}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_semantic_search(self):
        """Test semantic search"""
        print("\n[TEST 3] Testing semantic search...")
        try:
            queries = [
                "confidentiality obligations",
                "liability limitation",
                "termination clause",
                "payment terms"
            ]
            
            for query in queries:
                print(f"\n  Query: '{query}'")
                response = self.session.get(
                    f"{self.base_url}/search/semantic/",
                    params={
                        'q': query,
                        'top_k': 5,
                        'threshold': 0.3
                    },
                    timeout=15
                )
                
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    count = data.get('count', 0)
                    print(f"  ✓ Results found: {count}")
                    
                    for i, result in enumerate(data.get('results', [])[:3], 1):
                        print(f"    {i}. Chunk #{result.get('chunk_number')} - Score: {result.get('similarity_score', 'N/A'):.3f}")
                        text_preview = result.get('text', '')[:100]
                        print(f"       Text: {text_preview}...")
                else:
                    print(f"  ✗ Search failed: {response.text[:200]}")
                    
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def test_keyword_search(self):
        """Test keyword search"""
        print("\n[TEST 4] Testing keyword search...")
        try:
            queries = [
                "confidentiality",
                "termination",
                "liability"
            ]
            
            for query in queries:
                print(f"\n  Query: '{query}'")
                response = self.session.get(
                    f"{self.base_url}/search/keyword/",
                    params={
                        'q': query,
                        'limit': 5
                    },
                    timeout=15
                )
                
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    count = data.get('count', 0)
                    print(f"  ✓ Results found: {count}")
                    
                    for i, result in enumerate(data.get('results', [])[:3], 1):
                        print(f"    {i}. Chunk #{result.get('chunk_number')}")
                else:
                    print(f"  ✗ Search failed: {response.text[:200]}")
                    
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def test_hybrid_search(self):
        """Test hybrid search"""
        print("\n[TEST 5] Testing hybrid search...")
        try:
            query = "intellectual property rights"
            print(f"  Query: '{query}'")
            
            response = self.session.get(
                f"{self.base_url}/search/hybrid/",
                params={
                    'q': query,
                    'top_k': 5,
                    'semantic_weight': 0.7,
                    'keyword_weight': 0.3
                },
                timeout=15
            )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                print(f"  ✓ Results found: {count}")
                
                for i, result in enumerate(data.get('results', [])[:5], 1):
                    print(f"    {i}. Chunk #{result.get('chunk_number')} - Score: {result.get('similarity_score', 'N/A'):.3f}")
            else:
                print(f"  ✗ Search failed: {response.text[:200]}")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def test_search_stats(self):
        """Test search statistics"""
        print("\n[TEST 6] Testing search statistics...")
        try:
            response = self.session.get(
                f"{self.base_url}/search/stats/",
                timeout=15
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Statistics retrieved:")
                print(f"  Total documents: {data.get('total_documents', 'N/A')}")
                print(f"  Total chunks: {data.get('total_chunks', 'N/A')}")
                print(f"  Chunks with embeddings: {data.get('chunks_with_embeddings', 'N/A')}")
                
                clauses = data.get('clause_statistics', {})
                if clauses:
                    print(f"  Clause statistics:")
                    for clause_type, count in list(clauses.items())[:5]:
                        print(f"    - {clause_type}: {count}")
            else:
                print(f"✗ Failed: {response.text[:200]}")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 70)
        print("SEMANTIC SEARCH PIPELINE TEST SUITE")
        print("=" * 70)
        
        if not self.authenticate():
            print("\n✗ Authentication failed. Stopping tests.")
            return False
        
        if not self.upload_document():
            print("\n✗ Document upload failed. Stopping tests.")
            return False
        
        # Wait for embeddings to be generated
        print("\n[WAIT] Waiting 3 seconds for embeddings to be generated...")
        time.sleep(3)
        
        self.test_semantic_search()
        self.test_keyword_search()
        self.test_hybrid_search()
        self.test_search_stats()
        
        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETED")
        print("=" * 70)
        return True

if __name__ == '__main__':
    tester = SearchPipelineTester(BASE_URL, ADMIN_CREDENTIALS)
    tester.run_all_tests()
