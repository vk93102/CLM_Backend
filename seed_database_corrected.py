"""
Comprehensive Database Seeding Script - CORRECTED VERSION
Creates realistic test data for contracts, templates, approvals, and users
"""

import os
import django
import sys
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from random import choice, randint

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
sys.path.insert(0, '/Users/vishaljha/CLM_Backend')
django.setup()

from authentication.models import User
from contracts.models import Contract, ContractTemplate
from tenants.models import TenantModel
from audit_logs.models import AuditLogModel

def create_tenants():
    """Create sample tenants"""
    print("\n📌 Creating Tenants...")
    
    tenants_data = [
        {
            "name": "Acme Corporation",
            "domain": "acme.local",
            "status": "active",
            "subscription_plan": "enterprise"
        },
        {
            "name": "TechStart Inc",
            "domain": "techstart.local",
            "status": "active",
            "subscription_plan": "professional"
        },
        {
            "name": "Global Services Ltd",
            "domain": "globalservices.local",
            "status": "active",
            "subscription_plan": "professional"
        },
        {
            "name": "Enterprise Solutions",
            "domain": "enterprise-solutions.local",
            "status": "active",
            "subscription_plan": "enterprise"
        }
    ]
    
    created_tenants = []
    
    for tenant_data in tenants_data:
        try:
            tenant, created = TenantModel.objects.get_or_create(
                name=tenant_data["name"],
                defaults={
                    "domain": tenant_data["domain"],
                    "status": tenant_data["status"],
                    "subscription_plan": tenant_data["subscription_plan"],
                    "metadata": {
                        "description": f"Organization: {tenant_data['name']}"
                    }
                }
            )
            
            if created:
                created_tenants.append(tenant)
                print(f"  ✓ Created tenant: {tenant.name}")
            else:
                created_tenants.append(tenant)
                print(f"  • Tenant already exists: {tenant.name}")
        except Exception as e:
            print(f"  ✗ Error creating tenant: {str(e)}")
    
    return created_tenants

def create_users(tenants):
    """Create sample users with different roles"""
    print("\n👥 Creating Users...")
    
    users_data = [
        {
            "email": "admin@clm.local",
            "first_name": "Admin",
            "last_name": "User",
            "is_staff": True,
            "is_superuser": True,
            "password": "admin123",
            "tenant": tenants[0] if tenants else None
        },
        {
            "email": "manager@clm.local",
            "first_name": "John",
            "last_name": "Manager",
            "is_staff": True,
            "is_superuser": False,
            "password": "manager123",
            "tenant": tenants[0] if tenants else None
        },
        {
            "email": "approver@clm.local",
            "first_name": "Jane",
            "last_name": "Approver",
            "is_staff": False,
            "is_superuser": False,
            "password": "approver123",
            "tenant": tenants[1] if len(tenants) > 1 else tenants[0]
        },
        {
            "email": "vendor@clm.local",
            "first_name": "Bob",
            "last_name": "Vendor",
            "is_staff": False,
            "is_superuser": False,
            "password": "vendor123",
            "tenant": tenants[1] if len(tenants) > 1 else tenants[0]
        },
        {
            "email": "analyst@clm.local",
            "first_name": "Alice",
            "last_name": "Analyst",
            "is_staff": False,
            "is_superuser": False,
            "password": "analyst123",
            "tenant": tenants[2] if len(tenants) > 2 else tenants[0]
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        try:
            tenant = user_data.pop("tenant", None)
            password = user_data.pop("password")
            
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults=user_data
            )
            
            if created:
                user.set_password(password)
                if tenant:
                    user.tenant_id = tenant.id
                user.save()
                created_users.append(user)
                print(f"  ✓ Created user: {user.email}")
            else:
                created_users.append(user)
                print(f"  • User already exists: {user.email}")
        except Exception as e:
            print(f"  ✗ Error creating user: {str(e)}")
    
    return created_users

def create_templates(tenants, users):
    """Create contract templates"""
    print("\n📋 Creating Contract Templates...")
    
    templates_data = [
        {
            "name": "Standard Service Agreement",
            "contract_type": "Service",
            "description": "General service agreement template"
        },
        {
            "name": "Software License Template",
            "contract_type": "License",
            "description": "Software licensing agreement"
        },
        {
            "name": "NDA Template",
            "contract_type": "NDA",
            "description": "Non-disclosure agreement"
        },
    ]
    
    created_templates = []
    
    for template_data in templates_data:
        try:
            tenant = choice(tenants) if tenants else None
            user = choice(users) if users else None
            
            template, created = ContractTemplate.objects.get_or_create(
                name=template_data["name"],
                tenant_id=tenant.id if tenant else uuid.uuid4(),
                defaults={
                    "contract_type": template_data["contract_type"],
                    "description": template_data["description"],
                    "r2_key": f"templates/{template_data['name'].lower().replace(' ', '_')}.docx",
                    "created_by": user.user_id if user else uuid.uuid4(),
                    "merge_fields": ["company_name", "contract_value", "effective_date"],
                    "mandatory_clauses": [],
                    "business_rules": {}
                }
            )
            
            if created:
                created_templates.append(template)
                print(f"  ✓ Created template: {template.name}")
            else:
                created_templates.append(template)
                print(f"  • Template already exists: {template.name}")
        except Exception as e:
            print(f"  ✗ Error creating template: {str(e)}")
    
    return created_templates

def create_contracts(users, tenants, templates):
    """Create sample contracts with realistic data"""
    print("\n📄 Creating Contracts...")
    
    contract_titles = [
        "Service Agreement - Cloud Services",
        "Software License Agreement",
        "Maintenance and Support Contract",
        "Professional Services Agreement",
        "Vendor Agreement - IT Consulting",
        "Master Service Agreement",
        "Outsourcing Agreement",
        "Support and Maintenance Contract",
        "Development Services Agreement",
        "Hosting and Infrastructure Agreement"
    ]
    
    statuses = ["draft", "pending", "approved", "executed", "rejected"]
    counterparties = [
        "Acme Inc",
        "TechCorp Ltd",
        "Global Solutions",
        "CloudServices Inc",
        "Software Innovations",
        "IT Consultants Ltd",
        "Enterprise Tech",
        "Digital Solutions"
    ]
    
    created_contracts = []
    
    for i in range(10):
        try:
            user = choice(users) if users else None
            tenant = choice(tenants) if tenants else None
            template = choice(templates) if templates else None
            
            contract_data = {
                "title": contract_titles[i % len(contract_titles)],
                "description": f"Contract for {choice(['service delivery', 'software licensing', 'consulting services', 'support and maintenance'])}",
                "contract_type": choice(["Service", "License", "Vendor", "NDA", "Employment"]),
                "status": choice(statuses),
                "value": Decimal(randint(10000, 500000)) + Decimal('0.99'),
                "start_date": datetime.now().date(),
                "end_date": (datetime.now() + timedelta(days=randint(90, 730))).date(),
                "created_by": user.user_id if user else uuid.uuid4(),
                "counterparty": choice(counterparties),
                "tenant_id": tenant.id if tenant else uuid.uuid4(),
                "template": template,
                "approval_required": choice([True, False]),
                "current_approvers": [],
                "form_inputs": {
                    "payment_terms": f"Net {choice([15, 30, 45, 60])} days",
                    "renewal_term": choice(["auto", "manual", "none"])
                },
                "metadata": {
                    "renewal_date": (datetime.now() + timedelta(days=randint(90, 180))).isoformat(),
                    "negotiation_status": choice(["open", "in_progress", "closed"])
                }
            }
            
            contract, created = Contract.objects.get_or_create(
                title=contract_data["title"],
                tenant_id=contract_data["tenant_id"],
                status=contract_data["status"],
                defaults=contract_data
            )
            
            if created:
                created_contracts.append(contract)
                print(f"  ✓ Created contract: {contract.title} (${contract.value})")
            else:
                created_contracts.append(contract)
                print(f"  • Contract already exists: {contract.title}")
        except Exception as e:
            print(f"  ✗ Error creating contract: {str(e)}")
    
    return created_contracts

def create_audit_logs(users, contracts, tenants):
    """Create audit log entries for tracking"""
    print("\n📋 Creating Audit Logs...")
    
    actions = ["create", "update", "delete", "view"]
    entity_types = ["Contract", "User", "Tenant", "Approval"]
    
    created_logs = []
    
    for i in range(20):
        try:
            user = choice(users) if users else None
            contract = choice(contracts) if contracts else None
            tenant = choice(tenants) if tenants else None
            
            log_data = {
                "user_id": user.user_id if user else uuid.uuid4(),
                "entity_type": choice(entity_types),
                "entity_id": contract.id if contract else uuid.uuid4(),
                "action": choice(actions),
                "tenant_id": tenant.id if tenant else uuid.uuid4(),
                "changes": {
                    "field": choice(["status", "value", "assignee"]),
                    "old_value": choice(["draft", "pending", "active"]),
                    "new_value": choice(["pending", "active", "completed"])
                },
                "ip_address": f"192.168.1.{randint(1, 254)}"
            }
            
            log, created = AuditLogModel.objects.get_or_create(
                user_id=log_data["user_id"],
                action=log_data["action"],
                entity_type=log_data["entity_type"],
                entity_id=log_data["entity_id"],
                defaults=log_data
            )
            
            if created:
                created_logs.append(log)
                print(f"  ✓ Created audit log: {log.action}")
            else:
                created_logs.append(log)
                print(f"  • Audit log already exists")
        except Exception as e:
            print(f"  ✗ Error creating audit log: {str(e)}")
    
    return created_logs

def print_summary(tenants, users, contracts, templates, logs):
    """Print summary of created data"""
    print("\n" + "="*80)
    print("✅ DATABASE SEEDING COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"  • Tenants created: {len(tenants)}")
    print(f"  • Users created: {len(users)}")
    print(f"  • Templates created: {len(templates)}")
    print(f"  • Contracts created: {len(contracts)}")
    print(f"  • Audit logs created: {len(logs)}")
    
    print(f"\n🔐 Test Credentials:")
    print(f"  Email: admin@clm.local")
    print(f"  Password: admin123")
    
    print(f"\n📍 Access Dashboard:")
    print(f"  Dashboard: http://localhost:8000/api/admin/dashboard/")
    print(f"  Users List: http://localhost:8000/api/admin/users/")
    print(f"  Contracts List: http://localhost:8000/api/contracts/")
    
    print("\n🔐 Get Auth Token:")
    print("  curl -X POST http://localhost:8000/api/auth/login/ \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"email\": \"admin@clm.local\", \"password\": \"admin123\"}'")
    
    print("\n" + "="*80)

def main():
    """Main seeding function"""
    print("\n" + "="*80)
    print("CLM BACKEND - DATABASE SEEDING (CORRECTED VERSION)")
    print("="*80)
    
    try:
        # Create all data
        tenants = create_tenants()
        users = create_users(tenants)
        templates = create_templates(tenants, users)
        contracts = create_contracts(users, tenants, templates)
        logs = create_audit_logs(users, contracts, tenants)
        
        # Print summary
        print_summary(tenants, users, contracts, templates, logs)
        
    except Exception as e:
        print(f"\n❌ Fatal error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
