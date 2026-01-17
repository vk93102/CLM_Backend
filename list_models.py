#!/usr/bin/env python
"""
List available Gemini models
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')

import django
django.setup()

from django.conf import settings

import google.generativeai as genai
genai.configure(api_key=settings.GEMINI_API_KEY)

models = genai.list_models()
print("Available models:")
for model in models:
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")
