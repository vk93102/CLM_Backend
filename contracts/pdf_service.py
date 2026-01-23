#!/usr/bin/env python3
"""
PDF Generation Service - Production Ready Implementation
Supports multiple PDF generation methods with fallback options
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)

# HTML Template for Contract PDF
CONTRACT_PDF_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ template_name }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        @page {
            size: letter;
            margin: 0.75in;
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10px;
            }
        }
        
        body {
            font-family: 'Segoe UI', 'Calibri', 'Arial', sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background-color: white;
        }
        
        /* Header */
        .header {
            border-bottom: 3px solid #1f4e78;
            padding-bottom: 0.5in;
            margin-bottom: 0.75in;
            text-align: center;
        }
        
        .header h1 {
            font-size: 32px;
            color: #1f4e78;
            margin-bottom: 0.25in;
            font-weight: 700;
        }
        
        .header-meta {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: #666;
            margin-top: 0.25in;
        }
        
        /* Sections */
        .section {
            margin: 0.5in 0;
            page-break-inside: avoid;
        }
        
        .section-title {
            background-color: #e8f0f7;
            color: #1f4e78;
            padding: 0.25in 0.375in;
            margin: 0.5in 0 0.25in 0;
            font-weight: 700;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-left: 4px solid #1f4e78;
        }
        
        .section-content {
            padding: 0 0.375in;
            line-height: 1.8;
        }
        
        /* Field Display */
        .field-group {
            margin: 0.25in 0;
            display: flex;
            flex-wrap: wrap;
        }
        
        .field {
            flex: 1 1 45%;
            margin: 0.125in 0.25in 0.125in 0;
            min-width: 200px;
        }
        
        .field-label {
            font-weight: 700;
            color: #1f4e78;
            font-size: 11px;
            text-transform: uppercase;
            margin-bottom: 0.1in;
        }
        
        .field-value {
            color: #333;
            padding: 0.1in 0.1in;
            background-color: #f9f9f9;
            border-left: 2px solid #ddd;
            padding-left: 0.15in;
        }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 0.5in 0;
            font-size: 11px;
        }
        
        table thead {
            background-color: #e8f0f7;
            color: #1f4e78;
        }
        
        table th {
            padding: 0.25in;
            text-align: left;
            font-weight: 700;
            border-bottom: 2px solid #1f4e78;
        }
        
        table td {
            padding: 0.2in 0.25in;
            border-bottom: 1px solid #e0e0e0;
        }
        
        table tbody tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        /* Signature Section */
        .signature-section {
            margin: 1.5in 0 0 0;
            padding-top: 0.75in;
            border-top: 1px solid #ddd;
            page-break-inside: avoid;
        }
        
        .signature-block {
            display: flex;
            justify-content: space-between;
            margin-top: 0.75in;
        }
        
        .signature-column {
            width: 45%;
            min-width: 200px;
        }
        
        .signature-line {
            border-top: 2px solid #333;
            margin-bottom: 0.1in;
            min-width: 180px;
            height: 0.75in;
        }
        
        .signature-name {
            font-weight: 700;
            color: #1f4e78;
            font-size: 11px;
            margin-bottom: 0.1in;
        }
        
        .signature-title {
            font-size: 10px;
            color: #666;
            margin-bottom: 0.25in;
        }
        
        .signature-date {
            margin-top: 0.2in;
            font-size: 10px;
        }
        
        /* Footer */
        .footer {
            margin-top: 1in;
            padding-top: 0.5in;
            border-top: 1px solid #ddd;
            font-size: 9px;
            color: #999;
            text-align: center;
        }
        
        .footer p {
            margin: 0.1in 0;
        }
        
        /* Utilities */
        .page-break {
            page-break-after: always;
        }
        
        .no-page-break {
            page-break-inside: avoid;
        }
        
        .flex-center {
            text-align: center;
        }
        
        .highlight {
            background-color: #fff3cd;
            padding: 0.25in;
            border-left: 3px solid #ffc107;
        }
    </style>
</head>
<body>
    <!-- Document Header -->
    <div class="header">
        <h1>{{ template_name }}</h1>
        <div class="header-meta">
            <div>
                <strong>Document ID:</strong> {{ template_id }}<br>
                <strong>Type:</strong> {{ contract_type }}
            </div>
            <div>
                <strong>Generated:</strong> {{ generation_date }}<br>
                <strong>Version:</strong> {{ version }}
            </div>
        </div>
    </div>

    <!-- Agreement Information Section -->
    <div class="section">
        <div class="section-title">Agreement Information</div>
        <div class="section-content">
            <div class="field-group">
                <div class="field">
                    <div class="field-label">Effective Date</div>
                    <div class="field-value">{{ effective_date }}</div>
                </div>
                <div class="field">
                    <div class="field-label">Agreement Type</div>
                    <div class="field-value">{{ agreement_type }}</div>
                </div>
                <div class="field">
                    <div class="field-label">Governing Law</div>
                    <div class="field-value">{{ governing_law }}</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Parties Section -->
    <div class="section">
        <div class="section-title">Parties to the Agreement</div>
        <div class="section-content">
            <table>
                <thead>
                    <tr>
                        <th>Party Name</th>
                        <th>Address</th>
                        <th>Role</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>{{ first_party_name }}</strong></td>
                        <td>{{ first_party_address }}</td>
                        <td>First Party</td>
                    </tr>
                    <tr>
                        <td><strong>{{ second_party_name }}</strong></td>
                        <td>{{ second_party_address }}</td>
                        <td>Second Party</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Terms & Conditions Section -->
    <div class="section">
        <div class="section-title">Terms & Conditions</div>
        <div class="section-content no-page-break">
            <p style="margin-bottom: 0.25in;">
                The parties agree to the following terms and conditions effective as of the above date:
            </p>
            
            <div style="margin: 0.25in 0; padding: 0.25in; border-left: 3px solid #e8f0f7;">
                <strong style="color: #1f4e78;">1. Confidentiality Obligations</strong>
                <p style="margin-top: 0.1in; font-size: 11px;">
                    The Receiving Party agrees to maintain all Confidential Information in strict confidence 
                    and use it solely for the purpose outlined in this agreement.
                </p>
            </div>
            
            <div style="margin: 0.25in 0; padding: 0.25in; border-left: 3px solid #e8f0f7;">
                <strong style="color: #1f4e78;">2. Non-Disclosure</strong>
                <p style="margin-top: 0.1in; font-size: 11px;">
                    Neither party shall disclose the Confidential Information to any third party without 
                    prior written consent, except to its employees and advisors who have a need to know.
                </p>
            </div>
            
            <div style="margin: 0.25in 0; padding: 0.25in; border-left: 3px solid #e8f0f7;">
                <strong style="color: #1f4e78;">3. Return of Information</strong>
                <p style="margin-top: 0.1in; font-size: 11px;">
                    Upon request or termination of this agreement, all Confidential Information shall be 
                    returned or destroyed, as directed by the Disclosing Party.
                </p>
            </div>
        </div>
    </div>

    <!-- Page Break -->
    <div class="page-break"></div>

    <!-- Signatures Section -->
    <div class="signature-section">
        <div class="section-title">Authorized Signatures</div>
        <div class="signature-block">
            <div class="signature-column">
                <div class="signature-line"></div>
                <div class="signature-name">{{ first_party_name }}</div>
                <div class="signature-title">Authorized Representative</div>
                <div class="signature-date">Date: ___________________</div>
                <div style="margin-top: 0.1in; font-size: 10px;">Print Name: ___________________</div>
            </div>
            <div class="signature-column">
                <div class="signature-line"></div>
                <div class="signature-name">{{ second_party_name }}</div>
                <div class="signature-title">Authorized Representative</div>
                <div class="signature-date">Date: ___________________</div>
                <div style="margin-top: 0.1in; font-size: 10px;">Print Name: ___________________</div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <div class="footer">
        <p><strong>Confidentiality Notice:</strong> This document contains confidential and proprietary information. 
        Unauthorized disclosure is strictly prohibited.</p>
        <p style="margin-top: 0.1in;">
            Generated by Contract Management System | 
            <strong>{{ generation_date }}</strong> | 
            Document ID: {{ template_id }}
        </p>
    </div>
</body>
</html>
"""

class PDFGenerationService:
    """
    Multi-method PDF generation service with fallback options
    Methods: WeasyPrint (primary), ReportLab (fallback), Command-line (tertiary)
    """
    
    def __init__(self, output_dir: str = '/tmp/contract_pdfs'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template = Template(CONTRACT_PDF_TEMPLATE)
    
    def generate_pdf(
        self,
        template_data: Dict[str, Any],
        output_filename: str = None,
        method: str = 'weasyprint'
    ) -> Optional[str]:
        """
        Generate PDF with specified method
        
        Args:
            template_data: Dictionary with template fields
            output_filename: Output filename (default: template_id.pdf)
            method: 'weasyprint', 'reportlab', 'libreoffice', or 'auto'
        
        Returns:
            Path to generated PDF, or None if failed
        """
        if not output_filename:
            output_filename = f"{template_data.get('template_id', 'contract')}.pdf"
        
        output_path = self.output_dir / output_filename
        
        try:
            if method == 'auto':
                return self._generate_auto(template_data, output_path)
            elif method == 'weasyprint':
                return self._generate_weasyprint(template_data, output_path)
            elif method == 'reportlab':
                return self._generate_reportlab(template_data, output_path)
            elif method == 'libreoffice':
                return self._generate_libreoffice(template_data, output_path)
            else:
                logger.error(f"Unknown PDF method: {method}")
                return None
        
        except Exception as e:
            logger.error(f"PDF generation failed ({method}): {str(e)}")
            return None
    
    def _generate_auto(self, template_data: Dict[str, Any], output_path: Path) -> Optional[str]:
        """Try methods in order of preference with fallback"""
        methods = ['weasyprint', 'reportlab', 'libreoffice']
        
        for method in methods:
            try:
                result = self.generate_pdf(template_data, str(output_path.name), method)
                if result:
                    logger.info(f"PDF generated using {method}: {output_path}")
                    return result
            except Exception as e:
                logger.warning(f"Method {method} failed: {str(e)}")
                continue
        
        logger.error("All PDF generation methods failed")
        return None
    
    def _generate_weasyprint(
        self,
        template_data: Dict[str, Any],
        output_path: Path
    ) -> Optional[str]:
        """Generate PDF using WeasyPrint (RECOMMENDED)"""
        try:
            from weasyprint import HTML
            
            # Add generation date
            template_data['generation_date'] = datetime.now().strftime('%B %d, %Y at %I:%M %p')
            
            # Render HTML
            html_content = self.template.render(**template_data)
            
            # Generate PDF
            HTML(string=html_content).write_pdf(str(output_path))
            
            logger.info(f"PDF generated with WeasyPrint: {output_path}")
            return str(output_path)
        
        except ImportError:
            logger.error("WeasyPrint not installed")
            return None
    
    def _generate_reportlab(
        self,
        template_data: Dict[str, Any],
        output_path: Path
    ) -> Optional[str]:
        """Generate PDF using ReportLab (FALLBACK)"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import inch
            
            c = canvas.Canvas(str(output_path), pagesize=letter)
            w, h = letter
            
            # Draw header
            c.setFont("Helvetica-Bold", 24)
            c.drawString(inch, h - inch, template_data.get('template_name', 'CONTRACT'))
            
            # Draw metadata
            c.setFont("Helvetica", 10)
            c.drawString(inch, h - 1.25*inch, f"ID: {template_data.get('template_id', '')}")
            c.drawString(inch, h - 1.4*inch, f"Type: {template_data.get('contract_type', '')}")
            
            # Draw content
            y = h - 1.75*inch
            c.setFont("Helvetica", 11)
            
            lines = [
                f"Effective Date: {template_data.get('effective_date', '')}",
                f"First Party: {template_data.get('first_party_name', '')}",
                f"Second Party: {template_data.get('second_party_name', '')}",
                f"Governing Law: {template_data.get('governing_law', '')}",
                "",
                "This agreement contains confidential information. Unauthorized disclosure is prohibited.",
            ]
            
            for line in lines:
                if y < inch:
                    c.showPage()
                    y = h - inch
                c.drawString(inch, y, line)
                y -= 0.25*inch
            
            # Add signature section
            y -= 0.75*inch
            c.setFont("Helvetica-Bold", 11)
            c.drawString(inch, y, "AUTHORIZED SIGNATURES")
            
            c.setFont("Helvetica", 11)
            y -= 0.5*inch
            c.drawString(inch, y, "_" * 40)
            c.drawString(inch, y - 0.25*inch, f"{template_data.get('first_party_name', '')}")
            
            y -= 1*inch
            c.drawString(inch, y, "_" * 40)
            c.drawString(inch, y - 0.25*inch, f"{template_data.get('second_party_name', '')}")
            
            c.save()
            
            logger.info(f"PDF generated with ReportLab: {output_path}")
            return str(output_path)
        
        except ImportError:
            logger.error("ReportLab not installed")
            return None
    
    def _generate_libreoffice(
        self,
        template_data: Dict[str, Any],
        output_path: Path
    ) -> Optional[str]:
        """Generate PDF using LibreOffice CLI (for complex documents)"""
        try:
            import subprocess
            
            # First generate HTML to temp file
            html_content = self.template.render(**template_data)
            html_path = self.output_dir / f"{output_path.stem}.html"
            
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            # Convert HTML to PDF using LibreOffice
            result = subprocess.run(
                [
                    'libreoffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', str(self.output_dir),
                    str(html_path)
                ],
                capture_output=True,
                timeout=30
            )
            
            # Clean up HTML
            html_path.unlink()
            
            if result.returncode == 0:
                logger.info(f"PDF generated with LibreOffice: {output_path}")
                return str(output_path)
            else:
                logger.error(f"LibreOffice conversion failed: {result.stderr}")
                return None
        
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.error(f"LibreOffice not available: {str(e)}")
            return None
    
    def batch_generate(
        self,
        templates_data: list,
        method: str = 'auto'
    ) -> Dict[str, str]:
        """Generate PDFs for multiple templates"""
        results = {}
        
        for template_data in templates_data:
            template_id = template_data.get('template_id', 'unknown')
            try:
                pdf_path = self.generate_pdf(template_data, method=method)
                if pdf_path:
                    results[template_id] = {'status': 'success', 'path': pdf_path}
                else:
                    results[template_id] = {'status': 'failed', 'error': 'PDF generation returned None'}
            except Exception as e:
                results[template_id] = {'status': 'failed', 'error': str(e)}
        
        return results


# Example usage
if __name__ == '__main__':
    # Initialize service
    pdf_service = PDFGenerationService()
    
    # Sample template data
    sample_data = {
        'template_id': 'TPL-001-NDA-2026',
        'template_name': 'Standard Non-Disclosure Agreement',
        'contract_type': 'NDA',
        'version': '1.0',
        'effective_date': '2026-01-20',
        'agreement_type': 'Mutual',
        'governing_law': 'California',
        'first_party_name': 'Acme Corporation',
        'first_party_address': '123 Business Ave, San Francisco, CA 94102',
        'second_party_name': 'Tech Innovations Inc',
        'second_party_address': '456 Innovation Blvd, Palo Alto, CA 94301',
    }
    
    # Generate PDF with auto-fallback
    print("Generating PDF with auto-fallback...")
    pdf_path = pdf_service.generate_pdf(sample_data, method='auto')
    
    if pdf_path:
        print(f"✅ PDF generated successfully: {pdf_path}")
    else:
        print("❌ PDF generation failed")
    
    # Batch generation example
    print("\nBatch generating PDFs...")
    templates = [sample_data.copy() for i in range(3)]
    for i, t in enumerate(templates):
        t['template_id'] = f"TPL-{i+1:03d}"
        t['template_name'] = f"Contract #{i+1}"
    
    results = pdf_service.batch_generate(templates, method='auto')
    
    print(f"\nBatch Results:")
    for tid, result in results.items():
        status = result['status']
        msg = f"✅ {tid}: {result['path']}" if status == 'success' else f"❌ {tid}: {result.get('error', 'Unknown error')}"
        print(msg)
