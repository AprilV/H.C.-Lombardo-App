"""
Test production API endpoints
Sprint 7 - Production Integration
"""

import requests

print("="*70)
print("TESTING PRODUCTION API ENDPOINTS")
print("="*70)

BASE_URL = "http://127.0.0.1:5000/api/hcl"

# Test 1: GET /api/hcl/teams
print("\nTest 1: GET /api/hcl/teams?season=2025")
print("-"*70)
try:
    r = requests.get(f"{BASE_URL}/teams?season=2025")
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Teams: {len(data)}")
        print("\nFirst 5 teams:")
        for t in data[:5]:
            print(f"  {t['team']}: {t['wins']}-{t['losses']}, {float(t['avg_ppg_for']):.1f} PPG, {float(t['avg_epa_offense']) if t['avg_epa_offense'] else 0:.3f} EPA")
    else:
        print(f"❌ Error: {r.text}")
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 2: GET /api/hcl/teams/BAL
print("\n\nTest 2: GET /api/hcl/teams/BAL?season=2025")
print("-"*70)
try:
    r = requests.get(f"{BASE_URL}/teams/BAL?season=2025")
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Team: {data['team']}")
        print(f"   Record: {data['wins']}-{data['losses']}")
        print(f"   Games Played: {data['games_played']}")
        print(f"   PPG: {float(data['avg_ppg_for']):.1f}")
        print(f"   EPA/Play: {float(data['avg_epa_offense']) if data['avg_epa_offense'] else 0:.3f}")
    else:
        print(f"❌ Error: {r.text}")
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 3: GET /api/hcl/teams/KC/games
print("\n\nTest 3: GET /api/hcl/teams/KC/games?season=2025")
print("-"*70)
try:
    r = requests.get(f"{BASE_URL}/teams/KC/games?season=2025")
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Games: {len(data)}")
        print("\nFirst 3 games:")
        for g in data[:3]:
            result = "W" if g['won'] else "L"
            print(f"  Week {g['week']} vs {g['opponent']}: {result} {g['points_scored']}-{g['points_allowed']}")
    else:
        print(f"❌ Error: {r.text}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*70)
print("API TEST COMPLETE")
print("="*70)
