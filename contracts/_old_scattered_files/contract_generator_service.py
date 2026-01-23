"""
Contract Generator Service - Fills PDF templates with provided data
Supports: NDA, Agency Agreement, Property Management, Employment Contract
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import io

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

logger = logging.getLogger(__name__)

# Template mapping
TEMPLATE_PATHS = {
    'nda': 'templates/NDA.pdf',
    'agency_agreement': 'templates/Agency-Agreement.pdf',
    'property_management': 'templates/Property_management_contract.pdf',
    'employment_contract': 'templates/Employement-Agreement.pdf',
}

# Field definitions for each contract type
CONTRACT_FIELD_DEFINITIONS = {
    'nda': {
        'required': [
            'date',
            '1st_party_name',
            '2nd_party_name',
            'agreement_type',  # 'unilateral' or 'mutual'
            '1st_party_relationship',
            '2nd_party_relationship',
            'governing_law',
            '1st_party_printed_name',
            '2nd_party_printed_name',
        ],
        'optional': ['clauses', 'signed'],
        'sections': {
            'parties': 'Agreement parties and creation date',
            'whereas': 'Purpose: preventing unauthorized disclosure',
            'agreement_type': 'Unilateral or Mutual NDA type',
            'relationship': 'Relationship between parties',
            'definition': 'Definition of confidential information',
            'obligations': 'Party obligations and confidentiality duties',
            'time_frame': 'Duration of confidentiality obligation',
            'integration': 'Complete agreement and amendments',
            'severability': 'Invalidity provision handling',
            'enforcement': 'Breach remedies and equitable relief',
            'governing_law': 'State law jurisdiction',
        },
        'signature_fields': ['1st_party_signature', '2nd_party_signature'],
        'date_fields': ['signature_date_1st_party', 'signature_date_2nd_party'],
    },
    'agency_agreement': {
        'required': [
            'effective_date',
            'principal_name',
            'principal_address',
            'agent_name',
            'agent_address',
            'monthly_compensation',
            'invoice_submission_date',
            'payment_method',
            'payment_address',
            'contract_end_date',
            'principal_printed_name',
            'agent_printed_name',
        ],
        'optional': [
            'service_1',
            'service_2',
            'service_3',
            'service_4',
            'service_5',
            'additional_services',
            'clauses',
            'signed',
        ],
        'sections': {
            'services': 'Services to be performed (up to 5 items)',
            'appointment': 'Principal appoints Agent',
            'scope_of_authority': 'Agent authority limitations',
            'compensation': 'Monthly fees and payment terms',
            'ownership': 'Work product ownership rights',
        },
        'signature_fields': ['principal_signature', 'agent_signature'],
        'date_fields': ['principal_signature_date', 'agent_signature_date'],
    },
    'property_management': {
        'required': [
            'effective_date',
            'owner_name',
            'owner_address',
            'manager_name',
            'manager_address',
            'property_address',
            'repair_approval_limit',
            'governing_law',
            'owner_printed_name',
            'manager_printed_name',
        ],
        'optional': [
            'total_cost_services',
            'amount_at_signing',
            'means_of_payment',
            'termination_period_days',
            'clauses',
            'signed',
        ],
        'sections': {
            'general_terms': 'Property location and appointment details',
            'manager_responsibilities': 'All Manager duties and obligations',
            'payments_fees': 'Compensation and payment terms',
            'termination': 'Contract termination conditions',
            'succession': 'Binding effect on successors',
        },
        'signature_fields': ['owner_signature', 'manager_signature'],
        'date_fields': ['owner_signature_date', 'manager_signature_date'],
    },
    'employment_contract': {
        'required': [
            'effective_date',
            'employer_name',
            'employer_address',
            'employee_name',
            'employee_address',
            'job_title',
            'commencement_date',
            'working_days_from',
            'working_days_to',
            'employment_type',  # 'part_time' or 'full_time'
            'working_hours_from',
            'working_hours_to',
            'average_hours_per_week',
            'daily_lunch_break',
            'work_mode',  # 'remote', 'on_site', or 'hybrid'
            'salary_amount',
            'payment_schedule',
            'payment_method',
            'probation_period',
            'notice_period_termination',
            'employer_printed_name',
            'employee_printed_name',
        ],
        'optional': [
            'responsibility_1',
            'responsibility_2',
            'responsibility_3',
            'responsibility_4',
            'work_location',
            'insurance_benefit',
            'holidays',
            'vacation',
            'wellness',
            'retirement_plan',
            'paid_time_off',
            'clauses',
            'signed',
        ],
        'sections': {
            'title_duties': 'Employee position and responsibilities',
            'start_date_location': 'Working arrangement and schedule',
            'compensation': 'Salary and payment details',
            'probationary_period': 'Trial period terms',
            'expenses_reimbursement': 'Expense handling policy',
        },
        'signature_fields': ['employer_signature', 'employee_signature'],
        'date_fields': ['employer_signature_date', 'employee_signature_date'],
    },
}


class ContractGeneratorService:
    """Service for generating filled PDF contracts"""
    
    def __init__(self, base_path: str = '/Users/vishaljha/CLM_Backend'):
        """Initialize the service with base path"""
        self.base_path = Path(base_path)
        self.templates_path = self.base_path / 'templates'
        
    def validate_contract_type(self, contract_type: str) -> bool:
        """Validate if contract type is supported"""
        return contract_type.lower() in TEMPLATE_PATHS
    
    def get_required_fields(self, contract_type: str) -> Dict[str, list]:
        """Get required and optional fields for a contract type"""
        contract_type = contract_type.lower()
        if contract_type not in CONTRACT_FIELD_DEFINITIONS:
            raise ValueError(f"Unknown contract type: {contract_type}")
        return CONTRACT_FIELD_DEFINITIONS[contract_type]
    
    def validate_contract_data(self, contract_type: str, data: Dict[str, Any]) -> tuple[bool, list]:
        """
        Validate that all required fields are present
        Returns: (is_valid, missing_fields)
        """
        contract_type = contract_type.lower()
        fields_config = self.get_required_fields(contract_type)
        required_fields = fields_config.get('required', [])
        
        missing_fields = []
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                missing_fields.append(field)
        
        is_valid = len(missing_fields) == 0
        return is_valid, missing_fields
    
    def generate_contract(
        self,
        contract_type: str,
        data: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate a filled contract PDF
        
        Args:
            contract_type: Type of contract ('nda', 'agency_agreement', etc.)
            data: Dictionary with contract field values
            output_path: Optional path to save the PDF. If None, generates in temp location
        
        Returns:
            Path to the generated PDF file
        """
        # Validate contract type
        contract_type = contract_type.lower()
        if not self.validate_contract_type(contract_type):
            raise ValueError(f"Unsupported contract type: {contract_type}")
        
        # Validate data
        is_valid, missing_fields = self.validate_contract_data(contract_type, data)
        if not is_valid:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Get template path
        template_relative = TEMPLATE_PATHS[contract_type]
        template_path = self.base_path / template_relative
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        logger.info(f"Generating {contract_type} contract with data keys: {list(data.keys())}")
        
        # Create filled PDF
        filled_pdf = self._fill_pdf_template(
            str(template_path),
            contract_type,
            data
        )
        
        # Save to disk
        if output_path is None:
            output_path = self.base_path / f"generated_{contract_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(filled_pdf)
        
        logger.info(f"Contract generated successfully: {output_path}")
        return str(output_path)
    
    def _fill_pdf_template(
        self,
        template_path: str,
        contract_type: str,
        data: Dict[str, Any]
    ) -> bytes:
        """
        Fill PDF template with data and return as bytes
        Uses ReportLab to overlay text on PDF
        """
        # Read the template PDF
        with open(template_path, 'rb') as f:
            reader = PdfReader(f)
            writer = PdfWriter()
            
            # Get the first page (assuming single page templates)
            page = reader.pages[0]
            
            # Create an overlay with filled data
            overlay_stream = io.BytesIO()
            overlay_canvas = canvas.Canvas(overlay_stream, pagesize=letter)
            
            # Define positioning based on contract type
            positions = self._get_field_positions(contract_type)
            
            # Fill in the fields
            for field_name, value in data.items():
                if field_name in positions:
                    x, y = positions[field_name]
                    self._draw_field_value(overlay_canvas, field_name, str(value), x, y, contract_type)
            
            overlay_canvas.save()
            overlay_stream.seek(0)
            
            # Read the overlay
            overlay_reader = PdfReader(overlay_stream)
            overlay_page = overlay_reader.pages[0]
            
            # Merge overlay with template
            page.merge_page(overlay_page)
            writer.add_page(page)
            
            # Write output
            output_stream = io.BytesIO()
            writer.write(output_stream)
            output_stream.seek(0)
            return output_stream.read()
    
    def _get_field_positions(self, contract_type: str) -> Dict[str, tuple]:
        """
        Get (x, y) positions for fields on each contract type
        Positions are approximate based on standard PDF layouts
        """
        if contract_type == 'nda':
            return {
                'date': (450, 750),
                '1st_party_name': (250, 700),
                '2nd_party_name': (250, 670),
                'agreement_type': (120, 640),
                '1st_party_relationship': (250, 600),
                '2nd_party_relationship': (250, 570),
                'governing_law': (250, 540),
                '1st_party_printed_name': (100, 200),
                '1st_party_signature': (100, 170),
                'signature_date_1st_party': (300, 170),
                '2nd_party_printed_name': (400, 200),
                '2nd_party_signature': (400, 170),
                'signature_date_2nd_party': (600, 170),
            }
        
        elif contract_type == 'agency_agreement':
            return {
                'effective_date': (450, 750),
                'principal_name': (250, 710),
                'principal_address': (250, 680),
                'agent_name': (250, 640),
                'agent_address': (250, 610),
                'monthly_compensation': (250, 520),
                'invoice_submission_date': (250, 490),
                'payment_method': (250, 460),
                'payment_address': (250, 430),
                'contract_end_date': (250, 400),
                'principal_printed_name': (100, 150),
                'principal_signature': (100, 120),
                'principal_signature_date': (300, 120),
                'agent_printed_name': (400, 150),
                'agent_signature': (400, 120),
                'agent_signature_date': (600, 120),
            }
        
        elif contract_type == 'property_management':
            return {
                'effective_date': (450, 750),
                'owner_name': (250, 710),
                'owner_address': (250, 680),
                'manager_name': (250, 640),
                'manager_address': (250, 610),
                'property_address': (250, 560),
                'repair_approval_limit': (250, 530),
                'governing_law': (250, 500),
                'owner_printed_name': (100, 150),
                'owner_signature': (100, 120),
                'owner_signature_date': (300, 120),
                'manager_printed_name': (400, 150),
                'manager_signature': (400, 120),
                'manager_signature_date': (600, 120),
            }
        
        elif contract_type == 'employment_contract':
            return {
                'effective_date': (450, 750),
                'employer_name': (250, 720),
                'employer_address': (250, 690),
                'employee_name': (250, 650),
                'employee_address': (250, 620),
                'job_title': (250, 580),
                'responsibilities': (250, 550),
                'commencement_date': (250, 510),
                'working_days_from': (150, 480),
                'working_days_to': (350, 480),
                'employment_type': (150, 450),
                'working_hours_from': (250, 420),
                'working_hours_to': (350, 420),
                'average_hours_per_week': (250, 390),
                'daily_lunch_break': (250, 360),
                'work_mode': (150, 330),
                'work_location': (250, 300),
                'salary_amount': (250, 260),
                'payment_schedule': (250, 230),
                'payment_method': (250, 200),
                'probation_period': (250, 170),
                'insurance_benefit': (250, 130),
                'holidays': (250, 100),
                'employer_printed_name': (100, 50),
                'employee_printed_name': (400, 50),
            }
        
        return {}
    
    def _draw_field_value(
        self,
        canvas_obj: canvas.Canvas,
        field_name: str,
        value: str,
        x: float,
        y: float,
        contract_type: str
    ) -> None:
        """Draw a field value on the canvas"""
        try:
            # Format value based on field type
            if 'date' in field_name and not value:
                value = datetime.now().strftime('%m/%d/%Y')
            
            # Truncate long values
            if len(value) > 50:
                value = value[:47] + "..."
            
            # Set font
            canvas_obj.setFont("Helvetica", 10)
            canvas_obj.setFillColor(colors.black)
            
            # Handle checkboxes
            if field_name == 'agreement_type':
                # This would be handled separately in a real implementation
                pass
            elif field_name == 'employment_type':
                # This would be handled separately
                pass
            elif field_name == 'work_mode':
                # This would be handled separately
                pass
            else:
                # Draw regular text
                canvas_obj.drawString(x, y, value)
            
            logger.debug(f"Drew {field_name} at ({x}, {y}): {value[:30]}")
        
        except Exception as e:
            logger.warning(f"Error drawing field {field_name}: {str(e)}")


# Convenience function
def generate_contract(
    contract_type: str,
    data: Dict[str, Any],
    output_path: Optional[str] = None,
) -> str:
    """
    Generate a contract - convenience function
    """
    service = ContractGeneratorService()
    return service.generate_contract(contract_type, data, output_path)
