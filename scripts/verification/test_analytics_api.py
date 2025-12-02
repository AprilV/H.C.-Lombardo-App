"""
Test HCL Analytics API Endpoints
"""

import requests
import time

BASE_URL = "http://localhost:5000"

print("Waiting for server to start...")
time.sleep(3)

print("\n" + "="*80)
print("TESTING HCL ANALYTICS ENDPOINTS")
print("="*80)

endpoints = [
    "/api/hcl/analytics/betting?season=2025",
    "/api/hcl/analytics/weather?season=2025",
    "/api/hcl/analytics/rest?season=2025",
    "/api/hcl/analytics/referees?season=2025",
    "/api/hcl/analytics/summary?season=2025"
]

for endpoint in endpoints:
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ {endpoint}")
            print(f"   Status: {response.status_code}")
            print(f"   Success: {data.get('success')}")
            print(f"   Keys: {list(data.keys())}")
        else:
            print(f"\n❌ {endpoint}")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"\n❌ {endpoint}")
        print(f"   Error: {str(e)[:200]}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
