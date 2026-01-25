"""
Template Management Endpoints
Provides detailed information about contract templates and their structure
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
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
import os
import re
import json
from django.utils import timezone
from django.conf import settings


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


class TemplateFileView(APIView):
    """
    GET /api/v1/templates/files/{template_type}/
    Get the template file content for a specific template type
    
    Path Parameters:
        template_type: NDA, MSA, EMPLOYMENT, SERVICE_AGREEMENT, etc.
    
    Response:
    {
        "success": true,
        "template_type": "NDA",
        "filename": "NDA.txt",
        "content": "NON-DISCLOSURE AGREEMENT...",
        "size": 2458
    }
    """
    # Keep this endpoint for template-type based previews, but the UI can use
    # the file-based endpoints below for exact raw file rendering.
    permission_classes = [AllowAny]
    
    def get(self, request, template_type):
        """Get template file content"""
        # Validate template type
        template_def = get_template_type(template_type)
        if not template_def:
            return Response({
                'success': False,
                'error': f'Unknown template type: {template_type}',
                'available_types': list(TEMPLATE_TYPES.keys())
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Map template types to file names
        template_file_map = {
            'NDA': 'NDA.txt',
            'MSA': 'MSA.txt',
            'EMPLOYMENT': 'Employement-Agreement.txt',
            # Repo currently uses these filenames under CLM_Backend/templates
            'SERVICE_AGREEMENT': 'Agency-Agreement.txt',
            'AGENCY_AGREEMENT': 'Agency-Agreement.txt',
            'PROPERTY_MANAGEMENT': 'Property_management_contract.txt',
            'PURCHASE_AGREEMENT': 'Purchase_Agreement.txt',
        }
        
        filename = template_file_map.get(template_type)
        if not filename:
            return Response({
                'success': False,
                'error': f'Template file not found for: {template_type}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Build file path
        template_path = os.path.join(
            settings.BASE_DIR, 
            'templates', 
            filename
        )
        
        # Check if file exists; if not, attempt a best-effort fallback
        if not os.path.exists(template_path):
            templates_dir = os.path.join(settings.BASE_DIR, 'templates')
            if os.path.isdir(templates_dir):
                candidates = [f for f in os.listdir(templates_dir) if f.lower().endswith('.txt')]
                # Try to match by template_type keyword
                preferred = None
                for cand in candidates:
                    c = cand.lower()
                    if template_type.lower() in c:
                        preferred = cand
                        break
                if preferred:
                    filename = preferred
                    template_path = os.path.join(settings.BASE_DIR, 'templates', filename)

        if not os.path.exists(template_path):
            return Response({
                'success': False,
                'error': f'Template file not found at: {filename}',
                'expected_path': template_path
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Read file content
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_size = os.path.getsize(template_path)
            
            return Response({
                'success': True,
                'template_type': template_type,
                'filename': filename,
                'content': content,
                'size': file_size,
                'display_name': template_def['display_name'],
                'description': template_def['description']
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to read template file: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _templates_dir() -> str:
    return os.path.join(settings.BASE_DIR, 'templates')


def _meta_path_for_template(template_path: str) -> str:
    # Store metadata alongside the .txt file without touching the DB.
    return f"{template_path}.meta.json"


def _json_safe(value):
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value


def _read_template_meta(template_path: str) -> dict:
    meta_path = _meta_path_for_template(template_path)
    if not os.path.exists(meta_path):
        return {}
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            data = json.load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_template_meta(template_path: str, meta: dict) -> None:
    meta_path = _meta_path_for_template(template_path)
    with open(meta_path, 'w', encoding='utf-8', newline='') as f:
        json.dump(_json_safe(meta or {}), f, ensure_ascii=False, indent=2)


def _infer_template_type(filename: str) -> str:
    name = filename.lower()
    if 'nda' in name:
        return 'NDA'
    if 'employ' in name:
        return 'EMPLOYMENT'
    if 'agency' in name:
        return 'AGENCY_AGREEMENT'
    if 'property' in name:
        return 'PROPERTY_MANAGEMENT'
    if 'purchase' in name:
        return 'PURCHASE_AGREEMENT'
    if 'msa' in name or 'master' in name:
        return 'MSA'
    return 'SERVICE_AGREEMENT'


def _display_name_from_filename(filename: str) -> str:
    base = os.path.splitext(os.path.basename(filename))[0]
    base = base.replace('_', ' ').replace('-', ' ').strip()
    base = re.sub(r'\s+', ' ', base)
    return base.title() if base else 'Template'


def _sanitize_filename(name: str) -> str:
    # Prevent path traversal and keep filenames simple.
    base = os.path.basename(name).strip()
    base = base.replace('\\', '').replace('/', '')
    base = re.sub(r'[^A-Za-z0-9 _.-]+', '', base)
    base = re.sub(r'\s+', '_', base).strip('_')
    if not base.lower().endswith('.txt'):
        base = f"{base}.txt" if base else 'New_Template.txt'
    return base


class TemplateFilesView(APIView):
    """Filesystem-backed templates (no DB).

    GET  /api/v1/templates/files/                 -> list templates in CLM_Backend/templates
    POST /api/v1/templates/files/                 -> create a new .txt template file
    """

    def get_permissions(self):
        # Listing templates is public; creating templates requires auth so we can attribute ownership.
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        templates_dir = _templates_dir()
        if not os.path.isdir(templates_dir):
            return Response({
                'success': True,
                'count': 0,
                'results': [],
                'message': 'Templates directory not found'
            }, status=status.HTTP_200_OK)

        files = [f for f in os.listdir(templates_dir) if f.lower().endswith('.txt')]
        files.sort(key=lambda f: os.path.getmtime(os.path.join(templates_dir, f)), reverse=True)

        results = []
        for f in files:
            path = os.path.join(templates_dir, f)
            try:
                mtime = timezone.datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.get_current_timezone())
                ctime = timezone.datetime.fromtimestamp(os.path.getctime(path), tz=timezone.get_current_timezone())
            except Exception:
                mtime = timezone.now()
                ctime = timezone.now()

            meta = _read_template_meta(path)

            results.append({
                'id': f,
                'filename': f,
                'name': _display_name_from_filename(f),
                'contract_type': _infer_template_type(f),
                'status': 'active',
                'created_at': ctime.isoformat(),
                'updated_at': mtime.isoformat(),
                'created_by_id': meta.get('created_by_id'),
                'created_by_email': meta.get('created_by_email'),
                'description': meta.get('description') or '',
            })

        return Response({
            'success': True,
            'count': len(results),
            'results': results,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        name = (request.data.get('name') or '').strip()
        filename = (request.data.get('filename') or '').strip()
        description = (request.data.get('description') or '').strip()
        content = request.data.get('content')

        if content is None:
            return Response({
                'success': False,
                'error': 'content is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        proposed = filename or name or 'New Template'
        safe = _sanitize_filename(proposed)

        templates_dir = _templates_dir()
        os.makedirs(templates_dir, exist_ok=True)

        path = os.path.join(templates_dir, safe)
        if os.path.exists(path):
            return Response({
                'success': False,
                'error': 'A template with that filename already exists',
                'filename': safe,
            }, status=status.HTTP_409_CONFLICT)

        try:
            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)

            now = timezone.now().isoformat()
            created_by_id = getattr(request.user, 'user_id', None)
            created_by_email = getattr(request.user, 'email', None)
            _write_template_meta(
                path,
                {
                    'created_by_id': created_by_id,
                    'created_by_email': created_by_email,
                    'description': description,
                    'created_at': now,
                    'updated_at': now,
                },
            )
            return Response({
                'success': True,
                'template': {
                    'id': safe,
                    'filename': safe,
                    'name': _display_name_from_filename(safe),
                    'contract_type': _infer_template_type(safe),
                    'status': 'active',
                    'created_at': now,
                    'updated_at': now,
                    'created_by_id': str(created_by_id) if created_by_id else None,
                    'created_by_email': created_by_email,
                    'description': description,
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to create template file: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateMyFilesView(APIView):
    """Authenticated user's templates (filesystem + metadata).

    GET /api/v1/templates/files/mine/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        templates_dir = _templates_dir()
        if not os.path.isdir(templates_dir):
            return Response({
                'success': True,
                'count': 0,
                'results': [],
                'message': 'Templates directory not found'
            }, status=status.HTTP_200_OK)

        user_id = getattr(request.user, 'user_id', None)
        user_id_str = str(user_id) if user_id else None
        email = getattr(request.user, 'email', None)

        files = [f for f in os.listdir(templates_dir) if f.lower().endswith('.txt')]
        files.sort(key=lambda f: os.path.getmtime(os.path.join(templates_dir, f)), reverse=True)

        results = []
        for f in files:
            path = os.path.join(templates_dir, f)
            meta = _read_template_meta(path)
            if not meta:
                continue

            meta_created_by_id = meta.get('created_by_id')
            meta_created_by_id_str = str(meta_created_by_id) if meta_created_by_id else None

            if user_id_str and meta_created_by_id_str == user_id_str:
                pass
            elif email and meta.get('created_by_email') == email:
                pass
            else:
                continue

            try:
                mtime = timezone.datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.get_current_timezone())
                ctime = timezone.datetime.fromtimestamp(os.path.getctime(path), tz=timezone.get_current_timezone())
            except Exception:
                mtime = timezone.now()
                ctime = timezone.now()

            results.append({
                'id': f,
                'filename': f,
                'name': _display_name_from_filename(f),
                'contract_type': _infer_template_type(f),
                'status': 'active',
                'created_at': ctime.isoformat(),
                'updated_at': mtime.isoformat(),
                'created_by_id': meta.get('created_by_id'),
                'created_by_email': meta.get('created_by_email'),
                'description': meta.get('description') or '',
            })

        return Response({
            'success': True,
            'count': len(results),
            'results': results,
        }, status=status.HTTP_200_OK)


class TemplateFileContentView(APIView):
    """GET /api/v1/templates/files/content/{filename}/ -> exact raw file content."""

    permission_classes = [AllowAny]

    def get(self, request, filename: str):
        safe = _sanitize_filename(filename)
        templates_dir = _templates_dir()
        path = os.path.join(templates_dir, safe)

        if not os.path.exists(path):
            return Response({
                'success': False,
                'error': 'Template file not found',
                'filename': safe,
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            return Response({
                'success': True,
                'filename': safe,
                'name': _display_name_from_filename(safe),
                'template_type': _infer_template_type(safe),
                'content': content,
                'size': os.path.getsize(path),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to read template file: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
