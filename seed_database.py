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
            "description": "Leading manufacturing company"
        },
        {
            "name": "TechStart Inc",
            "description": "Software development and IT services"
        },
        {
            "name": "Global Services Ltd",
            "description": "Consulting and professional services"
        },
        {
            "name": "Enterprise Solutions",
            "description": "Enterprise resource planning solutions"
        }
    ]
    
    tenants = []
    for tenant_data in tenants_data:
        tenant, created = TenantModel.objects.get_or_create(
            name=tenant_data['name'],
            defaults={
                'tenant_id': uuid.uuid4(),
                'description': tenant_data['description']
            }
        )
        tenants.append(tenant)
        status = "✓ Created" if created else "ℹ Exists"
        print(f"  {status}: {tenant.name}")
    
    return tenants

def create_users():
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
            "password": "admin123"
        },
        {
            "email": "manager@clm.local",
            "username": "john.manager",
            "first_name": "John",
            "last_name": "Manager",
            "is_staff": True,
            "is_superuser": False,
            "password": "manager123"
        },
        {
            "email": "approver@clm.local",
            "username": "jane.approver",
            "first_name": "Jane",
            "last_name": "Approver",
            "is_staff": False,
            "is_superuser": False,
            "password": "approver123"
        },
        {
            "email": "vendor@clm.local",
            "username": "bob.vendor",
            "first_name": "Bob",
            "last_name": "Vendor",
            "is_staff": False,
            "is_superuser": False,
            "password": "vendor123"
        },
        {
            "email": "analyst@clm.local",
            "username": "sarah.analyst",
            "first_name": "Sarah",
            "last_name": "Analyst",
            "is_staff": False,
            "is_superuser": False,
            "password": "analyst123"
        }
    ]
    
    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'user_id': uuid.uuid4(),
                'username': user_data['username'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser'],
                'is_active': True
            }
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
        
        users.append(user)
        status = "✓ Created" if created else "ℹ Exists"
        print(f"  {status}: {user.email} ({user.username})")
    
    return users

def create_contracts(users, tenants):
    """Create sample contracts with realistic data"""
    print("\n📄 Creating Contracts...")
    
    statuses = ['draft', 'pending_approval', 'active', 'completed', 'archived']
    contract_types = ['service_agreement', 'vendor_agreement', 'nda', 'license', 'partnership']
    
    contracts_data = [
        {
            "title": "Enterprise Software License Agreement",
            "description": "12-month software license for enterprise deployment with 24/7 support",
            "contract_type": "license",
            "status": "active",
            "contract_value": Decimal("250000.00"),
            "start_date": datetime.now() - timedelta(days=180),
            "end_date": datetime.now() + timedelta(days=180),
            "created_by_idx": 0,
            "tenant_idx": 0,
            "renewal_date": datetime.now() + timedelta(days=150)
        },
        {
            "title": "Vendor Service Agreement - Cloud Infrastructure",
            "description": "Cloud hosting services including compute, storage, and networking",
            "contract_type": "service_agreement",
            "status": "active",
            "contract_value": Decimal("150000.00"),
            "start_date": datetime.now() - timedelta(days=90),
            "end_date": datetime.now() + timedelta(days=270),
            "created_by_idx": 1,
            "tenant_idx": 1,
            "renewal_date": datetime.now() + timedelta(days=250)
        },
        {
            "title": "Mutual Non-Disclosure Agreement",
            "description": "NDA between Acme Corp and Tech Partner for joint venture discussions",
            "contract_type": "nda",
            "status": "active",
            "contract_value": Decimal("0.00"),
            "start_date": datetime.now() - timedelta(days=60),
            "end_date": datetime.now() + timedelta(days=300),
            "created_by_idx": 2,
            "tenant_idx": 0,
            "renewal_date": None
        },
        {
            "title": "Marketing Services Agreement",
            "description": "Digital marketing and brand management services for 12 months",
            "contract_type": "service_agreement",
            "status": "pending_approval",
            "contract_value": Decimal("75000.00"),
            "start_date": datetime.now() + timedelta(days=30),
            "end_date": datetime.now() + timedelta(days=395),
            "created_by_idx": 1,
            "tenant_idx": 2,
            "renewal_date": datetime.now() + timedelta(days=365)
        },
        {
            "title": "Vendor Partnership Agreement",
            "description": "Long-term partnership for supply chain management and logistics",
            "contract_type": "partnership",
            "status": "active",
            "contract_value": Decimal("500000.00"),
            "start_date": datetime.now() - timedelta(days=120),
            "end_date": datetime.now() + timedelta(days=240),
            "created_by_idx": 0,
            "tenant_idx": 1,
            "renewal_date": datetime.now() + timedelta(days=220)
        },
        {
            "title": "Consulting Services - Digital Transformation",
            "description": "Management consulting for enterprise digital transformation initiative",
            "contract_type": "service_agreement",
            "status": "active",
            "contract_value": Decimal("350000.00"),
            "start_date": datetime.now() - timedelta(days=30),
            "end_date": datetime.now() + timedelta(days=330),
            "created_by_idx": 2,
            "tenant_idx": 3,
            "renewal_date": None
        },
        {
            "title": "Hardware Maintenance Agreement",
            "description": "24-month warranty and maintenance for enterprise hardware systems",
            "contract_type": "service_agreement",
            "status": "draft",
            "contract_value": Decimal("45000.00"),
            "start_date": datetime.now() + timedelta(days=15),
            "end_date": datetime.now() + timedelta(days=745),
            "created_by_idx": 1,
            "tenant_idx": 0,
            "renewal_date": datetime.now() + timedelta(days=720)
        },
        {
            "title": "Employee Training Program Agreement",
            "description": "Comprehensive training program for 500+ employees covering various IT skills",
            "contract_type": "service_agreement",
            "status": "pending_approval",
            "contract_value": Decimal("125000.00"),
            "start_date": datetime.now() + timedelta(days=45),
            "end_date": datetime.now() + timedelta(days=405),
            "created_by_idx": 2,
            "tenant_idx": 2,
            "renewal_date": None
        },
        {
            "title": "Professional Liability Insurance",
            "description": "Annual professional liability and E&O insurance policy",
            "contract_type": "license",
            "status": "active",
            "contract_value": Decimal("65000.00"),
            "start_date": datetime.now() - timedelta(days=150),
            "end_date": datetime.now() + timedelta(days=215),
            "created_by_idx": 0,
            "tenant_idx": 3,
            "renewal_date": datetime.now() + timedelta(days=200)
        },
        {
            "title": "Data Processing Agreement (GDPR Compliant)",
            "description": "GDPR-compliant data processing agreement with subprocessors disclosure",
            "contract_type": "vendor_agreement",
            "status": "active",
            "contract_value": Decimal("35000.00"),
            "start_date": datetime.now() - timedelta(days=200),
            "end_date": datetime.now() + timedelta(days=160),
            "created_by_idx": 1,
            "tenant_idx": 1,
            "renewal_date": datetime.now() + timedelta(days=140)
        }
    ]
    
    contracts = []
    for contract_data in contracts_data:
        contract_id = uuid.uuid4()
        try:
            contract, created = Contract.objects.get_or_create(
                title=contract_data['title'],
                defaults={
                    'id': contract_id,
                    'description': contract_data['description'],
                    'contract_type': contract_data['contract_type'],
                    'status': contract_data['status'],
                    'contract_value': contract_data['contract_value'],
                    'start_date': contract_data['start_date'],
                    'end_date': contract_data['end_date'],
                    'renewal_date': contract_data.get('renewal_date'),
                    'created_by': users[contract_data['created_by_idx']].user_id,
                    'tenant_id': tenants[contract_data['tenant_idx']].tenant_id,
                    'created_at': datetime.now() - timedelta(hours=24),
                    'updated_at': datetime.now()
                }
            )
            contracts.append(contract)
            status = "✓ Created" if created else "ℹ Exists"
            print(f"  {status}: {contract.title} (${contract.contract_value})")
        except Exception as e:
            print(f"  ✗ Error creating contract: {str(e)}")
    
    return contracts

def create_audit_logs(users, contracts):
    """Create sample audit logs"""
    print("\n📋 Creating Audit Logs...")
    
    audit_events = [
        {
            "entity_type": "contract",
            "action": "created",
            "description": "Contract created"
        },
        {
            "entity_type": "contract",
            "action": "updated",
            "description": "Contract status updated"
        },
        {
            "entity_type": "contract",
            "action": "viewed",
            "description": "Contract viewed by user"
        },
        {
            "entity_type": "approval",
            "action": "submitted",
            "description": "Approval request submitted"
        },
        {
            "entity_type": "approval",
            "action": "approved",
            "description": "Approval request approved"
        }
    ]
    
    logs = []
    for i in range(20):
        event = audit_events[i % len(audit_events)]
        user = users[i % len(users)]
        contract = contracts[i % len(contracts)] if contracts else None
        
        try:
            log, created = AuditLogModel.objects.get_or_create(
                id=uuid.uuid4(),
                defaults={
                    'user_id': user.user_id,
                    'entity_type': event['entity_type'],
                    'entity_id': str(contract.id) if contract else str(uuid.uuid4()),
                    'action': event['action'],
                    'description': event['description'],
                    'old_values': {},
                    'new_values': {},
                    'created_at': datetime.now() - timedelta(hours=i*2),
                    'updated_at': datetime.now() - timedelta(hours=i*2)
                }
            )
            logs.append(log)
        except Exception as e:
            pass
    
    print(f"  ✓ Created {len(logs)} audit log entries")
    return logs

def print_summary(users, tenants, contracts):
    """Print summary of created data"""
    print("\n" + "="*80)
    print("DATABASE SEEDING SUMMARY")
    print("="*80 + "\n")
    
    print("✓ USERS CREATED:")
    for user in users:
        role = "Admin" if user.is_staff else "User"
        print(f"  • {user.email} ({role})")
    
    print(f"\n✓ TENANTS CREATED:")
    for tenant in tenants:
        contract_count = Contract.objects.filter(tenant_id=tenant.tenant_id).count()
        print(f"  • {tenant.name} ({contract_count} contracts)")
    
    print(f"\n✓ CONTRACTS CREATED:")
    statuses = {}
    for contract in contracts:
        status = contract.status
        statuses[status] = statuses.get(status, 0) + 1
        print(f"  • {contract.title}")
        print(f"    Status: {contract.status} | Value: ${contract.contract_value:,.2f}")
    
    print(f"\n✓ SUMMARY:")
    print(f"  Total Users: {len(users)}")
    print(f"  Total Tenants: {len(tenants)}")
    print(f"  Total Contracts: {len(contracts)}")
    print(f"  Contract Status Breakdown:")
    for status, count in sorted(statuses.items()):
        print(f"    - {status}: {count}")
    
    print("\n" + "="*80)
    print("✓ DATABASE SEEDING COMPLETE")
    print("="*80 + "\n")

def main():
    """Run database seeding"""
    print("\n" + "="*80)
    print("CLM BACKEND - DATABASE SEEDING")
    print("="*80)
    
    try:
        # Create data
        tenants = create_tenants()
        users = create_users()
        contracts = create_contracts(users, tenants)
        logs = create_audit_logs(users, contracts)
        
        # Print summary
        print_summary(users, tenants, contracts)
        
        print("\n💡 TEST CREDENTIALS:")
        print("  Email: admin@clm.local")
        print("  Password: admin123")
        print("\n  Email: manager@clm.local")
        print("  Password: manager123")
        
        print("\n🌐 TEST ENDPOINTS:")
        print("  Health: http://localhost:8000/api/health/")
        print("  Users: http://localhost:8000/api/users/")
        print("  Roles: http://localhost:8000/api/roles/")
        print("  Permissions: http://localhost:8000/api/permissions/")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
