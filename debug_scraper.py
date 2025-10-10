"""
Debug version of scraper to see what's happening
"""
import requests
from datetime import datetime

def scrape_standings_debug():
    """Scrape team standings with debug output"""
    url = "https://site.web.api.espn.com/apis/v2/sports/football/nfl/standings"
    
    print("\n" + "="*70)
    print("DEBUG: Scraping standings from ESPN")
    print("="*70)
    
    try:
        response = requests.get(url)
        data = response.json()
        
        teams = {}  # Use dict to avoid duplicates
        
        # Get standings from children (conferences/divisions)
        if 'children' in data:
            print(f"✓ Found {len(data['children'])} conferences")
            
            for conference in data['children']:
                conf_name = conference.get('name', 'Unknown')
                print(f"\nProcessing: {conf_name}")
                
                if 'standings' in conference and 'entries' in conference['standings']:
                    entries = conference['standings']['entries']
                    print(f"  Found {len(entries)} teams")
                    
                    for entry in entries:
                        team_name = entry['team']['displayName']
                        stats = entry['stats']
                        
                        # Find wins and losses in stats
                        wins = 0
                        losses = 0
                        for stat in stats:
                            if stat['name'] == 'wins':
                                wins = int(stat['value'])
                            elif stat['name'] == 'losses':
                                losses = int(stat['value'])
                        
                        teams[team_name] = {
                            'name': team_name,
                            'wins': wins,
                            'losses': losses
                        }
                        print(f"    ✓ {team_name}: {wins}-{losses}")
        
        teams_list = list(teams.values())
        print(f"\n✅ Total teams scraped: {len(teams_list)}")
        return teams_list
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

# Run the debug scraper
teams = scrape_standings_debug()

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Teams returned: {len(teams)}")
if len(teams) > 0:
    print("\nFirst 5 teams:")
    for team in teams[:5]:
        print(f"  {team['name']:30s} {team['wins']}-{team['losses']}")
