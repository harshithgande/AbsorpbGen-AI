#!/usr/bin/env python3
"""
Debug script to test app step by step
"""

print("Step 1: Testing basic Python...")
print("✅ Basic Python works")

print("\nStep 2: Testing imports...")
try:
    import flask
    print("✅ Flask imported")
except Exception as e:
    print(f"❌ Flask import failed: {e}")

try:
    from openai_client import get_ai_pharmacist_recommendation
    print("✅ OpenAI client imported")
except Exception as e:
    print(f"❌ OpenAI client import failed: {e}")

print("\nStep 3: Testing app compilation...")
try:
    with open('app_simple.py', 'r') as f:
        code = f.read()
    compile(code, 'app_simple.py', 'exec')
    print("✅ App compiles successfully")
except Exception as e:
    print(f"❌ App compilation failed: {e}")

print("\nDebug complete!") 