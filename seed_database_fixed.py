"""
Comprehensive Database Seeding Script
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
from contracts.models import Contract
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
            "username": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "is_staff": True,
            "is_superuser": True,
            "password": "admin123",
            "tenant": tenants[0] if tenants else None
        },
        {
            "email": "manager@clm.local",
            "username": "john.manager",
            "first_name": "John",
            "last_name": "Manager",
            "is_staff": True,
            "is_superuser": False,
            "password": "manager123",
            "tenant": tenants[0] if tenants else None
        },
        {
            "email": "approver@clm.local",
            "username": "jane.approver",
            "first_name": "Jane",
            "last_name": "Approver",
            "is_staff": False,
            "is_superuser": False,
            "password": "approver123",
            "tenant": tenants[1] if len(tenants) > 1 else tenants[0]
        },
        {
            "email": "vendor@clm.local",
            "username": "bob.vendor",
            "first_name": "Bob",
            "last_name": "Vendor",
            "is_staff": False,
            "is_superuser": False,
            "password": "vendor123",
            "tenant": tenants[1] if len(tenants) > 1 else tenants[0]
        },
        {
            "email": "analyst@clm.local",
            "username": "alice.analyst",
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
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults=user_data
            )
            
            if created:
                user.set_password(user_data["password"])
                if tenant:
                    user.tenant = tenant
                user.save()
                created_users.append(user)
                print(f"  ✓ Created user: {user.email}")
            else:
                created_users.append(user)
                print(f"  • User already exists: {user.email}")
        except Exception as e:
            print(f"  ✗ Error creating user: {str(e)}")
    
    return created_users

def create_contracts(users, tenants):
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
    
    statuses = ["draft", "pending_review", "active", "completed", "terminated"]
    
    created_contracts = []
    
    for i in range(10):
        try:
            contract_data = {
                "title": contract_titles[i % len(contract_titles)],
                "description": f"Contract for {choice(['service delivery', 'software licensing', 'consulting services', 'support and maintenance'])}",
                "contract_type": choice(["Service", "License", "Vendor", "NDA", "Employment"]),
                "status": choice(statuses),
                "contract_value": Decimal(randint(10000, 500000)) + Decimal('0.99'),
                "currency": "USD",
                "start_date": datetime.now().date(),
                "end_date": (datetime.now() + timedelta(days=randint(90, 730))).date(),
                "created_by": users[0] if users else None,
                "assigned_to": choice(users) if users else None,
                "tenant": choice(tenants) if tenants else None,
                "metadata": {
                    "renewal_term": choice(["auto", "manual", "none"]),
                    "payment_terms": f"Net {choice([15, 30, 45, 60])}",
                    "renewal_date": (datetime.now() + timedelta(days=randint(90, 180))).isoformat()
                }
            }
            
            contract, created = Contract.objects.get_or_create(
                title=contract_data["title"],
                status=contract_data["status"],
                defaults=contract_data
            )
            
            if created:
                created_contracts.append(contract)
                print(f"  ✓ Created contract: {contract.title} (${contract.contract_value})")
            else:
                created_contracts.append(contract)
                print(f"  • Contract already exists: {contract.title}")
        except Exception as e:
            print(f"  ✗ Error creating contract: {str(e)}")
    
    return created_contracts

def create_audit_logs(users, contracts):
    """Create audit log entries for tracking"""
    print("\n📋 Creating Audit Logs...")
    
    actions = [
        "contract_created",
        "contract_updated",
        "contract_reviewed",
        "contract_approved",
        "contract_signed",
        "user_login",
        "user_created",
        "user_updated",
        "permission_changed"
    ]
    
    statuses = ["success", "pending", "failed"]
    
    created_logs = []
    
    for i in range(20):
        try:
            log_data = {
                "user": choice(users) if users else None,
                "entity_type": choice(["Contract", "User", "Tenant", "Approval"]),
                "entity_id": str(choice(contracts).id) if contracts else str(uuid.uuid4()),
                "action": choice(actions),
                "status": choice(statuses),
                "changes": {
                    "field": choice(["status", "value", "assignee"]),
                    "old_value": choice(["draft", "pending", "active"]),
                    "new_value": choice(["pending", "active", "completed"])
                },
                "ip_address": f"192.168.1.{randint(1, 254)}",
                "metadata": {
                    "user_agent": "Mozilla/5.0",
                    "referer": "http://localhost:8000"
                }
            }
            
            log, created = AuditLogModel.objects.get_or_create(
                user=log_data["user"],
                action=log_data["action"],
                entity_type=log_data["entity_type"],
                defaults=log_data
            )
            
            if created:
                created_logs.append(log)
                print(f"  ✓ Created audit log: {log.action}")
            else:
                created_logs.append(log)
                print(f"  • Audit log already exists: {log.action}")
        except Exception as e:
            print(f"  ✗ Error creating audit log: {str(e)}")
    
    return created_logs

def print_summary(tenants, users, contracts, logs):
    """Print summary of created data"""
    print("\n" + "="*80)
    print("✅ DATABASE SEEDING COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"  • Tenants created: {len(tenants)}")
    print(f"  • Users created: {len(users)}")
    print(f"  • Contracts created: {len(contracts)}")
    print(f"  • Audit logs created: {len(logs)}")
    
    print(f"\n🔐 Test Credentials:")
    print(f"  Email: admin@clm.local")
    print(f"  Password: admin123")
    
    print(f"\n📍 Access:")
    print(f"  Dashboard: http://localhost:8000/api/admin/dashboard/")
    print(f"  Users List: http://localhost:8000/api/admin/users/")
    print(f"  Contracts List: http://localhost:8000/api/contracts/")
    
    print("\n" + "="*80)

def main():
    """Main seeding function"""
    print("\n" + "="*80)
    print("CLM BACKEND - DATABASE SEEDING")
    print("="*80)
    
    try:
        # Create all data
        tenants = create_tenants()
        users = create_users(tenants)
        contracts = create_contracts(users, tenants)
        logs = create_audit_logs(users, contracts)
        
        # Print summary
        print_summary(tenants, users, contracts, logs)
        
    except Exception as e:
        print(f"\n❌ Fatal error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
