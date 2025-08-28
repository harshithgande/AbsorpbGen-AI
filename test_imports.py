#!/usr/bin/env python3
"""
Simple test script to verify imports work
"""

print("Testing imports...")

try:
    print("1. Testing Flask import...")
    from flask import Flask
    print("   ✅ Flask imported successfully")
except Exception as e:
    print(f"   ❌ Flask import failed: {e}")

try:
    print("2. Testing openai_client import...")
    from openai_client import get_llm_dose
    print("   ✅ openai_client imported successfully")
except Exception as e:
    print(f"   ❌ openai_client import failed: {e}")

try:
    print("3. Testing validators import...")
    from validators import UserRequest, AITriage, APIError
    print("   ✅ validators imported successfully")
except Exception as e:
    print(f"   ❌ validators import failed: {e}")

try:
    print("4. Testing safety import...")
    from safety import has_red_flag
    print("   ✅ safety imported successfully")
except Exception as e:
    print(f"   ❌ safety import failed: {e}")

try:
    print("5. Testing dosing_rules import...")
    from dosing_rules import compute_conservative_dose
    print("   ✅ dosing_rules imported successfully")
except Exception as e:
    print(f"   ❌ dosing_rules import failed: {e}")

print("\nAll import tests completed!") 