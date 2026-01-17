#!/usr/bin/env python
"""
Test Gemini metadata extraction directly
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')

import django
django.setup()

from repository.document_service import MetadataExtractionService

contract_text = """
SERVICE AGREEMENT

Between ABC Corporation (USA) and XYZ Industries (UK)
Effective January 15, 2024
Expires December 31, 2025

CONTRACT VALUE: USD 750,000
PAYMENT: $375,000 per year

KEY TERMS:
- Confidentiality clause: 3 years
- Termination: 90 days notice
- Liability: Limited to contract value
"""

print("Testing MetadataExtractionService directly...")
service = MetadataExtractionService()
print(f"✓ Service initialized")
print(f"✓ API key present: {bool(service.gemini_api_key)}")

print("\nExtracting metadata...")
result = service.extract_metadata(contract_text)

print(f"\nResult:")
print(f"  Parties: {result.get('parties')}")
print(f"  Value: {result.get('contract_value')}")
print(f"  Currency: {result.get('currency')}")
print(f"  Clauses: {result.get('identified_clauses')}")
print(f"  Summary: {result.get('summary')[:80]}..." if result.get('summary') else "  Summary: None")
print(f"  Risk: {result.get('risk_score')}")
