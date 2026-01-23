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
from .models import ContractTemplate
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
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]
    
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
