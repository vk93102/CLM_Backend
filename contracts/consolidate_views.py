#!/usr/bin/env python3
"""
Script to consolidate all scattered view files into a single views.py
"""

# Week 1 & 2 views (from original views.py before consolidation)
week_views = '''"""
Contract API Views - Week 1 & Week 2 Endpoints
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Contract, WorkflowLog
from .serializers import (
    ContractSerializer,
    ContractDetailSerializer,
    ContractDecisionSerializer,
    WorkflowLogSerializer
)
from authentication.r2_service import R2StorageService


class ContractListCreateView(APIView):
    """
    POST /api/v1/contracts/ - Create a new contract with file upload
    GET /api/v1/contracts/ - List all contracts for the tenant
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        if not request.user.tenant_id:
            return Response(
                {'error': 'Tenant ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES.get('file')
        title = request.data.get('title')
        contract_status = request.data.get('status', 'draft')
        counterparty = request.data.get('counterparty', '')
        contract_type = request.data.get('contract_type', '')
        
        if not file:
            return Response(
                {'error': 'File is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not title:
            return Response(
                {'error': 'Title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            r2_service = R2StorageService()
            r2_key = r2_service.upload_file(file, request.user.tenant_id, file.name)
            
            contract = Contract.objects.create(
                tenant_id=request.user.tenant_id,
                title=title,
                r2_key=r2_key,
                status=contract_status,
                created_by=request.user.user_id,
                counterparty=counterparty,
                contract_type=contract_type
            )
            
            WorkflowLog.objects.create(
                contract=contract,
                action='created',
                performed_by=request.user.user_id,
                comment='Contract created'
            )
            
            serializer = ContractSerializer(contract)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to create contract: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        if not request.user.tenant_id:
            return Response(
                {'error': 'Tenant ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contracts = Contract.objects.filter(tenant_id=request.user.tenant_id)
        serializer = ContractSerializer(contracts, many=True)
        return Response(serializer.data)


class ContractDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, contract_id):
        if not request.user.tenant_id:
            return Response(
                {'error': 'Tenant ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contract = get_object_or_404(
            Contract,
            id=contract_id,
            tenant_id=request.user.tenant_id
        )
        
        try:
            r2_service = R2StorageService()
            download_url = r2_service.generate_presigned_url(contract.r2_key)
            
            serializer = ContractDetailSerializer(contract)
            data = serializer.data
            data['download_url'] = download_url
            
            return Response(data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate download URL: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContractSubmitView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, contract_id):
        if not request.user.tenant_id:
            return Response(
                {'error': 'Tenant ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contract = get_object_or_404(
            Contract,
            id=contract_id,
            tenant_id=request.user.tenant_id
        )
        
        if contract.status != 'draft':
            return Response(
                {'error': f'Cannot submit contract with status "{contract.status}"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                contract.status = 'pending'
                contract.save()
                
                WorkflowLog.objects.create(
                    contract=contract,
                    action='submitted',
                    performed_by=request.user.user_id,
                    comment='Submitted for approval'
                )
            
            serializer = ContractSerializer(contract)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to submit contract: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContractDecideView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, contract_id):
        if not request.user.tenant_id:
            return Response(
                {'error': 'Tenant ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contract = get_object_or_404(
            Contract,
            id=contract_id,
            tenant_id=request.user.tenant_id
        )
        
        serializer = ContractDecisionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        decision = serializer.validated_data['decision']
        comment = serializer.validated_data.get('comment', '')
        
        if contract.status != 'pending':
            return Response(
                {'error': f'Cannot decide on contract with status "{contract.status}"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                if decision == 'approve':
                    contract.status = 'approved'
                    action = 'approved'
                else:
                    contract.status = 'rejected'
                    action = 'rejected'
                
                contract.save()
                
                WorkflowLog.objects.create(
                    contract=contract,
                    action=action,
                    performed_by=request.user.user_id,
                    comment=comment or f'Contract {action}'
                )
            
            serializer = ContractSerializer(contract)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to process decision: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContractDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, contract_id):
        if not request.user.tenant_id:
            return Response(
                {'error': 'Tenant ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contract = get_object_or_404(
            Contract,
            id=contract_id,
            tenant_id=request.user.tenant_id
        )
        
        try:
            with transaction.atomic():
                WorkflowLog.objects.create(
                    contract=contract,
                    action='deleted',
                    performed_by=request.user.user_id,
                    comment='Contract deleted'
                )
                
                r2_service = R2StorageService()
                r2_service.delete_file(contract.r2_key)
                
                contract.delete()
            
            return Response(
                {'message': 'Contract deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Exception as e:
            return Response(
                {'error': f'Failed to delete contract: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
'''

# Read generation views
with open('_old_scattered_files/generation_views.py', 'r') as f:
    generation_views = f.read()

# Read manual editing views
with open('_old_scattered_files/manual_editing_views.py', 'r') as f:
    manual_views = f.read()

# Read R2 views
with open('_old_scattered_files/r2_views.py', 'r') as f:
    r2_views = f.read()

# Read health views  
with open('_old_scattered_files/health_views.py', 'r') as f:
    health_views = f.read()

# Read SignNow views
with open('_old_scattered_files/signnow_views.py', 'r') as f:
    signnow_views = f.read()

# Extract class/function definitions (skip imports and docstrings)
def extract_code_without_header(content):
    lines = content.split('\n')
    # Find first class or function definition
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('class ') or line.strip().startswith('@api_view') or line.strip().startswith('def '):
            start_idx = i
            break
    return '\n'.join(lines[start_idx:])

# Build consolidated file
consolidated = '''"""
Consolidated Contract API Views
All contract-related views organized by functionality
"""
# ============================================================================
# IMPORTS
# ============================================================================
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db import transaction, connection
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.utils import timezone
from django.http import FileResponse
from datetime import datetime, timedelta
import uuid
import hashlib
import json
import logging

from .models import (
    Contract, WorkflowLog, ContractVersion, ContractTemplate, Clause,
    GenerationJob, BusinessRule, ContractClause, ESignatureContract,
    Signer, SigningAuditLog
)
from .manual_editing_models import (
    ContractEditingSession, ContractEditingTemplate, ContractPreview,
    ContractEditingStep, ContractEdits, ContractFieldValidationRule
)
from .serializers import (
    ContractSerializer, ContractDetailSerializer, ContractDecisionSerializer,
    WorkflowLogSerializer, ContractTemplateSerializer, ClauseSerializer,
    ContractVersionSerializer, GenerationJobSerializer,
    ContractGenerateSerializer, ContractApproveSerializer
)
from .manual_editing_serializers import (
    ContractEditingSessionSerializer, ContractEditingSessionDetailSerializer,
    ContractEditingTemplateSerializer, ContractPreviewSerializer,
    FormFieldSubmissionSerializer, ClauseSelectionSerializer,
    ConstraintDefinitionSerializer, ContractPreviewRequestSerializer,
    ContractEditAfterPreviewSerializer, FinalizedContractSerializer
)
from .services import ContractGenerator, RuleEngine
from .signnow_service import SignNowAPIService, SignNowAuthService
from authentication.r2_service import R2StorageService

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: WEEK 1 & WEEK 2 BASIC CONTRACT VIEWS
# ============================================================================

'''

# Add Week 1 & 2 views
week_code = extract_code_without_header(week_views)
consolidated += week_code

# Add generation views
consolidated += '''

# ============================================================================
# SECTION 2: CONTRACT GENERATION VIEWSETS
# ============================================================================

'''
gen_code = extract_code_without_header(generation_views)
consolidated += gen_code

# Add manual editing views
consolidated += '''

# ============================================================================
# SECTION 3: MANUAL EDITING VIEWS
# ============================================================================

'''
manual_code = extract_code_without_header(manual_views)
consolidated += manual_code

# Add R2 views
consolidated += '''

# ============================================================================
# SECTION 4: R2 UPLOAD ENDPOINTS
# ============================================================================

'''
r2_code = extract_code_without_header(r2_views)
consolidated += r2_code

# Add health views
consolidated += '''

# ============================================================================
# SECTION 5: HEALTH CHECK VIEWS
# ============================================================================

'''
health_code = extract_code_without_header(health_views)
consolidated += health_code

# Add SignNow views
consolidated += '''

# ============================================================================
# SECTION 6: SIGNNOW E-SIGNATURE VIEWS
# ============================================================================

'''
signnow_code = extract_code_without_header(signnow_views)
consolidated += signnow_code

# Write the consolidated file
with open('views.py', 'w') as f:
    f.write(consolidated)

# Print summary
total_lines = len(consolidated.split('\n'))
print("✅ Consolidated views.py created successfully!")
print(f"📊 Total lines: {total_lines}")
print(f"\n📁 Sections:")
print(f"   1. Week 1 & 2 Basic Contract Views")
print(f"   2. Contract Generation ViewSets") 
print(f"   3. Manual Editing Views")
print(f"   4. R2 Upload Endpoints")
print(f"   5. Health Check Views")
print(f"   6. SignNow E-Signature Views")
