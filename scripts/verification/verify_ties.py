import requests

response = requests.get('http://localhost:5000/api/hcl/teams?season=2025')
data = response.json()

print("Looking for Dallas and Green Bay:")
for team in data['teams']:
    if team['team'] in ['DAL', 'GB']:
        print(f"{team['team']}: {team['wins']}-{team['losses']}-{team['ties']}")
