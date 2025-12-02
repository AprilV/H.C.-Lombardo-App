import requests
import json

# Fetch ESPN data
print("Fetching from ESPN API...")
url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
response = requests.get(url)
data = response.json()

# Check if Baltimore Ravens exists in ESPN data
ravens_found = False
bills_found = False

print("\n" + "=" * 60)
print("SEARCHING ESPN API FOR RAVENS AND BILLS:")

if 'events' in data:
    for event in data['events']:
        for competition in event.get('competitions', []):
            for team_data in competition.get('competitors', []):
                team_name = team_data.get('team', {}).get('displayName', '')
                team_abbr = team_data.get('team', {}).get('abbreviation', '')
                
                if 'Baltimore' in team_name or team_abbr == 'BAL':
                    ravens_found = True
                    print(f"\n✅ FOUND RAVENS:")
                    print(f"   Name: {team_name}")
                    print(f"   Abbreviation: {team_abbr}")
                    print(f"   Record: {team_data.get('records', [{}])[0].get('summary', 'N/A')}")
                    
                if 'Buffalo' in team_name or team_abbr == 'BUF':
                    bills_found = True
                    print(f"\n✅ FOUND BILLS:")
                    print(f"   Name: {team_name}")
                    print(f"   Abbreviation: {team_abbr}")
                    print(f"   Record: {team_data.get('records', [{}])[0].get('summary', 'N/A')}")

# Check standings endpoint
print("\n" + "=" * 60)
print("CHECKING ESPN STANDINGS ENDPOINT:")
standings_url = "http://site.api.espn.com/apis/v2/sports/football/nfl/standings"
standings_response = requests.get(standings_url)
standings_data = standings_response.json()

ravens_in_standings = False
bills_in_standings = False

if 'children' in standings_data:
    for conference in standings_data['children']:
        for standing in conference.get('standings', {}).get('entries', []):
            team = standing.get('team', {})
            team_name = team.get('displayName', '')
            
            if 'Baltimore' in team_name:
                ravens_in_standings = True
                stats = standing.get('stats', [])
                wins = next((s['value'] for s in stats if s['name'] == 'wins'), 0)
                losses = next((s['value'] for s in stats if s['name'] == 'losses'), 0)
                print(f"\n✅ RAVENS IN STANDINGS:")
                print(f"   Name: {team_name}")
                print(f"   Record: {wins}-{losses}")
                
            if 'Buffalo' in team_name:
                bills_in_standings = True
                stats = standing.get('stats', [])
                wins = next((s['value'] for s in stats if s['name'] == 'wins'), 0)
                losses = next((s['value'] for s in stats if s['name'] == 'losses'), 0)
                print(f"\n✅ BILLS IN STANDINGS:")
                print(f"   Name: {team_name}")
                print(f"   Record: {wins}-{losses}")

print("\n" + "=" * 60)
print("SUMMARY:")
print(f"Ravens in scoreboard: {ravens_found}")
print(f"Bills in scoreboard: {bills_found}")
print(f"Ravens in standings: {ravens_in_standings}")
print(f"Bills in standings: {bills_in_standings}")
