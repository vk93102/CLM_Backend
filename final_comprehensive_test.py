#!/usr/bin/env python
"""
Final comprehensive test with timeout handling
"""
import subprocess
import sys
import time

# Run test with subprocess
print("Starting comprehensive contract test...")
print("=" * 70)

try:
    result = subprocess.run(
        [sys.executable, "test_comprehensive_contract.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd="/Users/vishaljha/CLM_Backend"
    )
    
    # Print only important sections
    lines = result.stdout.split('\n')
    
    # Find and print metadata section
    in_metadata = False
    in_validation = False
    
    for i, line in enumerate(lines):
        if "EXTRACTED METADATA" in line:
            in_metadata = True
            in_validation = False
        elif "VALIDATION" in line:
            in_metadata = False
            in_validation = True
        elif "TEST COMPLETED" in line:
            in_validation = False
        
        if in_metadata or in_validation:
            print(line)
        elif "Parties" in line or "Contract Value" in line or "Dates" in line:
            print(line)
    
    if result.returncode != 0:
        print(f"\n✗ Test failed with code {result.returncode}")
        if result.stderr:
            print("STDERR:", result.stderr[-500:])
    else:
        print("\n✓ Test completed successfully")

except subprocess.TimeoutExpired:
    print("✗ Test timed out after 120 seconds")
except Exception as e:
    print(f"✗ Error: {e}")
