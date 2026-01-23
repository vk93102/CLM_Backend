"""
Script to consolidate scattered files into clean individual files
"""
import shutil
from pathlib import Path

# Base directory
BASE = Path("/Users/vishaljha/CLM_Backend/contracts")

print("🔄 Starting consolidation...")

# 1. Consolidate VIEWS
print("\n📝 Consolidating views...")
view_files = [
    'generation_views.py',
    'manual_editing_views.py', 
    'r2_views.py',
    'health_views.py',
    'signnow_views.py'
]

with open(BASE / 'views_consolidated_NEW.py', 'w') as outfile:
    # Write header
    outfile.write('"""\nCLM Backend - Consolidated Views\n')
    outfile.write('All contract management endpoints in one file\n"""\n\n')
    
    # Write existing views.py first
    with open(BASE / 'views.py') as f:
        outfile.write("# ========== WEEK 1 & 2: BASIC CONTRACT CRUD ==========\n\n")
        outfile.write(f.read())
        outfile.write("\n\n")
    
    # Add other view files
    for view_file in view_files:
        filepath = BASE / view_file
        if filepath.exists():
            outfile.write(f"\n\n# ========== {view_file.replace('.py', '').upper().replace('_', ' ')} ==========\n\n")
            with open(filepath) as f:
                content = f.read()
                # Skip docstring and imports if they're duplicates
                lines = content.split('\n')
                start_idx = 0
                for i, line in enumerate(lines):
                    if 'class ' in line or 'def ' in line or '@api_view' in line:
                        start_idx = i
                        break
                outfile.write('\n'.join(lines[start_idx:]))
                outfile.write("\n")

print("✅ Views consolidated to views_consolidated_NEW.py")

# 2. Consolidate MODELS
print("\n📝 Consolidating models...")
with open(BASE / 'models_consolidated_NEW.py', 'w') as outfile:
    # Write main models.py
    with open(BASE / 'models.py') as f:
        outfile.write(f.read())
        outfile.write("\n\n")
    
    # Add manual_editing_models.py
    if (BASE / 'manual_editing_models.py').exists():
        outfile.write("\n# ========== MANUAL EDITING MODELS ==========\n\n")
        with open(BASE / 'manual_editing_models.py') as f:
            content = f.read()
            lines = content.split('\n')
            # Skip imports
            start_idx = 0
            for i, line in enumerate(lines):
                if 'class ' in line:
                    start_idx = i
                    break
            outfile.write('\n'.join(lines[start_idx:]))

print("✅ Models consolidated to models_consolidated_NEW.py")

# 3. Consolidate SERIALIZERS
print("\n📝 Consolidating serializers...")
with open(BASE / 'serializers_consolidated_NEW.py', 'w') as outfile:
    # Write main serializers.py
    with open(BASE / 'serializers.py') as f:
        outfile.write(f.read())
        outfile.write("\n\n")
    
    # Add other serializers
    for ser_file in ['manual_editing_serializers.py', 'signnow_serializers.py']:
        filepath = BASE / ser_file
        if filepath.exists():
            outfile.write(f"\n# ========== {ser_file.replace('.py', '').upper().replace('_', ' ')} ==========\n\n")
            with open(filepath) as f:
                content = f.read()
                lines = content.split('\n')
                start_idx = 0
                for i, line in enumerate(lines):
                    if 'class ' in line:
                        start_idx = i
                        break
                outfile.write('\n'.join(lines[start_idx:]))

print("✅ Serializers consolidated to serializers_consolidated_NEW.py")

# 4. Consolidate SERVICES
print("\n📝 Consolidating services...")
with open(BASE / 'services_consolidated_NEW.py', 'w') as outfile:
    # Write main services.py
    with open(BASE / 'services.py') as f:
        outfile.write(f.read())
        outfile.write("\n\n")
    
    # Add other services
    for svc_file in ['generation_service.py', 'contract_generator_service.py', 'signnow_service.py']:
        filepath = BASE / svc_file
        if filepath.exists():
            outfile.write(f"\n# ========== {svc_file.replace('.py', '').upper().replace('_', ' ')} ==========\n\n")
            with open(filepath) as f:
                content = f.read()
                lines = content.split('\n')
                start_idx = 0
                for i, line in enumerate(lines):
                    if 'class ' in line or 'def ' in line:
                        start_idx = i
                        break
                outfile.write('\n'.join(lines[start_idx:]))

print("✅ Services consolidated to services_consolidated_NEW.py")

# 5. Consolidate URLS
print("\n📝 Consolidating URLs...")
with open(BASE / 'urls_consolidated_NEW.py', 'w') as outfile:
    # Write main urls.py
    with open(BASE / 'urls.py') as f:
        content = f.read()
        # Remove the final urlpatterns close bracket
        content = content.rstrip()
        if content.endswith(']'):
            content = content[:-1]
        outfile.write(content)
        outfile.write(",\n\n")
    
    # Add other URLs
    for url_file in ['signnow_urls.py', 'urls_health.py']:
        filepath = BASE / url_file
        if filepath.exists():
            outfile.write(f"    # ========== {url_file.replace('.py', '').upper().replace('_', ' ')} ==========\n")
            with open(filepath) as f:
                content = f.read()
                # Extract path() statements
                for line in content.split('\n'):
                    if 'path(' in line:
                        outfile.write(f"    {line.strip()}\n")
    
    outfile.write("]\n")

print("✅ URLs consolidated to urls_consolidated_NEW.py")

print("\n✅ Consolidation complete!")
print("\nGenerated files:")
print("  - views_consolidated_NEW.py")
print("  - models_consolidated_NEW.py")
print("  - serializers_consolidated_NEW.py")
print("  - services_consolidated_NEW.py")
print("  - urls_consolidated_NEW.py")
print("\nReview these files, then replace the originals.")
