import requests
import json

url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
response = requests.get(url)
data = response.json()

print(f"Top level keys: {data.keys()}")
print(f"\nSports count: {len(data.get('sports', []))}")

if 'sports' in data and len(data['sports']) > 0:
    sport = data['sports'][0]
    print(f"Sport keys: {sport.keys()}")
    
    if 'leagues' in sport and len(sport['leagues']) > 0:
        league = sport['leagues'][0]
        print(f"League keys: {league.keys()}")
        print(f"Teams count: {len(league.get('teams', []))}")
        
        if 'teams' in league and len(league['teams']) > 0:
            # Show first team structure
            first_team = league['teams'][0]['team']
            print(f"\nFirst team name: {first_team['displayName']}")
            print(f"First team keys: {first_team.keys()}")
            
            if 'record' in first_team:
                print(f"\nRecord structure: {json.dumps(first_team['record'], indent=2)}")
