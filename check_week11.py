import requests

r = requests.get('http://127.0.0.1:5000/api/hcl/teams/KC/games?season=2025')
games = r.json()['games']

w11 = [g for g in games if g['week'] == 11]
if w11:
    game = w11[0]
    print(f"KC Week 11 @ {game['opponent']}")
    print(f"  Team points: {game['team_points']}")
    print(f"  Home score: {game['home_score']}")
    print(f"  Away score: {game['away_score']}")
    print(f"  Is home: {game['is_home']}")
    print(f"  Result: {game['result']}")
