"""
PDF Generator from Template .txt Files
Converts filled template files to PDF documents
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from io import BytesIO
import json
import re
from datetime import datetime


class TextToPDFConverter:
    """Converts filled text template to PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='Title',
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            fontName='Helvetica-Bold',
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading',
            fontSize=12,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText',
            fontSize=10,
            spaceAfter=10,
            alignment=4  # Justify
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=3,
            fontName='Helvetica-Oblique'
        ))
    
    def parse_txt_template(self, txt_content):
        """
        Parse filled text template
        Format:
        FIELD_NAME: field_value
        FIELD_NAME2: field_value2
        
        Or:
        # Section Title
        FIELD: value
        """
        sections = {}
        current_section = 'General'
        sections[current_section] = {}
        
        for line in txt_content.split('\n'):
            line = line.strip()
            
            if not line:
                continue
            
            # Section headers
            if line.startswith('# '):
                current_section = line[2:]
                sections[current_section] = {}
            
            # Field: value pairs
            elif ':' in line:
                field, value = line.split(':', 1)
                sections[current_section][field.strip()] = value.strip()
        
        return sections
    
    def txt_to_pdf(self, txt_content, filename='contract.pdf', title='Contract Document'):
        """
        Convert txt template to PDF
        
        Args:
            txt_content: Text content with filled fields
            filename: Output filename
            title: PDF title
        
        Returns:
            BytesIO: PDF binary content
        """
        try:
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1*inch,
                bottomMargin=0.75*inch
            )
            
            elements = []
            
            # Parse template
            sections = self.parse_txt_template(txt_content)
            
            # Add title
            elements.append(Paragraph(title, self.styles['Title']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Add metadata section
            elements.append(Paragraph('Document Information', self.styles['Heading']))
            metadata_data = [
                ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ['Document Type:', title],
                ['Status:', 'Draft']
            ]
            metadata_table = Table(metadata_data, colWidths=[2*inch, 3*inch])
            metadata_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(metadata_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Add sections
            for section_name, fields in sections.items():
                if section_name == 'General':
                    continue  # Skip if already processed
                
                elements.append(Paragraph(section_name, self.styles['Heading']))
                
                # Create field table
                field_data = []
                for field_name, field_value in fields.items():
                    field_data.append([
                        Paragraph(f'<b>{field_name}:</b>', self.styles['FieldLabel']),
                        Paragraph(str(field_value), self.styles['BodyText'])
                    ])
                
                if field_data:
                    field_table = Table(field_data, colWidths=[2.5*inch, 3.5*inch])
                    field_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f9f9f9')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
                    ]))
                    elements.append(field_table)
                
                elements.append(Spacer(1, 0.2*inch))
            
            # Add footer
            elements.append(Spacer(1, 0.2*inch))
            footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
            elements.append(Paragraph(footer_text, self.styles['FieldLabel']))
            
            # Build PDF
            doc.build(elements)
            pdf_buffer.seek(0)
            return pdf_buffer
        
        except Exception as e:
            print(f"Error converting to PDF: {str(e)}")
            return None
    
    def generate_sample_txt(self, template_type='nda'):
        """Generate sample .txt template for testing"""
        samples = {
            'nda': """# Non-Disclosure Agreement

Effective Date: 2026-01-20
Term (Months): 12

# Party Information
Company Name: TechCorp Inc
Company Address: 123 Tech Street, San Francisco, CA 94105
Recipient Name: John Doe
Recipient Email: john@example.com

# Agreement Terms
Governing Law: California
Confidential Information: All technical data, business plans, and proprietary information
Additional Terms: Mutual non-disclosure agreement between parties

# Signatures
Company Representative: Jane Smith
Signer Date: 2026-01-20
Acknowledgment: Received and acknowledged by recipient""",

            'employment': """# Employment Contract

Effective Date: 2026-01-20
Employment Start Date: 2026-02-01

# Employee Information
Employee Name: John Doe
Job Title: Senior Software Engineer
Department: Engineering

# Compensation
Salary: $150,000
Currency: USD
Pay Frequency: Monthly
Vacation Days: 20

# Position Details
Work Location: San Francisco, CA
Reporting To: Engineering Manager

# Terms
Notice Period: 30 Days
Governing Law: California
Confidentiality Terms: All company information is confidential
Benefits: Health insurance, 401k, stock options""",

            'service': """# Service Agreement

Effective Date: 2026-01-20
Service Start Date: 2026-02-01
Service End Date: 2026-08-31

# Service Provider Information
Service Provider: ABC Consulting Inc
Client Name: XYZ Corporation

# Service Details
Service Description: Full-stack web development services
Project Price: $50,000
Payment Schedule: Monthly installments of $8,333

# Deliverables
Deliverables: Fully functional web application with documentation
Milestones: Phase 1 (Feb), Phase 2 (Apr), Phase 3 (Jun), Final (Aug)

# Terms
Intellectual Property: Rights transfer to client upon payment
Termination Clause: Either party can terminate with 30 days notice"""
        }
        
        return samples.get(template_type, samples['nda'])
