import requests

r = requests.get('http://127.0.0.1:5000/api/hcl/teams/KC/games?season=2025&limit=20')
data = r.json()
print(f"KC games returned: {data['count']}")
print(f"\nFirst few games:")
for game in data['games'][:5]:
    result = game.get('result') or 'TBD'
    print(f"  Week {game['week']}: {'vs' if game['is_home'] else '@'} {game['opponent']} - {result}")
