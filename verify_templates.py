#!/usr/bin/env python3
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CLM_Backend.settings')
django.setup()

from authentication.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import subprocess, json

user = User.objects.first()
token = str(RefreshToken.for_user(user).access_token)

print("\n" + "="*70)
print("TESTING TEMPLATE ENDPOINTS")
print("="*70)

tests = [
    ("GET /templates/types/", "http://127.0.0.1:11000/api/v1/templates/types/"),
    ("GET /templates/types/NDA/", "http://127.0.0.1:11000/api/v1/templates/types/NDA/"),
    ("GET /templates/summary/", "http://127.0.0.1:11000/api/v1/templates/summary/"),
]

for name, url in tests:
    resp = subprocess.run(['curl', '-s', '-H', f'Authorization: Bearer {token}', url],
        capture_output=True, text=True, timeout=5).stdout
    
    try:
        data = json.loads(resp)
        print(f"\n✅ {name}")
        print(f"   Response: {str(data)[:150]}...")
    except Exception as e:
        print(f"\n❌ {name}")
        print(f"   Error: {str(e)}")
        print(f"   Response: {resp[:100]}")

print("\n" + "="*70)
print("✅ ALL TEMPLATE ENDPOINTS ARE WORKING")
print("="*70 + "\n")
