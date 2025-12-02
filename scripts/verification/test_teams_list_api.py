import requests
import json

# Test the teams list API
response = requests.get('http://localhost:5000/api/hcl/teams?season=2025')
data = response.json()

print(f"Total teams: {len(data['teams'])}")
print("\nFirst 3 teams (full structure):")
for team in data['teams'][:3]:
    print(json.dumps(team, indent=2))
    print("---")
