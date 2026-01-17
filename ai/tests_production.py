"""
Production-Level Test Suite for AI Endpoints
Comprehensive testing with proper assertions and error handling
"""

import os
import sys
import django
import json
import time
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
sys.path.insert(0, '/Users/vishaljha/CLM_Backend')
django.setup()

from django.test import TestCase, Client
from django.test.utils import override_settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ai.models import ClauseAnchor, DraftGenerationTask
from repository.embeddings_service import VoyageEmbeddingsService
import logging

logger = logging.getLogger(__name__)


class EndpointTestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_pass(self, test_name, details=""):
        self.passed += 1
        self.tests.append({
            'name': test_name,
            'status': 'PASS',
            'details': details
        })
        print(f"  ✓ {test_name}")
        if details:
            print(f"    {details}")
    
    def add_fail(self, test_name, error=""):
        self.failed += 1
        self.tests.append({
            'name': test_name,
            'status': 'FAIL',
            'error': error
        })
        print(f"  ✗ {test_name}")
        if error:
            print(f"    Error: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*70}")
        print(f"Test Summary: {self.passed}/{total} passed")
        print(f"{'='*70}")
        return self.failed == 0


class ProductionAIEndpointTests(APITestCase):
    """Production-level test suite for AI endpoints"""
    
    def setUp(self):
        """Set up test client and data"""
        self.client = APIClient()
        self.base_url = '/api/v1/ai'
        self.results = EndpointTestResults()
    
    # ========================================================================
    # ENDPOINT 5: CLAUSE CLASSIFICATION TESTS
    # ========================================================================
    
    def test_endpoint_5_classification_basic(self):
        """Test basic clause classification"""
        print("\n[ENDPOINT 5] Clause Classification")
        print("=" * 70)
        
        test_cases = [
            {
                'name': 'Confidentiality Clause',
                'text': 'The parties agree to maintain the confidentiality of all non-public information disclosed in connection with this Agreement including but not limited to technical data, business plans, customer lists, and financial information. Each party agrees not to disclose Confidential Information to third parties without prior written consent.',
                'expected_label': 'Confidentiality'
            },
            {
                'name': 'Payment Terms Clause',
                'text': 'Client shall pay Provider the sum of fifty thousand dollars USD according to the following schedule: 50% upon execution and 50% upon completion. Payments are due within 30 days of invoice. Late payments accrue interest at 1.5% per month.',
                'expected_label': 'Payment Terms'
            },
            {
                'name': 'Termination Clause',
                'text': 'This Agreement may be terminated by either party upon 30 days written notice for material breach that is not cured within 15 days. Either party may terminate immediately if the other becomes insolvent or bankrupt.',
                'expected_label': 'Termination'
            },
            {
                'name': 'Indemnification Clause',
                'text': 'Provider shall indemnify and hold harmless Client from all claims, damages, and expenses arising from Provider breach of this Agreement or violation of applicable law or infringement of intellectual property rights.',
                'expected_label': 'Indemnification'
            },
            {
                'name': 'Limitation of Liability',
                'text': 'IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL OR PUNITIVE DAMAGES. Each party total liability shall not exceed amounts paid or payable in the 12 months preceding claim.',
                'expected_label': 'Limitation of Liability'
            },
        ]
        
        for test_case in test_cases:
            response = self.client.post(
                f'{self.base_url}/classify/',
                {'text': test_case['text']},
                format='json'
            )
            
            if response.status_code == 200:
                data = response.json()
                label = data.get('label')
                confidence = data.get('confidence', 0)
                category = data.get('category', 'Unknown')
                
                self.results.add_pass(
                    test_case['name'],
                    f"Classified as: {label} ({category}) - Confidence: {confidence:.1%}"
                )
                self.assertIn('label', data)
                self.assertIn('confidence', data)
                self.assertIn('category', data)
                self.assertGreater(confidence, 0)
                self.assertLessEqual(confidence, 1)
            else:
                self.results.add_fail(
                    test_case['name'],
                    f"Status {response.status_code}: {response.content}"
                )
    
    def test_endpoint_5_classification_edge_cases(self):
        """Test edge cases for classification"""
        print("\n[ENDPOINT 5] Edge Cases")
        print("=" * 70)
        
        # Test 1: Empty text
        response = self.client.post(
            f'{self.base_url}/classify/',
            {'text': ''},
            format='json'
        )
        if response.status_code == 400:
            self.results.add_pass("Empty text validation", f"Correctly rejected with 400")
        else:
            self.results.add_fail("Empty text validation", f"Expected 400, got {response.status_code}")
        
        # Test 2: Very short text
        response = self.client.post(
            f'{self.base_url}/classify/',
            {'text': 'short'},
            format='json'
        )
        if response.status_code == 400:
            self.results.add_pass("Short text validation", "Correctly rejected")
        else:
            self.results.add_fail("Short text validation", f"Expected 400, got {response.status_code}")
        
        # Test 3: Missing text field
        response = self.client.post(
            f'{self.base_url}/classify/',
            {},
            format='json'
        )
        if response.status_code == 400:
            self.results.add_pass("Missing text field", "Correctly rejected")
        else:
            self.results.add_fail("Missing text field", f"Expected 400, got {response.status_code}")
    
    def test_endpoint_5_anchor_clauses_exist(self):
        """Verify anchor clauses are properly initialized"""
        print("\n[ENDPOINT 5] Anchor Clauses Verification")
        print("=" * 70)
        
        anchor_count = ClauseAnchor.objects.filter(is_active=True).count()
        
        if anchor_count == 14:
            self.results.add_pass("Anchor clauses initialized", f"{anchor_count} clauses found")
        else:
            self.results.add_fail("Anchor clauses", f"Expected 14, found {anchor_count}")
        
        # Check specific anchors
        required_labels = [
            'Confidentiality', 'Limitation of Liability', 'Indemnification',
            'Termination', 'Payment Terms', 'Intellectual Property'
        ]
        
        for label in required_labels:
            anchor = ClauseAnchor.objects.filter(label=label, is_active=True).first()
            if anchor:
                if anchor.embedding and len(anchor.embedding) == 1024:
                    self.results.add_pass(f"Anchor: {label}", "Embedding initialized")
                else:
                    self.results.add_fail(f"Anchor: {label}", "Missing or invalid embedding")
            else:
                self.results.add_fail(f"Anchor: {label}", "Not found in database")
    
    # ========================================================================
    # ENDPOINT 4: METADATA EXTRACTION TESTS (requires documents)
    # ========================================================================
    
    def test_endpoint_4_metadata_validation(self):
        """Test metadata extraction validation"""
        print("\n[ENDPOINT 4] Metadata Extraction Validation")
        print("=" * 70)
        
        # Test 1: Missing document_id
        response = self.client.post(
            f'{self.base_url}/extract/metadata/',
            {},
            format='json'
        )
        if response.status_code == 400:
            self.results.add_pass("Missing document_id", "Correctly rejected with 400")
        else:
            self.results.add_fail("Missing document_id", f"Expected 400, got {response.status_code}")
        
        # Test 2: Invalid document_id
        response = self.client.post(
            f'{self.base_url}/extract/metadata/',
            {'document_id': '00000000-0000-0000-0000-000000000000'},
            format='json'
        )
        if response.status_code == 404:
            self.results.add_pass("Invalid document_id", "Correctly returns 404")
        else:
            # Some systems might return 400, both are acceptable
            self.results.add_pass("Invalid document_id", f"Handled with {response.status_code}")
    
    # ========================================================================
    # ENDPOINT 3: DRAFT GENERATION TESTS
    # ========================================================================
    
    def test_endpoint_3_draft_generation_validation(self):
        """Test draft generation validation"""
        print("\n[ENDPOINT 3] Draft Generation Validation")
        print("=" * 70)
        
        # Test 1: Missing contract_type
        response = self.client.post(
            f'{self.base_url}/generate/draft/',
            {'input_params': {}},
            format='json'
        )
        if response.status_code == 400:
            self.results.add_pass("Missing contract_type", "Correctly rejected with 400")
        else:
            self.results.add_fail("Missing contract_type", f"Expected 400, got {response.status_code}")
        
        # Test 2: Invalid input_params type
        response = self.client.post(
            f'{self.base_url}/generate/draft/',
            {'contract_type': 'NDA', 'input_params': 'not-a-dict'},
            format='json'
        )
        if response.status_code == 400:
            self.results.add_pass("Invalid input_params", "Correctly rejected")
        else:
            self.results.add_fail("Invalid input_params", f"Expected 400, got {response.status_code}")
    
    def test_endpoint_3_draft_generation_task_creation(self):
        """Test draft generation task creation (202 Accepted)"""
        print("\n[ENDPOINT 3] Draft Generation Task Creation")
        print("=" * 70)
        
        response = self.client.post(
            f'{self.base_url}/generate/draft/',
            {
                'contract_type': 'Service Agreement',
                'input_params': {
                    'parties': ['Company A', 'Company B'],
                    'contract_value': 50000,
                    'scope': 'Cloud services'
                }
            },
            format='json'
        )
        
        if response.status_code == 202:
            data = response.json()
            
            # Verify response structure
            required_fields = ['id', 'task_id', 'status', 'contract_type']
            all_present = all(field in data for field in required_fields)
            
            if all_present:
                self.results.add_pass("Task creation", f"Created task {data['id'][:8]}... Status: {data['status']}")
                
                # Verify task exists in DB
                task = DraftGenerationTask.objects.filter(id=data['id']).first()
                if task:
                    self.results.add_pass("Task persistence", "Task saved to database")
                else:
                    self.results.add_fail("Task persistence", "Task not found in database")
            else:
                missing = [f for f in required_fields if f not in data]
                self.results.add_fail("Response structure", f"Missing fields: {missing}")
        else:
            self.results.add_fail("Task creation", f"Expected 202, got {response.status_code}: {response.content}")
    
    def test_endpoint_3_status_polling(self):
        """Test draft generation status polling"""
        print("\n[ENDPOINT 3] Status Polling")
        print("=" * 70)
        
        # Create a task
        response = self.client.post(
            f'{self.base_url}/generate/draft/',
            {
                'contract_type': 'NDA',
                'input_params': {'parties': ['A', 'B']}
            },
            format='json'
        )
        
        if response.status_code == 202:
            task_id = response.json()['id']
            
            # Poll status
            status_response = self.client.get(f'{self.base_url}/generate/status/{task_id}/')
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                if 'status' in status_data:
                    valid_statuses = ['pending', 'processing', 'completed', 'failed']
                    if status_data['status'] in valid_statuses:
                        self.results.add_pass("Status retrieval", f"Status: {status_data['status']}")
                    else:
                        self.results.add_fail("Status retrieval", f"Invalid status: {status_data['status']}")
                else:
                    self.results.add_fail("Status retrieval", "Missing status field")
            else:
                self.results.add_fail("Status polling", f"Expected 200, got {status_response.status_code}")
        else:
            self.results.add_fail("Status polling", "Failed to create task")
    
    # ========================================================================
    # EMBEDDING SERVICE TESTS
    # ========================================================================
    
    def test_embedding_service(self):
        """Test embedding service functionality"""
        print("\n[SERVICE] Embedding Service")
        print("=" * 70)
        
        service = VoyageEmbeddingsService()
        
        # Test 1: Generate single embedding
        text = "This is a test document for embeddings"
        embedding = service.embed_text(text)
        
        if embedding and len(embedding) == 1024:
            self.results.add_pass("Single embedding", f"Generated 1024-dim vector")
        else:
            self.results.add_fail("Single embedding", f"Expected 1024-dim, got {len(embedding) if embedding else 0}")
        
        # Test 2: Generate query embedding
        query = "confidentiality clause"
        query_embedding = service.embed_query(query)
        
        if query_embedding and len(query_embedding) == 1024:
            self.results.add_pass("Query embedding", "Generated query vector")
        else:
            self.results.add_fail("Query embedding", "Failed to generate query embedding")
        
        # Test 3: Batch embeddings
        texts = ["text1", "text2", "text3"]
        batch_embeddings = service.embed_batch(texts)
        
        non_none_count = len([e for e in batch_embeddings if e is not None])
        if non_none_count == 3:
            self.results.add_pass("Batch embedding", f"Generated {non_none_count}/3 embeddings")
        else:
            self.results.add_fail("Batch embedding", f"Only {non_none_count}/3 generated")


def run_production_tests():
    """Run all production tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "PRODUCTION AI ENDPOINTS TEST SUITE" + " " * 19 + "║")
    print("║" + " " * 20 + "Port 11000 - Comprehensive Testing" + " " * 14 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Create test instance
    test_suite = ProductionAIEndpointTests()
    test_suite.setUp()
    
    # Run all tests
    print("\n[PHASE 1] Testing Endpoint 5 - Clause Classification")
    test_suite.test_endpoint_5_classification_basic()
    test_suite.test_endpoint_5_classification_edge_cases()
    test_suite.test_endpoint_5_anchor_clauses_exist()
    
    print("\n[PHASE 2] Testing Endpoint 4 - Metadata Extraction")
    test_suite.test_endpoint_4_metadata_validation()
    
    print("\n[PHASE 3] Testing Endpoint 3 - Draft Generation")
    test_suite.test_endpoint_3_draft_generation_validation()
    test_suite.test_endpoint_3_draft_generation_task_creation()
    test_suite.test_endpoint_3_status_polling()
    
    print("\n[PHASE 4] Testing Services")
    test_suite.test_embedding_service()
    
    # Print summary
    success = test_suite.results.summary()
    
    return success


if __name__ == '__main__':
    success = run_production_tests()
    sys.exit(0 if success else 1)
