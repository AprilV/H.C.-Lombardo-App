"""
Test HCL API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5001/api/hcl"

def test_endpoints():
    print("\n🧪 Testing HCL API Endpoints")
    print("=" * 60)
    
    # Test 1: GET /api/hcl/teams
    print("\n[1/3] Testing GET /api/hcl/teams...")
    try:
        response = requests.get(f"{BASE_URL}/teams")
        data = response.json()
        
        if data['success']:
            print(f"✅ SUCCESS: {data['count']} teams returned")
            print(f"   Sample: {data['teams'][0]['team']} - {data['teams'][0]['wins']}-{data['teams'][0]['losses']}, {data['teams'][0]['ppg']} PPG")
        else:
            print(f"❌ FAILED: {data.get('error')}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: GET /api/hcl/teams/BAL
    print("\n[2/3] Testing GET /api/hcl/teams/BAL...")
    try:
        response = requests.get(f"{BASE_URL}/teams/BAL")
        data = response.json()
        
        if data['success']:
            team = data['team']
            print(f"✅ SUCCESS: {team['team']} season stats retrieved")
            print(f"   Record: {team['wins']}-{team['losses']}")
            print(f"   PPG: {team['ppg']}, EPA: {team['epa_per_play']}")
            print(f"   Home/Away: {team['home_ppg']}/{team['away_ppg']} PPG")
        else:
            print(f"❌ FAILED: {data.get('error')}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: GET /api/hcl/teams/BAL/games
    print("\n[3/3] Testing GET /api/hcl/teams/BAL/games...")
    try:
        response = requests.get(f"{BASE_URL}/teams/BAL/games")
        data = response.json()
        
        if data['success']:
            print(f"✅ SUCCESS: {data['count']} games returned for {data['team']}")
            game = data['games'][0]
            print(f"   Latest: Week {game['week']} vs {game['opponent']}")
            print(f"   Result: {game['result']} {game['team_points']}-{game['opponent_points']}")
            print(f"   Stats: {game['epa_per_play']} EPA, {game['total_yards']} yards")
        else:
            print(f"❌ FAILED: {data.get('error')}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API Testing Complete!\n")

if __name__ == '__main__':
    test_endpoints()
