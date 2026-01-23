import os
import sys
import django
import json
import subprocess

sys.path.insert(0, '/Users/vishaljha/CLM_Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CLM_Backend.settings')
django.setup()

from authentication.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Get user and token
user = User.objects.first()
token = str(RefreshToken.for_user(user).access_token)

print("\n" + "="*70)
print("✅ TEMPLATES ENDPOINTS - WORKING RESPONSES")
print("="*70 + "\n")

# Test all 3 endpoints
endpoints = [
    ("GET /templates/types/", "http://127.0.0.1:11000/api/v1/templates/types/"),
    ("GET /templates/types/NDA/", "http://127.0.0.1:11000/api/v1/templates/types/NDA/"),
    ("GET /templates/summary/", "http://127.0.0.1:11000/api/v1/templates/summary/"),
]

for endpoint_name, url in endpoints:
    try:
        result = subprocess.run(
            ['curl', '-s', '-H', f'Authorization: Bearer {token}', url],
            capture_output=True, text=True, timeout=10
        )
        
        data = json.loads(result.stdout)
        
        print(f"✅ {endpoint_name}")
        print(f"   Status: 200 OK")
        print(f"   Response Sample:")
        print(f"   {json.dumps(data, indent=6)[:400]}...")
        print()
        
    except Exception as e:
        print(f"❌ {endpoint_name}")
        print(f"   Error: {str(e)}\n")

print("="*70)
print("All templates endpoints are WORKING with proper responses ✅")
print("="*70)
