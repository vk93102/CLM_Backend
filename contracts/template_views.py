"""
Template Management Endpoints
Provides detailed information about contract templates and their structure
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .template_definitions import (
    get_template_type, 
    get_all_template_types,
    get_template_summary,
    validate_template_data,
    TEMPLATE_TYPES
)
from .models import ContractTemplate, TemplateFile
from .serializers import ContractTemplateSerializer
import uuid


class TemplateTypesView(APIView):
    """
    GET /api/v1/templates/types/
    Get all available contract template types with full documentation
    
    Response:
    {
        "NDA": {
            "display_name": "Non-Disclosure Agreement",
            "description": "Protects confidential information...",
            "required_fields": [...],
            "optional_fields": [...],
            "mandatory_clauses": [...],
            "sample_data": {...}
        },
        ...
    }
    """
    permission_classes = []
    
    def get(self, request):
        all_types = get_all_template_types()
        
        return Response({
            'success': True,
            'total_types': len(all_types),
            'template_types': all_types
        }, status=status.HTTP_200_OK)


class TemplateTypeSummaryView(APIView):
    """
    GET /api/v1/templates/summary/
    Quick summary of all template types
    
    Response:
    {
        "NDA": {
            "display_name": "Non-Disclosure Agreement",
            "description": "...",
            "required_fields_count": 7,
            "optional_fields_count": 5,
            "mandatory_clauses": [...]
        },
        ...
    }
    """
    permission_classes = []
    
    def get(self, request):
        """Get summary of all template types"""
        summary = get_template_summary()
        
        return Response({
            'success': True,
            'total_types': len(summary),
            'summary': summary
        }, status=status.HTTP_200_OK)


class TemplateTypeDetailView(APIView):
    """
    GET /api/v1/templates/types/{template_type}/
    Get detailed information about a specific template type
    
    Path Parameters:
        template_type: NDA, MSA, EMPLOYMENT, SERVICE_AGREEMENT, etc.
    
    Response:
    {
        "template_type": "NDA",
        "display_name": "Non-Disclosure Agreement",
        "description": "...",
        "required_fields": [
            {
                "name": "effective_date",
                "type": "date",
                "description": "Date agreement becomes effective"
            },
            ...
        ],
        "optional_fields": [...],
        "mandatory_clauses": [...],
        "business_rules": {...},
        "sample_data": {...}
    }
    """
    permission_classes = []
    
    def get(self, request, template_type):
        """Get detailed information about a template type"""
        template = get_template_type(template_type)
        
        if not template:
            return Response({
                'success': False,
                'error': f'Unknown template type: {template_type}',
                'available_types': list(TEMPLATE_TYPES.keys())
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Add field descriptions
        field_descriptions = {
            'effective_date': 'Date when the agreement becomes effective',
            'first_party_name': 'Name of the first party',
            'second_party_name': 'Name of the second party',
            'governing_law': 'Jurisdiction for dispute resolution',
            'client_name': 'Name of the client',
            'service_provider_name': 'Name of the service provider',
            'monthly_fees': 'Monthly service fees in USD',
            'annual_salary': 'Annual compensation in USD',
            'employer_name': 'Name of the employer',
            'employee_name': 'Name of the employee',
            'job_title': 'Job title and position',
            'total_project_value': 'Total project value in USD',
            'principal_name': 'Name of the principal',
            'agent_name': 'Name of the agent',
            'owner_name': 'Name of property owner',
            'manager_name': 'Name of property manager',
            'property_address': 'Address of the property',
            'buyer_name': 'Name of the buyer',
            'seller_name': 'Name of the seller',
            'purchase_price': 'Purchase price in USD'
        }
        
        return Response({
            'success': True,
            'template_type': template_type,
            'display_name': template['display_name'],
            'description': template['description'],
            'contract_type': template['contract_type'],
            'required_fields': [
                {
                    'name': field,
                    'description': field_descriptions.get(field, f'{field} (required)')
                }
                for field in template['required_fields']
            ],
            'optional_fields': [
                {
                    'name': field,
                    'description': field_descriptions.get(field, f'{field} (optional)')
                }
                for field in template['optional_fields']
            ],
            'mandatory_clauses': template['mandatory_clauses'],
            'business_rules': template['business_rules'],
            'sample_data': template['sample_data']
        }, status=status.HTTP_200_OK)


class TemplateFileView(APIView):
    """
    GET /api/v1/templates/files/{template_type}/
    Get the actual template file content for viewing/downloading
    """
    permission_classes = []
    
    def get(self, request, template_type):
        """Get template file content"""
        import os
        from django.conf import settings
        
        # Map template types to file names
        template_files = {
            'NDA': 'NDA.txt',
            'EMPLOYMENT': 'Employement-Agreement.txt',
            'AGENCY_AGREEMENT': 'Agency-Agreement.txt',
            'PROPERTY_MANAGEMENT': 'Property_management_contract.txt'
        }
        
        filename = template_files.get(template_type)
        if not filename:
            return Response({
                'success': False,
                'error': f'No template file found for type: {template_type}',
                'available_types': list(template_files.keys())
            }, status=status.HTTP_404_NOT_FOUND)
        
        template_path = os.path.join(settings.BASE_DIR, 'templates', filename)

        # Prefer DB-backed templates.
        try:
            tmpl = TemplateFile.objects.filter(filename=filename).first()
            if tmpl:
                content = tmpl.content or ''
                return Response({
                    'success': True,
                    'template_type': template_type,
                    'filename': filename,
                    'content': content,
                    'size': len(content.encode('utf-8'))
                }, status=status.HTTP_200_OK)
        except Exception:
            pass

        # Transitional fallback: if DB isn't populated yet, read from filesystem.
        if not os.path.exists(template_path):
            return Response({
                'success': False,
                'error': f'Template not found in DB or filesystem: {filename}'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return Response({
                'success': True,
                'template_type': template_type,
                'filename': filename,
                'content': content,
                'size': len(content)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to read template: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateTemplateFromTypeView(APIView):
    """
    POST /api/v1/templates/create-from-type/
    Create a new contract template from a predefined type
    
    Request:
    {
        "template_type": "NDA",
        "name": "Standard NDA - 2026",
        "description": "Our standard NDA template",
        "status": "published",
        "data": {
            "effective_date": "2026-01-20",
            "first_party_name": "Acme Corp",
            ...
        }
    }
    
    Response:
    {
        "success": true,
        "template_id": "uuid",
        "name": "Standard NDA - 2026",
        "contract_type": "NDA",
        "status": "published",
        "message": "Template created successfully"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a template from a predefined type"""
        template_type = request.data.get('template_type')
        name = request.data.get('name')
        description = request.data.get('description', '')
        status_choice = request.data.get('status', 'draft')
        data = request.data.get('data', {})
        
        # Validate request
        if not template_type:
            return Response({
                'success': False,
                'error': 'template_type is required',
                'available_types': list(TEMPLATE_TYPES.keys())
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not name:
            return Response({
                'success': False,
                'error': 'name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get template definition
        template_def = get_template_type(template_type)
        if not template_def:
            return Response({
                'success': False,
                'error': f'Unknown template type: {template_type}',
                'available_types': list(TEMPLATE_TYPES.keys())
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validate data against required fields
        is_valid, error_msg = validate_template_data(template_type, data)
        if not is_valid:
            return Response({
                'success': False,
                'error': error_msg,
                'required_fields': template_def['required_fields']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create contract template
            template = ContractTemplate.objects.create(
                tenant_id=request.user.tenant_id,
                name=name,
                contract_type=template_def['contract_type'],
                description=description,
                status=status_choice,
                r2_key=f"templates/{template_type}/{uuid.uuid4()}.docx",
                merge_fields=template_def['required_fields'] + template_def['optional_fields'],
                mandatory_clauses=template_def['mandatory_clauses'],
                business_rules=template_def['business_rules'],
                created_by=request.user.user_id
            )
            
            serializer = ContractTemplateSerializer(template)
            
            return Response({
                'success': True,
                'template_id': str(template.id),
                'name': template.name,
                'contract_type': template.contract_type,
                'status': template.status,
                'merge_fields': template.merge_fields,
                'mandatory_clauses': template.mandatory_clauses,
                'message': f'Template "{name}" created successfully from {template_type} type',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Failed to create template'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidateTemplateDataView(APIView):
    """
    POST /api/v1/templates/validate/
    Validate data against a template type's required fields
    
    Request:
    {
        "template_type": "NDA",
        "data": {
            "effective_date": "2026-01-20",
            "first_party_name": "Acme Corp",
            ...
        }
    }
    
    Response:
    {
        "success": true,
        "is_valid": true,
        "template_type": "NDA",
        "required_fields": [...],
        "provided_fields": [...],
        "missing_fields": [],
        "message": "All required fields provided"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Validate data against template type requirements"""
        template_type = request.data.get('template_type')
        data = request.data.get('data', {})
        
        if not template_type:
            return Response({
                'success': False,
                'error': 'template_type is required',
                'available_types': list(TEMPLATE_TYPES.keys())
            }, status=status.HTTP_400_BAD_REQUEST)
        
        template_def = get_template_type(template_type)
        if not template_def:
            return Response({
                'success': False,
                'error': f'Unknown template type: {template_type}',
                'available_types': list(TEMPLATE_TYPES.keys())
            }, status=status.HTTP_404_NOT_FOUND)
        
        is_valid, error_msg = validate_template_data(template_type, data)
        
        required = template_def['required_fields']
        provided = list(data.keys())
        missing = [f for f in required if f not in provided or not data.get(f)]
        
        return Response({
            'success': True,
            'is_valid': is_valid,
            'template_type': template_type,
            'required_fields': required,
            'optional_fields': template_def['optional_fields'],
            'provided_fields': provided,
            'missing_fields': missing,
            'message': error_msg or 'All required fields provided',
            'validation_details': {
                'total_required': len(required),
                'total_provided': len(provided),
                'fields_missing': len(missing),
                'fields_extra': len([f for f in provided if f not in required])
            }
        }, status=status.HTTP_200_OK)


class UserTemplatesView(APIView):
    """
    GET /api/v1/templates/user/
    Get all templates created by the current user
    
    POST /api/v1/templates/user/
    Create a new template instance
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all templates created by the current user"""
        try:
            templates = ContractTemplate.objects.filter(
                tenant_id=request.user.tenant_id,
                created_by=request.user.user_id
            ).order_by('-created_at')
            
            serializer = ContractTemplateSerializer(templates, many=True)
            
            return Response({
                'success': True,
                'count': templates.count(),
                'templates': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create a new template instance"""
        try:
            template_type = request.data.get('template_type')
            name = request.data.get('name')
            description = request.data.get('description', '')
            
            if not template_type or not name:
                return Response({
                    'success': False,
                    'error': 'template_type and name are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            template_def = get_template_type(template_type)
            if not template_def:
                return Response({
                    'success': False,
                    'error': f'Unknown template type: {template_type}'
                }, status=status.HTTP_404_NOT_FOUND)
            
            template = ContractTemplate.objects.create(
                tenant_id=request.user.tenant_id,
                name=name,
                contract_type=template_def['contract_type'],
                description=description,
                status='published',
                r2_key=f"templates/{template_type}/{uuid.uuid4()}.docx",
                merge_fields=template_def['required_fields'] + template_def['optional_fields'],
                mandatory_clauses=template_def.get('mandatory_clauses', []),
                business_rules=template_def.get('business_rules', {}),
                created_by=request.user.user_id
            )
            
            serializer = ContractTemplateSerializer(template)
            
            return Response({
                'success': True,
                'message': f'Template "{name}" created successfully',
                'template': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteTemplateView(APIView):
    """
    DELETE /api/v1/templates/{template_id}/
    Delete a template (admin only)
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, template_id):
        """Delete a template (admin only)"""
        try:
            if not request.user.is_staff:
                return Response({
                    'success': False,
                    'error': 'Only administrators can delete templates'
                }, status=status.HTTP_403_FORBIDDEN)
            
            template = ContractTemplate.objects.get(id=template_id)
            template_name = template.name
            template.delete()
            
            return Response({
                'success': True,
                'message': f'Template "{template_name}" deleted successfully'
            }, status=status.HTTP_200_OK)
        except ContractTemplate.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Template not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
