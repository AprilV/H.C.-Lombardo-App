"""
Comprehensive test of ESPN standings API
"""
import requests
import json

print("="*70)
print("TESTING ESPN STANDINGS API")
print("="*70)

url = "https://site.web.api.espn.com/apis/v2/sports/football/nfl/standings"
print(f"\nURL: {url}")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTop-level keys: {list(data.keys())}")
        
        if 'children' in data:
            print(f"\nConferences found: {len(data['children'])}")
            
            all_teams = []
            for i, conference in enumerate(data['children']):
                conf_name = conference.get('name', f'Conference {i}')
                print(f"\n{conf_name}:")
                
                if 'standings' in conference and 'entries' in conference['standings']:
                    entries = conference['standings']['entries']
                    print(f"  Teams: {len(entries)}")
                    
                    for entry in entries[:3]:  # Show first 3 teams
                        team_name = entry['team']['displayName']
                        stats = entry['stats']
                        
                        wins = 0
                        losses = 0
                        for stat in stats:
                            if stat['name'] == 'wins':
                                wins = int(stat['value'])
                            elif stat['name'] == 'losses':
                                losses = int(stat['value'])
                        
                        print(f"    {team_name:30s} {wins}-{losses}")
                        all_teams.append({'name': team_name, 'wins': wins, 'losses': losses})
            
            print(f"\n✅ TOTAL TEAMS FOUND: {len(all_teams)}")
            
            if len(all_teams) > 0:
                print("\n✅ ESPN API IS WORKING!")
            else:
                print("\n❌ No teams extracted")
        else:
            print("\n❌ No 'children' key found")
            print(f"Available keys: {list(data.keys())}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()
