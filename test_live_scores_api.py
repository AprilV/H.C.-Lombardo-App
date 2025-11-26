import requests
import json

print("Testing Live Scores API...")
print("=" * 60)

response = requests.get('http://localhost:5000/api/live-scores')
data = response.json()

print(f"\nAPI Success: {data.get('success')}")
print(f"Week Info: {data.get('week_info')}")
print(f"Number of games: {len(data.get('games', []))}")

print("\n" + "=" * 60)
print("GAME DATA:")
print("=" * 60)

for i, game in enumerate(data.get('games', []), 1):
    print(f"\nGame {i}:")
    print(f"  {game['away_team']} @ {game['home_team']}")
    print(f"  Score: {game['away_score']} - {game['home_score']}")
    print(f"  Status: {game['status']}")
    print(f"  AI Spread: {game.get('ai_spread')}")
    print(f"  Vegas Spread: {game.get('vegas_spread')}")
    print(f"  Vegas Total: {game.get('vegas_total')}")
    print(f"  AI Prediction: {game.get('ai_prediction')}")
    
    # Check if differential tracker should show
    if game.get('ai_spread') or game.get('vegas_spread'):
        print(f"  ✓ Differential tracker WILL SHOW")
    else:
        print(f"  ✗ Differential tracker WON'T SHOW (no spread data)")

print("\n" + "=" * 60)
