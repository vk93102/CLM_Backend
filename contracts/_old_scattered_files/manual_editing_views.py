"""
Manual Contract Editing - Views
Comprehensive views for manual contract creation and editing
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from datetime import datetime
import json

from .manual_editing_models import (
    ContractEditingSession, ContractEditingTemplate, ContractPreview,
    ContractEditingStep, ContractEdits, ContractFieldValidationRule
)
from .manual_editing_serializers import (
    ContractEditingSessionSerializer, ContractEditingSessionDetailSerializer,
    ContractEditingTemplateSerializer, ContractPreviewSerializer,
    FormFieldSubmissionSerializer, ClauseSelectionSerializer,
    ConstraintDefinitionSerializer, ContractPreviewRequestSerializer,
    ContractEditAfterPreviewSerializer, FinalizedContractSerializer
)
from contracts.models import Contract, ContractVersion, Clause


class ContractEditingTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for managing contract editing templates
    Users can browse available templates for manual editing
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ContractEditingTemplateSerializer
    
    def get_queryset(self):
        tenant_id = self.request.user.tenant_id
        return ContractEditingTemplate.objects.filter(
            tenant_id=tenant_id,
            is_active=True
        ).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        GET /manual-templates/by-category/?category=nda
        Get templates filtered by category
        """
        category = request.query_params.get('category')
        tenant_id = request.user.tenant_id
        
        if not category:
            return Response(
                {'error': 'category parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        templates = ContractEditingTemplate.objects.filter(
            tenant_id=tenant_id,
            category=category,
            is_active=True
        )
        
        serializer = self.get_serializer(templates, many=True)
        return Response({
            'category': category,
            'count': len(templates),
            'templates': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        GET /manual-templates/by-type/?contract_type=nda
        Get templates filtered by contract type
        """
        contract_type = request.query_params.get('contract_type')
        tenant_id = request.user.tenant_id
        
        if not contract_type:
            return Response(
                {'error': 'contract_type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        templates = ContractEditingTemplate.objects.filter(
            tenant_id=tenant_id,
            contract_type=contract_type.upper(),
            is_active=True
        )
        
        serializer = self.get_serializer(templates, many=True)
        return Response({
            'contract_type': contract_type,
            'count': len(templates),
            'templates': serializer.data
        })


class ContractEditingSessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing contract editing sessions
    Complete workflow: select template -> fill form -> select clauses -> preview -> finalize
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ContractEditingSessionSerializer
    
    def get_queryset(self):
        tenant_id = self.request.user.tenant_id
        user_id = self.request.user.user_id
        return ContractEditingSession.objects.filter(
            tenant_id=tenant_id,
            user_id=user_id
        ).order_by('-updated_at')
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        POST /manual-sessions/
        Create a new contract editing session
        
        Request body:
        {
            "template_id": "uuid",
            "initial_form_data": {...}
        }
        """
        tenant_id = request.user.tenant_id
        user_id = request.user.user_id
        template_id = request.data.get('template_id')
        initial_form_data = request.data.get('initial_form_data', {})
        
        # Validate template exists and is accessible
        try:
            template = ContractEditingTemplate.objects.get(
                id=template_id,
                tenant_id=tenant_id,
                is_active=True
            )
        except ContractEditingTemplate.DoesNotExist:
            return Response(
                {'error': 'Template not found or not accessible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create session
        session = ContractEditingSession.objects.create(
            tenant_id=tenant_id,
            user_id=user_id,
            template_id=template_id,
            status='draft',
            form_data=initial_form_data
        )
        
        # Log first step
        ContractEditingStep.objects.create(
            session=session,
            step_type='template_selection',
            step_data={
                'template_id': str(template_id),
                'template_name': template.name,
                'contract_type': template.contract_type
            }
        )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """
        GET /manual-sessions/{id}/detail/
        Get detailed session information with all steps and edits
        """
        session = self.get_object()
        serializer = ContractEditingSessionDetailSerializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def fill_form(self, request, pk=None):
        """
        POST /manual-sessions/{id}/fill-form/
        Fill form fields for the contract
        
        Request body:
        {
            "form_data": {
                "party_a_name": "ACME Corp",
                "party_b_name": "Beta LLC",
                "contract_value": 50000,
                "effective_date": "2026-01-20"
            }
        }
        """
        session = self.get_object()
        form_data = request.data.get('form_data', {})
        
        if not form_data:
            return Response(
                {'error': 'form_data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get template for validation
        template = ContractEditingTemplate.objects.get(id=session.template_id)
        
        # Validate all required fields are present
        validation_errors = {}
        for field_name, field_config in template.form_fields.items():
            if field_config.get('required') and field_name not in form_data:
                validation_errors[field_name] = 'This field is required'
        
        if validation_errors:
            return Response(
                {'errors': validation_errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update session
        session.form_data = form_data
        session.status = 'in_progress'
        session.last_saved_at = timezone.now()
        session.save()
        
        # Log step
        ContractEditingStep.objects.create(
            session=session,
            step_type='form_fill',
            step_data=form_data
        )
        
        serializer = self.get_serializer(session)
        return Response(
            {
                'message': 'Form data saved successfully',
                'session': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def select_clauses(self, request, pk=None):
        """
        POST /manual-sessions/{id}/select-clauses/
        Select clauses for the contract
        
        Request body:
        {
            "clause_ids": ["CONF-001", "TERM-001", "LIAB-001"],
            "custom_clause_content": {
                "CUSTOM-001": "Custom clause text here..."
            }
        }
        """
        session = self.get_object()
        clause_ids = request.data.get('clause_ids', [])
        custom_clauses = request.data.get('custom_clause_content', {})
        
        if not clause_ids:
            return Response(
                {'error': 'At least one clause must be selected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate all clause IDs exist
        invalid_clauses = []
        valid_clauses = []
        for clause_id in clause_ids:
            try:
                Clause.objects.get(
                    clause_id=clause_id,
                    tenant_id=request.user.tenant_id,
                    status='published'
                )
                valid_clauses.append(clause_id)
            except Clause.DoesNotExist:
                invalid_clauses.append(clause_id)
        
        if invalid_clauses:
            return Response(
                {
                    'error': 'Some clauses not found',
                    'invalid_clauses': invalid_clauses,
                    'valid_clauses': valid_clauses
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update session
        session.selected_clause_ids = clause_ids
        session.custom_clauses = custom_clauses
        session.save()
        
        # Log step
        ContractEditingStep.objects.create(
            session=session,
            step_type='clause_selection',
            step_data={
                'clause_ids': clause_ids,
                'custom_clauses': bool(custom_clauses)
            }
        )
        
        serializer = self.get_serializer(session)
        return Response(
            {
                'message': 'Clauses selected successfully',
                'selected_count': len(valid_clauses),
                'session': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def define_constraints(self, request, pk=None):
        """
        POST /manual-sessions/{id}/define-constraints/
        Define constraints/versions for the contract
        
        Request body:
        {
            "constraints": {
                "payment_terms": "Net 30",
                "jurisdiction": "California",
                "confidentiality_period": "5 years"
            }
        }
        """
        session = self.get_object()
        constraints = request.data.get('constraints', {})
        
        if not constraints:
            return Response(
                {'error': 'At least one constraint must be defined'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update session
        session.constraints_config = constraints
        session.save()
        
        # Log step
        ContractEditingStep.objects.create(
            session=session,
            step_type='constraint_definition',
            step_data=constraints
        )
        
        serializer = self.get_serializer(session)
        return Response(
            {
                'message': 'Constraints defined successfully',
                'constraints_count': len(constraints),
                'session': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def generate_preview(self, request, pk=None):
        """
        POST /manual-sessions/{id}/generate-preview/
        Generate HTML and text preview of the contract
        
        Request body:
        {
            "form_data": {...},
            "selected_clause_ids": [...],
            "constraints_config": {...}
        }
        """
        session = self.get_object()
        
        form_data = request.data.get('form_data', session.form_data)
        clause_ids = request.data.get('selected_clause_ids', session.selected_clause_ids)
        constraints = request.data.get('constraints_config', session.constraints_config)
        
        if not form_data or not clause_ids:
            return Response(
                {
                    'error': 'Form data and clause IDs are required',
                    'current_form_data': bool(session.form_data),
                    'current_clause_ids': bool(session.selected_clause_ids)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get template
        template = ContractEditingTemplate.objects.get(id=session.template_id)
        
        # Build contract content
        contract_html = self._build_contract_html(
            template, form_data, clause_ids, constraints, request.user.tenant_id
        )
        contract_text = self._build_contract_text(
            template, form_data, clause_ids, constraints, request.user.tenant_id
        )
        
        # Save preview
        preview, created = ContractPreview.objects.update_or_create(
            session=session,
            defaults={
                'preview_html': contract_html,
                'preview_text': contract_text,
                'form_data_snapshot': form_data,
                'clauses_snapshot': clause_ids,
                'constraints_snapshot': constraints
            }
        )
        
        # Log step
        ContractEditingStep.objects.create(
            session=session,
            step_type='preview_generated',
            step_data={
                'preview_id': str(preview.id),
                'form_fields_count': len(form_data),
                'clauses_count': len(clause_ids)
            }
        )
        
        serializer = ContractPreviewSerializer(preview)
        return Response(
            {
                'message': 'Preview generated successfully',
                'preview': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def edit_after_preview(self, request, pk=None):
        """
        POST /manual-sessions/{id}/edit-after-preview/
        Make edits after reviewing the preview
        
        Request body:
        {
            "edit_type": "form_field",
            "field_name": "party_a_name",
            "old_value": "ACME Corp",
            "new_value": "ACME Corporation",
            "edit_reason": "Corrected company name spelling"
        }
        """
        session = self.get_object()
        
        edit_type = request.data.get('edit_type')
        field_name = request.data.get('field_name')
        old_value = request.data.get('old_value')
        new_value = request.data.get('new_value')
        edit_reason = request.data.get('edit_reason', '')
        
        if not edit_type:
            return Response(
                {'error': 'edit_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apply edit based on type
        if edit_type == 'form_field':
            if field_name not in session.form_data:
                return Response(
                    {'error': f'Field {field_name} not found in form data'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            session.form_data[field_name] = new_value
        
        elif edit_type == 'clause_added':
            clause_id = request.data.get('clause_id')
            if clause_id not in session.selected_clause_ids:
                session.selected_clause_ids.append(clause_id)
        
        elif edit_type == 'clause_removed':
            clause_id = request.data.get('clause_id')
            if clause_id in session.selected_clause_ids:
                session.selected_clause_ids.remove(clause_id)
        
        elif edit_type == 'clause_content_edited':
            clause_id = request.data.get('clause_id')
            custom_content = request.data.get('custom_content')
            session.custom_clauses[clause_id] = custom_content
        
        session.save()
        
        # Log edit
        ContractEdits.objects.create(
            session=session,
            edit_type=edit_type,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            edit_reason=edit_reason
        )
        
        # Log as step
        ContractEditingStep.objects.create(
            session=session,
            step_type='field_edited',
            step_data={
                'edit_type': edit_type,
                'field_name': field_name,
                'edit_reason': edit_reason
            }
        )
        
        serializer = self.get_serializer(session)
        return Response(
            {
                'message': 'Edit applied successfully',
                'session': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def finalize_and_create(self, request, pk=None):
        """
        POST /manual-sessions/{id}/finalize-and-create/
        Finalize editing and create actual contract
        
        Request body:
        {
            "contract_title": "NDA with ACME Corp",
            "contract_description": "Non-disclosure agreement",
            "contract_value": 50000,
            "effective_date": "2026-01-20",
            "expiration_date": "2027-01-20",
            "additional_metadata": {...}
        }
        """
        session = self.get_object()
        
        # Validate session has required data
        if not session.form_data:
            return Response(
                {'error': 'Form data is required. Please fill the form first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not session.selected_clause_ids:
            return Response(
                {'error': 'At least one clause must be selected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get template to use default clauses if needed
        template = ContractEditingTemplate.objects.get(id=session.template_id)
        
        # Use selected clauses or fall back to template defaults
        final_clause_ids = session.selected_clause_ids or template.mandatory_clauses
        final_constraints = session.constraints_config or {}
        
        # Create contract
        contract_data = {
            'title': request.data.get('contract_title', 'Untitled Contract'),
            'contract_type': template.contract_type,
            'status': 'draft',
            'generation_mode': 'manual',
            'form_inputs': session.form_data,
            'metadata': {
                'editing_session_id': str(session.id),
                'constraints': final_constraints,
                'custom_clauses': session.custom_clauses
            }
        }
        
        try:
            contract = Contract.objects.create(
                tenant_id=request.user.tenant_id,
                created_by=request.user.user_id,
                **contract_data
            )
            
            # Create contract version with selected clauses
            version = ContractVersion.objects.create(
                contract=contract,
                version_number=1,
                template_id=session.template_id,
                template_version=template.version,
                change_summary='Created from manual editing session',
                created_by=request.user.user_id,
                r2_key=f'contracts/{request.user.tenant_id}/{contract.id}/v1.docx'
            )
            
            # Update session status
            session.status = 'completed'
            session.save()
            
            # Log final step
            ContractEditingStep.objects.create(
                session=session,
                step_type='saved',
                step_data={
                    'contract_id': str(contract.id),
                    'version_id': str(version.id),
                    'status': 'completed'
                }
            )
            
            return Response(
                {
                    'message': 'Contract created successfully',
                    'contract': {
                        'id': str(contract.id),
                        'title': contract.title,
                        'status': contract.status,
                        'contract_type': contract.contract_type,
                        'created_at': contract.created_at.isoformat(),
                        'version': {
                            'id': str(version.id),
                            'version_number': version.version_number,
                            'created_at': version.created_at.isoformat()
                        }
                    },
                    'session': self.get_serializer(session).data
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response(
                {'error': f'Failed to create contract: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _build_contract_html(self, template, form_data, clause_ids, constraints, tenant_id):
        """
        Build professional HTML preview of contract
        """
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                    color: #333;
                }}
                .contract-header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #000;
                    padding-bottom: 20px;
                }}
                h1 {{
                    margin: 0;
                    font-size: 24px;
                    text-transform: uppercase;
                }}
                .contract-date {{
                    margin-top: 10px;
                    font-style: italic;
                }}
                .section {{
                    margin: 30px 0;
                    page-break-inside: avoid;
                }}
                .section-title {{
                    font-weight: bold;
                    font-size: 14px;
                    margin-top: 20px;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                }}
                .clause {{
                    margin: 15px 0;
                    padding: 10px;
                    border-left: 3px solid #007bff;
                    background-color: #f8f9fa;
                }}
                .form-field {{
                    margin: 8px 0;
                }}
                .form-label {{
                    font-weight: bold;
                    display: inline-block;
                    width: 200px;
                }}
                .constraint {{
                    background-color: #fff3cd;
                    padding: 8px;
                    margin: 5px 0;
                    border-radius: 3px;
                }}
                @media print {{
                    body {{ margin: 20px; }}
                }}
            </style>
        </head>
        <body>
            <div class="contract-header">
                <h1>{template.name}</h1>
                <div class="contract-date">Date: {datetime.now().strftime('%B %d, %Y')}</div>
            </div>
            
            <div class="section">
                <div class="section-title">Contract Information</div>
        """
        
        # Add form data
        for field_name, field_value in form_data.items():
            html_content += f"""
                <div class="form-field">
                    <span class="form-label">{field_name.replace('_', ' ').title()}:</span>
                    <span>{field_value}</span>
                </div>
            """
        
        # Add constraints
        if constraints:
            html_content += '<div class="section-title">Constraints & Versions</div>'
            for constraint_name, constraint_value in constraints.items():
                html_content += f"""
                    <div class="constraint">
                        <strong>{constraint_name.replace('_', ' ').title()}:</strong> {constraint_value}
                    </div>
                """
        
        # Add clauses
        html_content += '<div class="section-title">Contract Clauses</div>'
        
        clauses = Clause.objects.filter(
            clause_id__in=clause_ids,
            tenant_id=tenant_id,
            status='published'
        )
        
        for idx, clause in enumerate(clauses, 1):
            html_content += f"""
                <div class="clause">
                    <strong>Clause {idx}: {clause.name}</strong><br>
                    {clause.content[:200]}...
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _build_contract_text(self, template, form_data, clause_ids, constraints, tenant_id):
        """
        Build plain text preview of contract
        """
        text_content = f"""
{template.name.upper()}

Date: {datetime.now().strftime('%B %d, %Y')}

{'='*60}

CONTRACT INFORMATION
{'='*60}

"""
        
        # Add form data
        for field_name, field_value in form_data.items():
            text_content += f"{field_name.replace('_', ' ').title()}: {field_value}\n"
        
        # Add constraints
        if constraints:
            text_content += f"\n{'='*60}\nCONSTRAINTS & VERSIONS\n{'='*60}\n\n"
            for constraint_name, constraint_value in constraints.items():
                text_content += f"{constraint_name.replace('_', ' ').title()}: {constraint_value}\n"
        
        # Add clauses
        text_content += f"\n{'='*60}\nCONTRACT CLAUSES\n{'='*60}\n\n"
        
        clauses = Clause.objects.filter(
            clause_id__in=clause_ids,
            tenant_id=tenant_id,
            status='published'
        )
        
        for idx, clause in enumerate(clauses, 1):
            text_content += f"\nClause {idx}: {clause.name}\n"
            text_content += f"{'-'*40}\n"
            text_content += f"{clause.content[:300]}...\n"
        
        return text_content
    
    @action(detail=True, methods=['post'])
    def save_draft(self, request, pk=None):
        """
        POST /manual-sessions/{id}/save-draft/
        Save the current state as draft without finalizing
        """
        session = self.get_object()
        
        session.last_saved_at = timezone.now()
        session.save()
        
        # Log step
        ContractEditingStep.objects.create(
            session=session,
            step_type='saved',
            step_data={
                'auto_saved': False,
                'timestamp': timezone.now().isoformat()
            }
        )
        
        serializer = self.get_serializer(session)
        return Response(
            {
                'message': 'Draft saved successfully',
                'last_saved_at': session.last_saved_at.isoformat(),
                'session': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['delete'])
    def discard(self, request, pk=None):
        """
        DELETE /manual-sessions/{id}/discard/
        Discard the editing session
        """
        session = self.get_object()
        session.status = 'abandoned'
        session.save()
        
        return Response(
            {'message': 'Session discarded successfully'},
            status=status.HTTP_200_OK
        )
