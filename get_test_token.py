import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from tenants.models import TenantModel

User = get_user_model()

# Create or get tenant
tenant, _ = TenantModel.objects.get_or_create(
    name='Template Test Tenant',
    defaults={'status': 'active'}
)

# Create or get user
user, created = User.objects.get_or_create(
    email='template_test@example.com',
    defaults={
        'first_name': 'Template',
        'last_name': 'Tester',
        'is_active': True,
        'tenant_id': tenant.id
    }
)

if created:
    user.set_password('TemplateTest123!')
    user.save()

# Add to tenant - user.tenant_id already set above
# Just get or create token

# Get token
token, _ = Token.objects.get_or_create(user=user)

print(f'TOKEN={token.key}')
print(f'USER_ID={user.id}')
print(f'TENANT_ID={tenant.id}')
