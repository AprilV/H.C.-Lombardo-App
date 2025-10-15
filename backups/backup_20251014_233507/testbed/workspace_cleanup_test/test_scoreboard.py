import requests
import json

url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
response = requests.get(url)
data = response.json()

print(f"Top level keys: {list(data.keys())}")

if 'leagues' in data:
    print(f"\nLeagues count: {len(data['leagues'])}")
    if len(data['leagues']) > 0:
        league = data['leagues'][0]
        print(f"League keys: {list(league.keys())}")
        
        if 'standings' in league:
            print(f"\nStandings keys: {list(league['standings'].keys())}")
            print(json.dumps(league['standings'], indent=2)[:500])
        else:
            print("\nNo 'standings' key in league")
