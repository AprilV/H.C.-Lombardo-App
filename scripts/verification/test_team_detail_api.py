import requests
import json

# Test the team detail API for Dallas
response = requests.get('http://localhost:5000/api/hcl/teams/DAL?season=2025')
data = response.json()

print("Dallas Cowboys team detail:")
print(json.dumps(data, indent=2))
