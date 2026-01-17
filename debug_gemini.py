#!/usr/bin/env python
"""
Debug Gemini API availability
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')

import django
django.setup()

from django.conf import settings
print(f"GEMINI_API_KEY in settings: {bool(settings.GEMINI_API_KEY)}")
print(f"GEMINI_API_KEY value: {settings.GEMINI_API_KEY[:20] if settings.GEMINI_API_KEY else 'NOT SET'}...")

# Try to import and use
try:
    import google.generativeai as genai
    print(f"✓ google.generativeai imported successfully")
    
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        print(f"✓ Gemini configured")
        
        # Try to get models
        models = genai.list_models()
        print(f"✓ Available models: {len(list(models))}")
        
        # Try simple generation
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        print(f"✓ Test generation successful: {response.text[:50]}...")
    else:
        print("✗ No Gemini API key in settings")
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
