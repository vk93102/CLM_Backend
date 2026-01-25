"""
Tests for contracts app
"""
from django.test import TestCase
from rest_framework.test import APIClient

from authentication.models import User
from contracts.models import Contract


class TemplateBasedDraftingFlowTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(email='test@example.com', password='pass1234')
		self.client.force_authenticate(user=self.user)

	def test_template_schema_endpoint(self):
		res = self.client.get('/api/v1/templates/files/schema/Mutual_NDA.txt/')
		self.assertEqual(res.status_code, 200)
		payload = res.json()
		self.assertTrue(payload.get('success'))
		self.assertEqual(payload.get('template_type'), 'NDA')
		self.assertIsInstance(payload.get('sections'), list)

	def test_preview_from_file_renders_and_includes_additions(self):
		res = self.client.post(
			'/api/v1/contracts/preview-from-file/',
			{
				'filename': 'Mutual_NDA.txt',
				'structured_inputs': {
					'effective_date': '2026-01-25',
					'disclosing_party_name': 'Acme Corp Inc.',
					'receiving_party_name': 'Stark Industries',
					'jurisdiction_state': 'Delaware',
					'confidentiality_duration_years': '3',
					'breach_penalty_amount': '50000',
				},
				'selected_clauses': [],
				'constraints': [{'name': 'Data Residency', 'value': 'US only'}],
				'custom_clauses': [{'title': 'Non-Solicit', 'content': 'Neither party will solicit employees for 12 months.'}],
			},
			format='json',
		)
		self.assertEqual(res.status_code, 200)
		payload = res.json()
		self.assertTrue(payload.get('success'))
		rendered = payload.get('rendered_text') or ''
		self.assertIn('Acme Corp Inc.', rendered)
		self.assertIn('Stark Industries', rendered)
		self.assertIn('ADDITIONAL CLAUSES & CONSTRAINTS', rendered)
		self.assertIn('Data Residency', rendered)
		self.assertIn('Non-Solicit', rendered)

	def test_generate_from_file_creates_contract(self):
		Contract.objects.all().delete()
		res = self.client.post(
			'/api/v1/contracts/generate-from-file/',
			{
				'filename': 'Mutual_NDA.txt',
				'title': 'Mutual NDA - Acme',
				'structured_inputs': {
					'effective_date': '2026-01-25',
					'disclosing_party_name': 'Acme Corp Inc.',
					'receiving_party_name': 'Stark Industries',
					'jurisdiction_state': 'Delaware',
					'confidentiality_duration_years': '3',
					'breach_penalty_amount': '50000',
				},
				'selected_clauses': [],
				'constraints': [{'name': 'Venue', 'value': 'New Castle County'}],
				'custom_clauses': [{'title': 'Security', 'content': 'Recipient will use reasonable security measures.'}],
			},
			format='json',
		)
		self.assertEqual(res.status_code, 201)
		payload = res.json()
		contract_id = ((payload.get('contract') or {}).get('id'))
		self.assertIsNotNone(contract_id)
		self.assertEqual(Contract.objects.count(), 1)
		contract = Contract.objects.first()
		self.assertEqual(str(contract.tenant_id), str(self.user.tenant_id))
		self.assertEqual(contract.contract_type, 'NDA')
		self.assertIn('rendered_text', contract.metadata or {})
