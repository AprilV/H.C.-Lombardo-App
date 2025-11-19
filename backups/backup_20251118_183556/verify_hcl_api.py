"""
HCL API Verification Script
Tests all HCL endpoints for Phase 2A+ deployment
Following testing protocol from POST_CLEANUP_TEST_RESULTS.md
"""

import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:5000"

# Test results tracker
tests_passed = 0
tests_failed = 0
test_results = []

def print_header(text):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_test(name, status, details=""):
    """Print test result"""
    global tests_passed, tests_failed
    
    status_icon = "✅" if status else "❌"
    status_text = "PASSED" if status else "FAILED"
    
    print(f"\n{status_icon} Test: {name}")
    print(f"   Status: {status_text}")
    
    if details:
        print(f"   Details: {details}")
    
    test_results.append({
        "name": name,
        "status": status_text,
        "details": details
    })
    
    if status:
        tests_passed += 1
    else:
        tests_failed += 1

def test_health_endpoint():
    """Test 1: Health endpoint"""
    print_header("TEST 1: HEALTH ENDPOINT")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy' and data.get('database') == 'connected':
                print_test("Health Endpoint", True, f"Status: {data['status']}, DB: {data['database']}")
                return True
        
        print_test("Health Endpoint", False, f"Status code: {response.status_code}")
        return False
        
    except Exception as e:
        print_test("Health Endpoint", False, f"Error: {str(e)}")
        return False

def test_teams_list():
    """Test 2: GET /api/hcl/teams"""
    print_header("TEST 2: TEAMS LIST ENDPOINT")
    
    try:
        response = requests.get(f"{BASE_URL}/api/hcl/teams?season=2025", timeout=10)
        
        if response.status_code != 200:
            print_test("Teams List Endpoint", False, f"Status code: {response.status_code}")
            return False
        
        data = response.json()
        
        if not data.get('success'):
            print_test("Teams List Endpoint", False, "Response success=False")
            return False
        
        teams = data.get('teams', [])
        team_count = len(teams)
        
        if team_count != 32:
            print_test("Teams List Endpoint", False, f"Expected 32 teams, got {team_count}")
            return False
        
        # Check first team has required fields
        first_team = teams[0]
        required_fields = ['team', 'games_played', 'wins', 'losses', 'ppg', 'yards_per_game', 'yards_per_play', 'completion_pct', 'total_turnovers']
        missing_fields = [f for f in required_fields if f not in first_team]
        
        if missing_fields:
            print_test("Teams List Endpoint", False, f"Missing fields: {missing_fields}")
            return False
        
        print_test("Teams List Endpoint", True, f"32 teams returned with all required fields")
        print(f"   Sample: {first_team['team']} - {first_team['wins']}-{first_team['losses']} ({first_team['games_played']} games)")
        return True
        
    except Exception as e:
        print_test("Teams List Endpoint", False, f"Error: {str(e)}")
        return False

def test_team_details():
    """Test 3: GET /api/hcl/teams/<team_abbr>"""
    print_header("TEST 3: TEAM DETAILS ENDPOINT")
    
    try:
        response = requests.get(f"{BASE_URL}/api/hcl/teams/BAL?season=2025", timeout=10)
        
        if response.status_code != 200:
            print_test("Team Details Endpoint", False, f"Status code: {response.status_code}")
            return False
        
        data = response.json()
        
        if not data.get('success'):
            print_test("Team Details Endpoint", False, "Response success=False")
            return False
        
        team = data.get('team')
        
        if not team:
            print_test("Team Details Endpoint", False, "No team data returned")
            return False
        
        # Check required fields
        required_fields = ['team', 'season', 'games_played', 'wins', 'losses', 'ppg', 
                          'total_yards_per_game', 'passing_yards_per_game', 'rushing_yards_per_game',
                          'yards_per_play', 'completion_pct', 'third_down_pct', 'red_zone_pct',
                          'turnovers', 'ppg_home', 'ppg_away', 'home_wins', 'away_wins']
        
        missing_fields = [f for f in required_fields if f not in team]
        
        if missing_fields:
            print_test("Team Details Endpoint", False, f"Missing fields: {missing_fields}")
            return False
        
        print_test("Team Details Endpoint", True, "All fields present")
        print(f"   Team: {team['team']} ({team['wins']}-{team['losses']})")
        print(f"   PPG: {team['ppg']} (Home: {team['ppg_home']}, Away: {team['ppg_away']})")
        print(f"   Yards/Game: {team['total_yards_per_game']} (Pass: {team['passing_yards_per_game']}, Rush: {team['rushing_yards_per_game']})")
        return True
        
    except Exception as e:
        print_test("Team Details Endpoint", False, f"Error: {str(e)}")
        return False

def test_team_games():
    """Test 4: GET /api/hcl/teams/<team_abbr>/games"""
    print_header("TEST 4: TEAM GAMES ENDPOINT (WITH BETTING/WEATHER)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/hcl/teams/BAL/games?season=2025&limit=5", timeout=10)
        
        if response.status_code != 200:
            print_test("Team Games Endpoint", False, f"Status code: {response.status_code}")
            return False
        
        data = response.json()
        
        if not data.get('success'):
            print_test("Team Games Endpoint", False, "Response success=False")
            return False
        
        games = data.get('games', [])
        
        if not games:
            print_test("Team Games Endpoint", False, "No games returned")
            return False
        
        # Check first game has betting and weather data
        first_game = games[0]
        
        betting_fields = ['spread_line', 'total_line', 'home_moneyline', 'away_moneyline']
        weather_fields = ['roof', 'temp', 'wind']
        context_fields = ['rest_days', 'is_divisional_game', 'referee']
        stats_fields = ['team_points', 'total_yards', 'passing_yards', 'rushing_yards', 
                       'turnovers', 'completion_pct', 'yards_per_play', 'third_down_pct']
        
        all_required_fields = betting_fields + weather_fields + context_fields + stats_fields
        missing_fields = [f for f in all_required_fields if f not in first_game]
        
        if missing_fields:
            print_test("Team Games Endpoint", False, f"Missing fields: {missing_fields}")
            return False
        
        print_test("Team Games Endpoint", True, f"{len(games)} games returned with all betting/weather/context fields")
        print(f"   Latest Game: {first_game['game_id']}")
        print(f"   Score: {first_game['team_points']} pts")
        print(f"   Betting: Spread {first_game['spread_line']}, Total {first_game['total_line']}")
        print(f"   Weather: {first_game['roof']}, {first_game['temp']}°F, {first_game['wind']} MPH wind")
        print(f"   Context: {first_game['rest_days']} days rest, Divisional: {first_game['is_divisional_game']}, Ref: {first_game['referee']}")
        return True
        
    except Exception as e:
        print_test("Team Games Endpoint", False, f"Error: {str(e)}")
        return False

def test_game_details():
    """Test 5: GET /api/hcl/games/<game_id>"""
    print_header("TEST 5: GAME DETAILS ENDPOINT")
    
    try:
        # Use a known game ID from 2025 season
        response = requests.get(f"{BASE_URL}/api/hcl/games/2025_08_CHI_BAL", timeout=10)
        
        if response.status_code != 200:
            print_test("Game Details Endpoint", False, f"Status code: {response.status_code}")
            return False
        
        data = response.json()
        
        if not data.get('success'):
            print_test("Game Details Endpoint", False, "Response success=False")
            return False
        
        game = data.get('game')
        team_stats = data.get('team_stats', [])
        
        if not game:
            print_test("Game Details Endpoint", False, "No game data returned")
            return False
        
        if len(team_stats) != 2:
            print_test("Game Details Endpoint", False, f"Expected 2 team stat records, got {len(team_stats)}")
            return False
        
        # Verify betting/weather/context fields in game
        required_game_fields = ['game_id', 'season', 'week', 'game_date', 'home_team', 'away_team',
                               'home_score', 'away_score', 'spread_line', 'total_line',
                               'home_moneyline', 'away_moneyline', 'roof', 'temp', 'wind',
                               'away_rest', 'home_rest', 'is_divisional_game', 'referee']
        
        missing_game_fields = [f for f in required_game_fields if f not in game]
        
        if missing_game_fields:
            print_test("Game Details Endpoint", False, f"Missing game fields: {missing_game_fields}")
            return False
        
        print_test("Game Details Endpoint", True, "Complete game data with betting/weather/context")
        print(f"   Game: {game['away_team']} @ {game['home_team']}")
        print(f"   Score: {game['away_score']}-{game['home_score']}")
        print(f"   Betting: Spread {game['spread_line']}, Total {game['total_line']}")
        print(f"   Weather: {game['roof']}, {game['temp']}°F")
        print(f"   Team Stats: 2 records returned")
        return True
        
    except Exception as e:
        print_test("Game Details Endpoint", False, f"Error: {str(e)}")
        return False

def test_week_games():
    """Test 6: GET /api/hcl/games/week/<season>/<week>"""
    print_header("TEST 6: WEEKLY GAMES ENDPOINT")
    
    try:
        response = requests.get(f"{BASE_URL}/api/hcl/games/week/2025/8", timeout=10)
        
        if response.status_code != 200:
            print_test("Weekly Games Endpoint", False, f"Status code: {response.status_code}")
            return False
        
        data = response.json()
        
        if not data.get('success'):
            print_test("Weekly Games Endpoint", False, "Response success=False")
            return False
        
        games = data.get('games', [])
        
        if not games:
            print_test("Weekly Games Endpoint", False, "No games returned")
            return False
        
        # Verify all games have betting/weather fields
        first_game = games[0]
        required_fields = ['game_id', 'season', 'week', 'game_date', 'away_team', 'home_team',
                          'away_score', 'home_score', 'spread_line', 'total_line',
                          'home_moneyline', 'away_moneyline', 'roof', 'temp', 'wind',
                          'is_divisional_game', 'referee']
        
        missing_fields = [f for f in required_fields if f not in first_game]
        
        if missing_fields:
            print_test("Weekly Games Endpoint", False, f"Missing fields: {missing_fields}")
            return False
        
        print_test("Weekly Games Endpoint", True, f"{len(games)} games returned for Week 8, 2025")
        print(f"   Sample: {first_game['away_team']} @ {first_game['home_team']} (Spread: {first_game['spread_line']})")
        return True
        
    except Exception as e:
        print_test("Weekly Games Endpoint", False, f"Error: {str(e)}")
        return False

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total_tests = tests_passed + tests_failed
    pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Tests Passed: {tests_passed} ✅")
    print(f"Tests Failed: {tests_failed} ❌")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if tests_failed == 0:
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED - HCL API IS PRODUCTION READY!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("⚠️  SOME TESTS FAILED - REVIEW ERRORS ABOVE")
        print("="*80)
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("="*80)
    print("HCL API VERIFICATION TEST SUITE")
    print("Phase 2A+ Deployment Testing")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Run all tests
    test_health_endpoint()
    test_teams_list()
    test_team_details()
    test_team_games()
    test_game_details()
    test_week_games()
    
    # Print summary
    print_summary()
