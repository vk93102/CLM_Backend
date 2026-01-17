"""
Comprehensive Database Seeding Script
Creates users, contracts, templates, approvals, and audit logs
with realistic test data
"""

import os
import django
import uuid
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import TenantModel
from contracts.models import Contract, ContractTemplate, Clause
from approvals.models import ApprovalModel
from audit_logs.models import AuditLogModel

User = get_user_model()

def create_users():
    """Create users including the specified email"""
    print("\n" + "="*80)
    print("CREATING USERS")
    print("="*80 + "\n")
    
    users_data = [
        {
            'email': 'rahuljha996886@gmail.com',
            'first_name': 'Rahul',
            'last_name': 'Jha',
            'password': 'Rahuljha@123',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'email': 'admin@clm.local',
            'first_name': 'Admin',
            'last_name': 'User',
            'password': 'admin123',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'email': 'john.doe@clm.local',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'user123',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'email': 'jane.smith@clm.local',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password': 'user123',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'email': 'michael.johnson@clm.local',
            'first_name': 'Michael',
            'last_name': 'Johnson',
            'password': 'user123',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'email': 'sarah.williams@clm.local',
            'first_name': 'Sarah',
            'last_name': 'Williams',
            'password': 'user123',
            'is_staff': False,
            'is_superuser': False,
        },
    ]
    
    created_users = []
    for user_data in users_data:
        password = user_data.pop('password')
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'user_id': uuid.uuid4(),
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser'],
                'is_active': True,
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            print(f"✓ Created: {user.email} (ID: {user.user_id})")
        else:
            print(f"ℹ Exists: {user.email}")
        
        created_users.append(user)
    
    return created_users


def create_tenants():
    """Create tenant organizations"""
    print("\n" + "="*80)
    print("CREATING TENANTS")
    print("="*80 + "\n")
    
    tenants_data = [
        {'name': 'Acme Corporation', 'domain': 'acme.clm.local'},
        {'name': 'TechStart Inc', 'domain': 'techstart.clm.local'},
        {'name': 'Global Services Ltd', 'domain': 'globalservices.clm.local'},
        {'name': 'Innovation Labs', 'domain': 'innovationlabs.clm.local'},
    ]
    
    created_tenants = []
    for tenant_data in tenants_data:
        tenant, created = TenantModel.objects.get_or_create(
            name=tenant_data['name'],
            defaults={
                'domain': tenant_data['domain'],
                'status': 'active',
                'subscription_plan': 'enterprise',
                'metadata': {
                    'industry': 'Technology',
                    'country': 'USA',
                    'employees': 100
                }
            }
        )
        
        if created:
            print(f"✓ Created: {tenant.name} (ID: {tenant.id})")
        else:
            print(f"ℹ Exists: {tenant.name}")
        
        created_tenants.append(tenant)
    
    return created_tenants


def create_contracts(users, tenants):
    """Create contracts with various statuses"""
    print("\n" + "="*80)
    print("CREATING CONTRACTS")
    print("="*80 + "\n")
    
    contract_templates = [
        {
            'title': 'Service Agreement - Enterprise',
            'description': 'Comprehensive service agreement for enterprise clients with SLA provisions',
            'contract_value': 150000,
            'status': 'active',
            'contract_type': 'service',
        },
        {
            'title': 'Software License Agreement',
            'description': 'Software licensing terms and conditions for commercial use',
            'contract_value': 75000,
            'status': 'active',
            'contract_type': 'license',
        },
        {
            'title': 'Vendor Supply Agreement',
            'description': 'Long-term supply agreement with tiered pricing',
            'contract_value': 250000,
            'status': 'active',
            'contract_type': 'vendor',
        },
        {
            'title': 'Maintenance & Support Contract',
            'description': '12-month maintenance and technical support agreement',
            'contract_value': 50000,
            'status': 'active',
            'contract_type': 'maintenance',
        },
        {
            'title': 'NDA - Confidential Partnership',
            'description': 'Non-disclosure agreement for partnership discussions',
            'contract_value': 0,
            'status': 'pending_approval',
            'contract_type': 'nda',
        },
        {
            'title': 'Consulting Services Agreement',
            'description': 'Professional consulting services for digital transformation',
            'contract_value': 120000,
            'status': 'under_review',
            'contract_type': 'consulting',
        },
        {
            'title': 'Employment Contract',
            'description': 'Executive employment agreement with benefits package',
            'contract_value': 180000,
            'status': 'active',
            'contract_type': 'employment',
        },
        {
            'title': 'Insurance Policy Agreement',
            'description': 'Commercial insurance policy and coverage details',
            'contract_value': 45000,
            'status': 'active',
            'contract_type': 'insurance',
        },
        {
            'title': 'Data Processing Agreement',
            'description': 'GDPR compliant data processing agreement',
            'contract_value': 25000,
            'status': 'pending_approval',
            'contract_type': 'data_processing',
        },
        {
            'title': 'Partnership Agreement',
            'description': 'Strategic partnership with revenue sharing terms',
            'contract_value': 300000,
            'status': 'completed',
            'contract_type': 'partnership',
        },
    ]
    
    created_contracts = []
    for contract_data in contract_templates:
        contract, created = Contract.objects.get_or_create(
            title=contract_data['title'],
            defaults={
                'id': uuid.uuid4(),
                'description': contract_data['description'],
                'contract_value': contract_data['contract_value'],
                'status': contract_data['status'],
                'contract_type': contract_data.get('contract_type', 'service'),
                'created_by': random.choice(users).user_id,
                'tenant_id': random.choice(tenants).tenant_id,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 90)),
                'updated_at': datetime.now(),
            }
        )
        
        if created:
            print(f"✓ Created: {contract.title} (Status: {contract.status}, Value: ${contract.contract_value})")
        else:
            print(f"ℹ Exists: {contract.title}")
        
        created_contracts.append(contract)
    
    return created_contracts


def create_approval_workflows(contracts, users):
    """Create approval workflows for contracts"""
    print("\n" + "="*80)
    print("CREATING APPROVAL WORKFLOWS")
    print("="*80 + "\n")
    
    approval_statuses = ['pending', 'approved', 'rejected']
    approvers = [u for u in users if u.is_staff]
    
    for contract in contracts[:6]:  # Create approvals for first 6 contracts
        try:
            approval, created = ApprovalModel.objects.get_or_create(
                entity_id=contract.id,
                entity_type='contract',
                defaults={
                    'id': uuid.uuid4(),
                    'status': random.choice(approval_statuses),
                    'requester_id': contract.created_by,
                    'approver_id': random.choice(approvers).user_id,
                    'tenant_id': contract.tenant_id,
                    'created_at': contract.created_at,
                    'comment': f'Approval required for {contract.title}',
                }
            )
            
            if created:
                print(f"✓ Approval created for: {contract.title} (Status: {approval.status})")
            else:
                print(f"ℹ Approval exists for: {contract.title}")
        except Exception as e:
            print(f"✗ Error creating approval for {contract.title}: {str(e)}")


def create_audit_logs(users):
    """Create audit log entries"""
    print("\n" + "="*80)
    print("CREATING AUDIT LOGS")
    print("="*80 + "\n")
    
    actions = [
        'contract_created',
        'contract_updated',
        'contract_approved',
        'user_login',
        'template_created',
        'approval_requested',
    ]
    
    for i in range(20):
        try:
            audit_log, created = AuditLogModel.objects.get_or_create(
                user_id=random.choice(users).user_id,
                entity_type=random.choice(['contract', 'template', 'approval', 'user']),
                action=random.choice(actions),
                defaults={
                    'id': uuid.uuid4(),
                    'details': f'Action performed on entity',
                    'created_at': datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                }
            )
            
            if created and i < 5:
                print(f"✓ Audit log entry created: {audit_log.action}")
        except Exception as e:
            pass
    
    print(f"✓ Created audit log entries")


def print_credentials(users):
    """Print login credentials"""
    print("\n" + "="*80)
    print("LOGIN CREDENTIALS")
    print("="*80 + "\n")
    
    # Find the main user
    main_user = User.objects.filter(email='rahuljha996886@gmail.com').first()
    if main_user:
        print(f"PRIMARY USER:")
        print(f"  Email: rahuljha996886@gmail.com")
        print(f"  Password: Rahuljha@123")
        print(f"  User ID: {main_user.user_id}")
        print(f"  Role: Admin\n")
    
    print(f"OTHER ADMIN USERS:")
    for user in User.objects.filter(is_staff=True).exclude(email='rahuljha996886@gmail.com'):
        print(f"  Email: {user.email}")
        print(f"  User ID: {user.user_id}\n")
    
    print(f"STANDARD USERS:")
    for user in User.objects.filter(is_staff=False)[:3]:
        print(f"  Email: {user.email}")
        print(f"  User ID: {user.user_id}\n")


def main():
    """Execute all seeding operations"""
    print("\n" + "="*80)
    print("DATABASE SEEDING - COMPREHENSIVE DATA POPULATION")
    print("="*80)
    
    try:
        users = create_users()
        tenants = create_tenants()
        contracts = create_contracts(users, tenants)
        create_approval_workflows(contracts, users)
        create_audit_logs(users)
        
        print_credentials(users)
        
        print("\n" + "="*80)
        print("✓ DATABASE SEEDING COMPLETED SUCCESSFULLY")
        print("="*80 + "\n")
        
        print("SUMMARY:")
        print(f"  Users: {User.objects.count()}")
        print(f"  Tenants: {TenantModel.objects.count()}")
        print(f"  Contracts: {Contract.objects.count()}")
        print(f"  Approvals: {ApprovalModel.objects.count()}")
        print(f"  Audit Logs: {AuditLogModel.objects.count()}")
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
