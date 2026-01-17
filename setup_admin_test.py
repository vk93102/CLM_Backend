"""
Setup test data and run comprehensive admin API tests
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
sys.path.insert(0, '/Users/vishaljha/CLM_Backend')
django.setup()

from authentication.models import User
from tenants.models import TenantModel
from contracts.models import Contract
import uuid

def create_test_data():
    """Create test users and data"""
    print("Creating test data...")
    
    # Create admin user
    admin, created = User.objects.get_or_create(
        email='admin@clm.local',
        defaults={
            'user_id': uuid.uuid4(),
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"✓ Created admin user: {admin.email}")
    else:
        print(f"ℹ Admin user already exists: {admin.email}")
    
    # Create regular user
    user, created = User.objects.get_or_create(
        email='user@clm.local',
        defaults={
            'user_id': uuid.uuid4(),
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'is_staff': False,
            'is_superuser': False,
            'is_active': True,
        }
    )
    if created:
        user.set_password('user123')
        user.save()
        print(f"✓ Created test user: {user.email}")
    else:
        print(f"ℹ Test user already exists: {user.email}")
    
    # Create tenant
    try:
        tenant, created = TenantModel.objects.get_or_create(
            name='Test Tenant',
            defaults={
                'tenant_id': uuid.uuid4(),
                'description': 'Test tenant for admin panel',
                'created_by': admin.user_id,
            }
        )
        if created:
            print(f"✓ Created tenant: {tenant.name}")
        else:
            print(f"ℹ Tenant already exists: {tenant.name}")
    except Exception as e:
        print(f"Note: Could not create tenant - {str(e)}")
    
    print("\nTest data setup complete!\n")

if __name__ == "__main__":
    create_test_data()
