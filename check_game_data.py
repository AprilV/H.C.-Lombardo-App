import requests
import json

r = requests.get('http://127.0.0.1:5000/api/hcl/teams/NE/games?season=2025')
games = r.json()['games']

print("NE 2025 Game Data Check:\n")
for game in sorted(games, key=lambda x: x['week']):
    week = game['week']
    passing = game.get('passing_yards') or 'MISSING'
    rushing = game.get('rushing_yards') or 'MISSING'
    total = game.get('total_yards') or 'MISSING'
    print(f"Week {week:2d}: Pass={str(passing):>7}, Rush={str(rushing):>7}, Total={str(total):>7}")
