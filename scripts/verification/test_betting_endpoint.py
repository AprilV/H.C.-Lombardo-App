import requests

print("Testing betting endpoint...")

# Test 1: No team filter
print("\n1. Testing without team filter:")
response = requests.get('http://localhost:5000/api/hcl/analytics/betting?season=2025')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Success: {data.get('success')}")
    print(f"Count: {data.get('count')}")
    if data.get('teams'):
        print(f"First team: {data['teams'][0]}")
else:
    print(f"Error: {response.text}")

# Test 2: With team filter (DAL)
print("\n2. Testing with team=DAL:")
response = requests.get('http://localhost:5000/api/hcl/analytics/betting?season=2025&team=DAL')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Success: {data.get('success')}")
    print(f"Count: {data.get('count')}")
    if data.get('teams'):
        print(f"DAL data: {data['teams'][0]}")
else:
    print(f"Error: {response.text}")

# Test 3: With team filter (KC)
print("\n3. Testing with team=KC:")
response = requests.get('http://localhost:5000/api/hcl/analytics/betting?season=2025&team=KC')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Success: {data.get('success')}")
    print(f"Count: {data.get('count')}")
    if data.get('teams'):
        print(f"KC data: {data['teams'][0]}")
else:
    print(f"Error: {response.text}")
