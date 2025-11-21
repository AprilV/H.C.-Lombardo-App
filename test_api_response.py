import requests

# Test the teams API
response = requests.get('http://localhost:5000/api/teams')
data = response.json()

# Find Dallas and Green Bay
for team in data['teams']:
    if team['abbreviation'] in ['DAL', 'GB']:
        print(f"{team['name']} ({team['abbreviation']}): wins={team['wins']}, losses={team['losses']}, ties={team['ties']}")
