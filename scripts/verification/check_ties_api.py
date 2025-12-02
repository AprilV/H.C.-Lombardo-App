import requests
import json

# Get teams from API
response = requests.get('http://localhost:5000/api/teams')
print(f"Status code: {response.status_code}")
print(f"Response text: {response.text[:500]}")

if response.status_code == 200:
    data = response.json()
    teams = data.get('teams', [])
    
    # Filter teams with ties
    ties_teams = [t for t in teams if t.get('ties', 0) > 0]
    
    print(f"\nTeams with ties: {len(ties_teams)}")
    print("-" * 50)
    for team in sorted(ties_teams, key=lambda t: t['name']):
        print(f"{team['name']} ({team['abbreviation']}): {team['wins']}-{team['losses']}-{team['ties']}")
else:
    print(f"Error: {response.status_code}")
