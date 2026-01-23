"""
Contract Template Definitions and Documentation
Defines all supported contract template types with required fields and examples
"""

TEMPLATE_TYPES = {
    "NDA": {
        "display_name": "Non-Disclosure Agreement",
        "description": "Protects confidential information exchanged between parties",
        "contract_type": "NDA",
        "required_fields": [
            "effective_date",
            "first_party_name",
            "first_party_address",
            "second_party_name",
            "second_party_address",
            "agreement_type",  # Unilateral or Mutual
            "governing_law"
        ],
        "optional_fields": [
            "duration_months",
            "confidentiality_definition",
            "permitted_disclosures",
            "return_of_materials",
            "additional_terms"
        ],
        "mandatory_clauses": [
            "CONF-001",  # Confidentiality obligations
            "TERM-001",  # Termination clause
            "LIAB-001"   # Liability limitations
        ],
        "business_rules": {
            "required_fields": [
                "effective_date",
                "first_party_name",
                "second_party_name"
            ]
        },
        "sample_data": {
            "effective_date": "2026-01-20",
            "first_party_name": "Acme Corp",
            "first_party_address": "123 Business Ave, New York, NY 10001",
            "second_party_name": "Tech Innovations LLC",
            "second_party_address": "456 Innovation St, San Francisco, CA 94105",
            "agreement_type": "Mutual",
            "governing_law": "California",
            "duration_months": 24
        }
    },
    
    "MSA": {
        "display_name": "Master Service Agreement",
        "description": "Establishes terms and conditions for services between parties",
        "contract_type": "MSA",
        "required_fields": [
            "effective_date",
            "client_name",
            "client_address",
            "service_provider_name",
            "service_provider_address",
            "service_description",
            "monthly_fees",
            "payment_terms",
            "sla_uptime"
        ],
        "optional_fields": [
            "implementation_timeline",
            "support_hours",
            "escalation_procedures",
            "renewal_terms",
            "warranty_period"
        ],
        "mandatory_clauses": [
            "TERM-001",  # Term and termination
            "CONF-001",  # Confidentiality
            "LIAB-002",  # Limitation of liability
            "PAY-001"    # Payment terms
        ],
        "business_rules": {
            "required_fields": [
                "effective_date",
                "client_name",
                "service_provider_name",
                "monthly_fees"
            ],
            "min_value": 10000,
            "requires_sla": True
        },
        "sample_data": {
            "effective_date": "2026-02-01",
            "client_name": "Global Enterprises Inc",
            "client_address": "789 Commerce Blvd, Chicago, IL 60601",
            "service_provider_name": "CloudTech Services Ltd",
            "service_provider_address": "321 Tech Drive, Seattle, WA 98101",
            "service_description": "Cloud infrastructure and support services",
            "monthly_fees": 25000,
            "payment_terms": "Net 30",
            "sla_uptime": "99.9%"
        }
    },
    
    "EMPLOYMENT": {
        "display_name": "Employment Agreement",
        "description": "Defines employment terms, compensation, and responsibilities",
        "contract_type": "EMPLOYMENT",
        "required_fields": [
            "effective_date",
            "employer_name",
            "employer_address",
            "employee_name",
            "employee_address",
            "job_title",
            "employment_type",  # Full-time, Part-time, Contract
            "annual_salary",
            "start_date"
        ],
        "optional_fields": [
            "reporting_to",
            "working_hours",
            "vacation_days",
            "benefits_description",
            "probation_period_days",
            "notice_period_days"
        ],
        "mandatory_clauses": [
            "TERM-002",  # Employment term
            "CONF-001",  # Confidentiality
            "IP-001"     # Intellectual property
        ],
        "business_rules": {
            "required_fields": [
                "effective_date",
                "employer_name",
                "employee_name",
                "job_title",
                "annual_salary"
            ]
        },
        "sample_data": {
            "effective_date": "2026-02-15",
            "employer_name": "Digital Solutions Corp",
            "employer_address": "555 Enterprise Lane, Austin, TX 78701",
            "employee_name": "Jane Smith",
            "employee_address": "999 Residential Ave, Austin, TX 78704",
            "job_title": "Senior Software Engineer",
            "employment_type": "Full-time",
            "annual_salary": 150000,
            "start_date": "2026-03-01",
            "vacation_days": 20,
            "probation_period_days": 90
        }
    },
    
    "SERVICE_AGREEMENT": {
        "display_name": "Service Agreement",
        "description": "Defines scope, terms, and conditions for services",
        "contract_type": "SERVICE",
        "required_fields": [
            "effective_date",
            "service_provider_name",
            "service_provider_address",
            "client_name",
            "client_address",
            "scope_of_services",
            "total_project_value",
            "payment_schedule"
        ],
        "optional_fields": [
            "deliverables",
            "timeline",
            "acceptance_criteria",
            "warranty_period",
            "maintenance_terms"
        ],
        "mandatory_clauses": [
            "TERM-001",  # Term
            "PAY-001",   # Payment
            "LIAB-001"   # Liability
        ],
        "business_rules": {
            "required_fields": [
                "effective_date",
                "service_provider_name",
                "client_name",
                "total_project_value"
            ],
            "min_value": 5000
        },
        "sample_data": {
            "effective_date": "2026-01-25",
            "service_provider_name": "Creative Agency Plus",
            "service_provider_address": "777 Design St, Los Angeles, CA 90001",
            "client_name": "Brand Marketing Co",
            "client_address": "888 Commerce St, Los Angeles, CA 90002",
            "scope_of_services": "Website design and development services",
            "total_project_value": 50000,
            "payment_schedule": "50% upfront, 50% on completion",
            "timeline": "90 days"
        }
    },
    
    "AGENCY_AGREEMENT": {
        "display_name": "Agency Agreement",
        "description": "Appoints an agent to perform services on behalf of principal",
        "contract_type": "AGENCY",
        "required_fields": [
            "effective_date",
            "principal_name",
            "principal_address",
            "agent_name",
            "agent_address",
            "scope_of_agency",
            "compensation_structure"
        ],
        "optional_fields": [
            "termination_clause",
            "commission_percentage",
            "expense_reimbursement",
            "territory",
            "exclusivity"
        ],
        "mandatory_clauses": [
            "TERM-001",  # Agency term
            "CONF-001",  # Confidentiality
            "PAY-001"    # Payment
        ],
        "business_rules": {
            "required_fields": [
                "effective_date",
                "principal_name",
                "agent_name"
            ]
        },
        "sample_data": {
            "effective_date": "2026-01-20",
            "principal_name": "International Trading Ltd",
            "principal_address": "100 Trade Center, Miami, FL 33101",
            "agent_name": "Sales Representatives Inc",
            "agent_address": "200 Sales Ave, Miami, FL 33102",
            "scope_of_agency": "Sales and business development in North America",
            "compensation_structure": "Commission-based",
            "commission_percentage": 10,
            "territory": "North America"
        }
    },
    
    "PROPERTY_MANAGEMENT": {
        "display_name": "Property Management Agreement",
        "description": "Manages property rental and maintenance on behalf of owner",
        "contract_type": "PROPERTY_MGMT",
        "required_fields": [
            "effective_date",
            "owner_name",
            "owner_address",
            "manager_name",
            "manager_address",
            "property_address",
            "management_fees_percentage",
            "services_included"
        ],
        "optional_fields": [
            "repair_approval_limit",
            "lease_term",
            "maintenance_standards",
            "tenant_screening_criteria",
            "accounting_frequency"
        ],
        "mandatory_clauses": [
            "TERM-001",  # Property management term
            "PAY-001",   # Payment and fees
            "LIAB-001"   # Liability
        ],
        "business_rules": {
            "required_fields": [
                "effective_date",
                "owner_name",
                "manager_name",
                "property_address"
            ]
        },
        "sample_data": {
            "effective_date": "2026-02-01",
            "owner_name": "Real Estate Holdings LLC",
            "owner_address": "300 Property Ln, Denver, CO 80202",
            "manager_name": "Professional Property Management",
            "manager_address": "400 Management Ave, Denver, CO 80203",
            "property_address": "500 Residential Blvd, Denver, CO 80204",
            "management_fees_percentage": 8,
            "services_included": "Tenant management, maintenance, accounting",
            "repair_approval_limit": 5000
        }
    },

    "PURCHASE_AGREEMENT": {
        "display_name": "Purchase Agreement",
        "description": "Defines terms for purchase of goods or services",
        "contract_type": "PURCHASE",
        "required_fields": [
            "effective_date",
            "buyer_name",
            "buyer_address",
            "seller_name",
            "seller_address",
            "item_description",
            "purchase_price",
            "payment_terms",
            "delivery_date"
        ],
        "optional_fields": [
            "warranty",
            "inspection_period",
            "return_policy",
            "shipping_terms",
            "inspection_conditions"
        ],
        "mandatory_clauses": [
            "TERM-001",  # Purchase terms
            "PAY-001",   # Payment
            "LIAB-001"   # Liability
        ],
        "business_rules": {
            "required_fields": [
                "effective_date",
                "buyer_name",
                "seller_name",
                "purchase_price"
            ]
        },
        "sample_data": {
            "effective_date": "2026-01-25",
            "buyer_name": "Manufacturing Solutions Ltd",
            "buyer_address": "600 Industrial Ave, Pittsburgh, PA 15201",
            "seller_name": "Equipment Distributors Inc",
            "seller_address": "700 Supplier Blvd, Pittsburgh, PA 15202",
            "item_description": "Industrial machinery and equipment",
            "purchase_price": 250000,
            "payment_terms": "50% deposit, 50% on delivery",
            "delivery_date": "2026-03-15",
            "warranty": "12 months parts and labor"
        }
    }
}

def get_template_type(contract_type):
    """Get template definition by contract type"""
    return TEMPLATE_TYPES.get(contract_type)

def get_all_template_types():
    """Get all available template types"""
    return TEMPLATE_TYPES

def get_template_summary():
    """Get summary of all template types"""
    return {
        type_key: {
            "display_name": data["display_name"],
            "description": data["description"],
            "required_fields_count": len(data["required_fields"]),
            "optional_fields_count": len(data["optional_fields"]),
            "mandatory_clauses": data["mandatory_clauses"]
        }
        for type_key, data in TEMPLATE_TYPES.items()
    }

def validate_template_data(contract_type, data):
    """Validate that all required fields are present for template type"""
    template = get_template_type(contract_type)
    if not template:
        return False, f"Unknown template type: {contract_type}"
    
    required = template.get("required_fields", [])
    missing = [field for field in required if not data.get(field)]
    
    if missing:
        return False, f"Missing required fields: {missing}"
    
    return True, None
