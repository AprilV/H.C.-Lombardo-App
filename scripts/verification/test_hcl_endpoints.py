"""Quick test of HCL API endpoints"""
import requests
import json

BASE_URL = "http://localhost:5000/api/hcl"

print("\n" + "="*60)
print("TESTING HCL API ENDPOINTS")
print("="*60)

# Test 1: Get all teams
print("\n[1] Testing GET /api/hcl/teams")
try:
    r = requests.get(f"{BASE_URL}/teams")
    print(f"   Status: {r.status_code}")
    if r.ok:
        data = r.json()
        if data.get('success'):
            teams = data.get('teams', [])
            print(f"   ✓ Teams returned: {len(teams)}")
            if teams:
                print(f"   ✓ First team: {teams[0]['team']} - {teams[0]['wins']}-{teams[0]['losses']}")
        else:
            print(f"   ✗ Error: {data.get('error')}")
    else:
        print(f"   ✗ Error: {r.text}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

# Test 2: Get specific team (DAL)
print("\n[2] Testing GET /api/hcl/teams/DAL")
try:
    r = requests.get(f"{BASE_URL}/teams/DAL")
    print(f"   Status: {r.status_code}")
    if r.ok:
        data = r.json()
        if data.get('success'):
            team = data.get('team', {})
            print(f"   ✓ Team: {team.get('team')}")
            print(f"   ✓ Record: {team.get('wins')}-{team.get('losses')}")
            print(f"   ✓ PPG: {team.get('ppg')}")
            print(f"   ✓ EPA/play: {team.get('epa_per_play')}")
        else:
            print(f"   ✗ Error: {data.get('error')}")
    else:
        print(f"   ✗ Error: {r.text}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

# Test 3: Get team games (DAL)
print("\n[3] Testing GET /api/hcl/teams/DAL/games")
try:
    r = requests.get(f"{BASE_URL}/teams/DAL/games")
    print(f"   Status: {r.status_code}")
    if r.ok:
        data = r.json()
        if data.get('success'):
            games = data.get('games', [])
            print(f"   ✓ Games returned: {len(games)}")
            if games:
                g = games[0]
                print(f"   ✓ First game: Week {g['week']} vs {g['opponent']} ({'W' if g['result'] else 'L'}) {g['team_points']}-{g['opponent_points']}")
        else:
            print(f"   ✗ Error: {data.get('error')}")
    else:
        print(f"   ✗ Error: {r.text}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60 + "\n")
