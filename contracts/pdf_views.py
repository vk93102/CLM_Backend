"""
PDF Generation API Endpoints
Handles contract PDF generation and download
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import FileResponse
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
import logging
import os
from pathlib import Path

from .models import ContractTemplate
from .pdf_service import PDFGenerationService

logger = logging.getLogger(__name__)


class ContractPDFDownloadView(APIView):
    """
    API Endpoint: GET /api/v1/contracts/{id}/download-pdf/
    
    Downloads a contract template as a professional PDF document.
    
    Query Parameters:
        - method: 'weasyprint' | 'reportlab' | 'libreoffice' | 'auto' (default: auto)
        - filename: Custom output filename (default: {template_name}.pdf)
    
    Response:
        - 200 OK: PDF file
        - 404 Not Found: Template not found
        - 500 Server Error: PDF generation failed
    
    Example:
        GET /api/v1/contracts/550e8400-e29b-41d4-a716-446655440000/download-pdf/?method=weasyprint
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, template_id):
        """Download contract as PDF"""
        try:
            # Get contract template
            template = get_object_or_404(ContractTemplate, id=template_id)
            
            # Verify tenant access
            if str(template.tenant_id) != str(request.user.profile.tenant_id):
                return Response(
                    {'error': 'Access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get PDF generation method from query params
            method = request.query_params.get('method', 'auto')
            custom_filename = request.query_params.get('filename', None)
            
            # Validate method
            valid_methods = ['weasyprint', 'reportlab', 'libreoffice', 'auto']
            if method not in valid_methods:
                return Response(
                    {'error': f'Invalid method. Choose from: {", ".join(valid_methods)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Prepare template data for PDF
            template_data = {
                'template_id': str(template.id),
                'template_name': template.name,
                'contract_type': template.contract_type,
                'version': template.version,
                'effective_date': template.created_at.strftime('%B %d, %Y'),
                'first_party_name': template.merge_fields.get('first_party_name', 'Party 1'),
                'first_party_address': template.merge_fields.get('first_party_address', ''),
                'second_party_name': template.merge_fields.get('second_party_name', 'Party 2'),
                'second_party_address': template.merge_fields.get('second_party_address', ''),
                'agreement_type': template.merge_fields.get('agreement_type', 'Standard'),
                'governing_law': template.merge_fields.get('governing_law', 'US Federal Law'),
            }
            
            # Generate PDF
            pdf_service = PDFGenerationService()
            filename = custom_filename or f"{template.name.replace(' ', '_')}.pdf"
            pdf_path = pdf_service.generate_pdf(template_data, filename, method=method)
            
            if not pdf_path:
                logger.error(f"PDF generation failed for template {template_id}")
                return Response(
                    {'error': 'PDF generation failed'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Open and return PDF file
            pdf_file = open(pdf_path, 'rb')
            
            response = FileResponse(
                pdf_file,
                content_type='application/pdf',
                as_attachment=True,
                filename=filename
            )
            
            # Log download
            logger.info(f"PDF downloaded for template {template_id} by user {request.user.id} using method {method}")
            
            return response
        
        except Exception as e:
            logger.error(f"Error downloading PDF for template {template_id}: {str(e)}")
            return Response(
                {'error': f'Error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContractBatchPDFGenerationView(APIView):
    """
    API Endpoint: POST /api/v1/contracts/batch-generate-pdf/
    
    Generates PDFs for multiple contract templates in batch.
    
    Request Body:
        {
            "template_ids": ["id1", "id2", "id3"],
            "method": "weasyprint" (optional, default: auto)
        }
    
    Response:
        {
            "success": true,
            "total": 3,
            "generated": 3,
            "failed": 0,
            "results": {
                "id1": {"status": "success", "path": "/tmp/contract.pdf"},
                "id2": {"status": "failed", "error": "Template not found"}
            }
        }
    
    Example:
        POST /api/v1/contracts/batch-generate-pdf/
        Content-Type: application/json
        
        {
            "template_ids": ["550e8400-e29b-41d4-a716-446655440000"],
            "method": "weasyprint"
        }
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Generate PDFs for multiple templates"""
        try:
            template_ids = request.data.get('template_ids', [])
            method = request.data.get('method', 'auto')
            
            if not template_ids:
                return Response(
                    {'error': 'template_ids is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not isinstance(template_ids, list):
                return Response(
                    {'error': 'template_ids must be a list'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(template_ids) > 100:
                return Response(
                    {'error': 'Maximum 100 templates per batch'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            results = {}
            generated_count = 0
            failed_count = 0
            
            pdf_service = PDFGenerationService()
            
            for template_id in template_ids:
                try:
                    # Get template
                    template = ContractTemplate.objects.filter(id=template_id).first()
                    
                    if not template:
                        results[template_id] = {
                            'status': 'failed',
                            'error': 'Template not found'
                        }
                        failed_count += 1
                        continue
                    
                    # Verify tenant access
                    if str(template.tenant_id) != str(request.user.profile.tenant_id):
                        results[template_id] = {
                            'status': 'failed',
                            'error': 'Access denied'
                        }
                        failed_count += 1
                        continue
                    
                    # Prepare template data
                    template_data = {
                        'template_id': str(template.id),
                        'template_name': template.name,
                        'contract_type': template.contract_type,
                        'version': template.version,
                        'effective_date': template.created_at.strftime('%B %d, %Y'),
                        'first_party_name': template.merge_fields.get('first_party_name', 'Party 1'),
                        'first_party_address': template.merge_fields.get('first_party_address', ''),
                        'second_party_name': template.merge_fields.get('second_party_name', 'Party 2'),
                        'second_party_address': template.merge_fields.get('second_party_address', ''),
                        'agreement_type': template.merge_fields.get('agreement_type', 'Standard'),
                        'governing_law': template.merge_fields.get('governing_law', 'US Federal Law'),
                    }
                    
                    # Generate PDF
                    filename = f"{template.name.replace(' ', '_')}.pdf"
                    pdf_path = pdf_service.generate_pdf(template_data, filename, method=method)
                    
                    if pdf_path:
                        results[template_id] = {
                            'status': 'success',
                            'path': pdf_path,
                            'filename': filename
                        }
                        generated_count += 1
                        logger.info(f"PDF generated for template {template_id}")
                    else:
                        results[template_id] = {
                            'status': 'failed',
                            'error': 'PDF generation returned None'
                        }
                        failed_count += 1
                
                except Exception as e:
                    results[template_id] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    failed_count += 1
                    logger.error(f"Error generating PDF for template {template_id}: {str(e)}")
            
            return Response({
                'success': failed_count == 0,
                'total': len(template_ids),
                'generated': generated_count,
                'failed': failed_count,
                'results': results
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Batch PDF generation error: {str(e)}")
            return Response(
                {'error': f'Error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PDFGenerationStatusView(APIView):
    """
    API Endpoint: GET /api/v1/contracts/pdf-generation-status/
    
    Checks PDF generation capabilities and available methods.
    
    Response:
        {
            "weasyprint": {"available": true, "version": "54.0"},
            "reportlab": {"available": true, "version": "3.6.0"},
            "libreoffice": {"available": false, "version": null},
            "recommended": "weasyprint"
        }
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Check PDF generation capabilities"""
        try:
            status_info = {
                'weasyprint': self._check_weasyprint(),
                'reportlab': self._check_reportlab(),
                'libreoffice': self._check_libreoffice(),
                'recommended': 'weasyprint'
            }
            
            return Response(status_info, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error checking PDF generation status: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def _check_weasyprint():
        """Check if WeasyPrint is available"""
        try:
            import weasyprint
            return {
                'available': True,
                'version': weasyprint.__version__,
                'recommended': True
            }
        except ImportError:
            return {
                'available': False,
                'version': None,
                'install': 'pip install weasyprint'
            }
    
    @staticmethod
    def _check_reportlab():
        """Check if ReportLab is available"""
        try:
            import reportlab
            return {
                'available': True,
                'version': reportlab.Version
            }
        except ImportError:
            return {
                'available': False,
                'version': None,
                'install': 'pip install reportlab'
            }
    
    @staticmethod
    def _check_libreoffice():
        """Check if LibreOffice CLI is available"""
        try:
            import subprocess
            result = subprocess.run(
                ['libreoffice', '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return {
                    'available': True,
                    'version': result.stdout.decode().strip()
                }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return {
            'available': False,
            'version': None,
            'install': 'apt-get install libreoffice'
        }
