"""
Test the combine logic to see name mismatches
"""
import requests
from bs4 import BeautifulSoup

# Get offense team names from TeamRankings
url_offense = "https://www.teamrankings.com/nfl/stat/points-per-game"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url_offense, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')
table = soup.find('table', class_='tr-table')

teamrankings_names = []
if table:
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        if len(cells) >= 3:
            team_name = cells[1].get_text(strip=True)
            teamrankings_names.append(team_name)

# Get standings team names from ESPN
url_espn = "https://site.web.api.espn.com/apis/v2/sports/football/nfl/standings"
response = requests.get(url_espn)
data = response.json()

espn_names = {}
if 'children' in data:
    for conference in data['children']:
        if 'standings' in conference and 'entries' in conference['standings']:
            for entry in conference['standings']['entries']:
                team_name = entry['team']['displayName']
                espn_names[team_name] = True

print("="*70)
print("TEAM NAME COMPARISON")
print("="*70)

print(f"\nTeamRankings teams: {len(teamrankings_names)}")
print(f"ESPN teams: {len(espn_names)}")

print("\n" + "="*70)
print("MISMATCHES:")
print("="*70)

for tr_name in teamrankings_names:
    if tr_name not in espn_names:
        print(f"❌ TeamRankings has '{tr_name}' - NOT in ESPN")
        # Try to find close match
        for espn_name in espn_names.keys():
            if tr_name.split()[-1] == espn_name.split()[-1]:  # Same team name (e.g., "Lions")
                print(f"   Possible match: ESPN has '{espn_name}'")

print("\n" + "="*70)
print("MATCHES:")
print("="*70)
matches = 0
for tr_name in teamrankings_names[:5]:
    if tr_name in espn_names:
        print(f"✅ '{tr_name}' - MATCH")
        matches += 1

print(f"\nTotal matches: {matches}/{len(teamrankings_names)}")
