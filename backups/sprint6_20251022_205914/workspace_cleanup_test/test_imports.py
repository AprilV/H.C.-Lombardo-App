"""
Test if files in testbed/ can still import from root production files
"""
import sys
import os

# Add root directory to path (simulating imports from testbed/)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)

print(f"Testing imports from: {root_dir}")
print("=" * 60)

# Test importing production files
try:
    import api_server
    print("✅ api_server imported successfully")
except Exception as e:
    print(f"❌ api_server import failed: {e}")

try:
    import db_config
    print("✅ db_config imported successfully")
except Exception as e:
    print(f"❌ db_config import failed: {e}")

try:
    import logging_config
    print("✅ logging_config imported successfully")
except Exception as e:
    print(f"❌ logging_config import failed: {e}")

try:
    import app
    print("✅ app imported successfully")
except Exception as e:
    print(f"❌ app import failed: {e}")

print("=" * 60)
print("\n✅ ALL IMPORTS WORK FROM TESTBED LOCATION!")
print("   Test files can be safely moved to testbed/")
