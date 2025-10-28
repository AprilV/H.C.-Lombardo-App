"""
Sportradar NFL API Testing
Tests API connectivity and data retrieval
"""
import requests
import json
from datetime import datetime

# API Configuration
API_KEY = "TuH3WpobOAO1cCQAigHdacAKDcqgwx6mWetV3jmd"
BASE_URL = "https://api.sportradar.us/nfl/official/trial/v7/en"

def test_api_connection():
    """Test basic API connectivity"""
    print("\n" + "="*70)
    print("SPORTRADAR NFL API TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Test 1: Current Season Standings (using 2024 season - 2025 may not be in trial)
    print("\n[TEST 1] Fetching Current Season Standings...")
    try:
        url = f"{BASE_URL}/seasons/2024/REG/standings.json?api_key={API_KEY}"
        response = requests.get(url, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Display basic info
            if 'season' in data:
                print(f"   ✅ Season: {data['season'].get('year')} - {data['season'].get('type')}")
            
            # Count teams/conferences
            if 'conferences' in data:
                total_teams = 0
                for conf in data['conferences']:
                    conf_name = conf.get('name', 'Unknown')
                    divisions = conf.get('divisions', [])
                    for div in divisions:
                        teams = div.get('teams', [])
                        total_teams += len(teams)
                        print(f"   ✅ {conf_name} - {div.get('name')}: {len(teams)} teams")
                
                print(f"\n   ✅ Total Teams: {total_teams}")
                
                # Show sample team data
                if total_teams > 0:
                    sample_team = data['conferences'][0]['divisions'][0]['teams'][0]
                    print(f"\n   Sample Team Data:")
                    print(f"      Name: {sample_team.get('market')} {sample_team.get('name')}")
                    print(f"      Alias: {sample_team.get('alias')}")
                    print(f"      Record: {sample_team.get('wins')}-{sample_team.get('losses')}-{sample_team.get('ties')}")
                    
                    # Save full response for inspection
                    with open('sportradar_standings_sample.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"\n   ✅ Full response saved to: sportradar_standings_sample.json")
            
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_team_profile():
    """Test fetching a single team's data"""
    print("\n[TEST 2] Fetching Team Profile...")
    
    # First, we need a team ID from standings
    # For now, we'll try to get all teams list
    try:
        url = f"{BASE_URL}/league/hierarchy.json?api_key={API_KEY}"
        response = requests.get(url, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Get first team ID
            if 'conferences' in data:
                sample_team = data['conferences'][0]['divisions'][0]['teams'][0]
                team_id = sample_team['id']
                team_name = f"{sample_team['market']} {sample_team['name']}"
                
                print(f"   ✅ Retrieved team: {team_name} (ID: {team_id})")
                
                # Save hierarchy
                with open('sportradar_hierarchy.json', 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"   ✅ League hierarchy saved to: sportradar_hierarchy.json")
                
                return team_id
            
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return None

def test_weekly_schedule():
    """Test fetching weekly schedule"""
    print("\n[TEST 3] Fetching Weekly Schedule...")
    
    try:
        # Get current week schedule (using 2024 season)
        url = f"{BASE_URL}/games/2024/REG/7/schedule.json?api_key={API_KEY}"
        response = requests.get(url, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'week' in data:
                print(f"   ✅ Week: {data['week'].get('sequence')} - {data['week'].get('title')}")
            
            if 'games' in data:
                games = data['games']
                print(f"   ✅ Games in this week: {len(games)}")
                
                # Show first game details
                if games:
                    game = games[0]
                    home = game.get('home', {})
                    away = game.get('away', {})
                    print(f"\n   Sample Game:")
                    print(f"      {away.get('alias')} @ {home.get('alias')}")
                    print(f"      Status: {game.get('status')}")
                    print(f"      Scheduled: {game.get('scheduled', 'N/A')}")
                
                # Save schedule
                with open('sportradar_week7_schedule.json', 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"\n   ✅ Week 7 schedule saved to: sportradar_week7_schedule.json")
                
                return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_seasonal_statistics():
    """Test fetching seasonal statistics"""
    print("\n[TEST 4] Fetching Seasonal Statistics...")
    
    try:
        url = f"{BASE_URL}/seasons/2024/REG/teams/statistics.json?api_key={API_KEY}"
        response = requests.get(url, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'season' in data:
                print(f"   ✅ Season: {data['season'].get('year')} - {data['season'].get('type')}")
            
            if 'conferences' in data:
                # Count teams with stats
                team_count = 0
                sample_team = None
                
                for conf in data['conferences']:
                    for div in conf.get('divisions', []):
                        teams = div.get('teams', [])
                        team_count += len(teams)
                        if not sample_team and teams:
                            sample_team = teams[0]
                
                print(f"   ✅ Teams with statistics: {team_count}")
                
                # Show sample stats
                if sample_team:
                    print(f"\n   Sample Team Stats: {sample_team.get('market')} {sample_team.get('name')}")
                    
                    if 'record' in sample_team:
                        record = sample_team['record']
                        print(f"      Record: {record.get('wins')}-{record.get('losses')}-{record.get('ties')}")
                    
                    if 'scoring' in sample_team:
                        scoring = sample_team['scoring']
                        print(f"      Points For: {scoring.get('points')}")
                        print(f"      Points Against: {scoring.get('points_against')}")
                    
                    # Check for detailed stats
                    if 'statistics' in sample_team:
                        stats = sample_team['statistics']
                        print(f"      Available stat categories: {len(stats)} categories")
                
                # Save full stats
                with open('sportradar_season_stats.json', 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"\n   ✅ Season statistics saved to: sportradar_season_stats.json")
                
                return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    results = {
        'standings': False,
        'team_profile': False,
        'schedule': False,
        'statistics': False
    }
    
    # Run tests
    results['standings'] = test_api_connection()
    team_id = test_team_profile()
    results['team_profile'] = team_id is not None
    results['schedule'] = test_weekly_schedule()
    results['statistics'] = test_seasonal_statistics()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name.upper()}: {status}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n   ✅ ALL TESTS PASSED - API IS READY TO USE!")
    else:
        print("\n   ⚠️  SOME TESTS FAILED - CHECK ERRORS ABOVE")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
