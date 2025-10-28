"""
Test script for HC Lombardo Historical Data API
Sprint 6: Validate all 4 endpoints with comprehensive checks

Tests:
1. GET /api/teams - List all teams
2. GET /api/teams/<abbr> - Team overview
3. GET /api/teams/<abbr>/games - Team game history
4. GET /api/games - Games by week
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def print_test_header(test_name):
    """Print formatted test header."""
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)

def test_root_endpoint():
    """Test 1: Root endpoint health check."""
    print_test_header("Root Endpoint Health Check")
    
    response = requests.get(f"{BASE_URL}/")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    assert response.status_code == 200, "Expected 200 OK"
    data = response.json()
    assert data['status'] == 'healthy', "Expected healthy status"
    assert 'endpoints' in data, "Expected endpoints listing"
    
    print("✅ PASSED: Root endpoint healthy")
    return True

def test_get_teams():
    """Test 2: GET /api/teams - List all teams."""
    print_test_header("GET /api/teams - List All Teams")
    
    response = requests.get(f"{BASE_URL}/api/teams?season=2024")
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    print(f"Season: {data['season']}")
    print(f"Total Teams: {data['total_teams']}")
    print(f"\nTop 5 Teams by EPA:")
    
    for i, team in enumerate(data['teams'][:5], 1):
        record = f"{team['wins']}-{team['losses']}"
        ppg = float(team['avg_ppg_for'])
        epa = float(team['avg_epa_offense']) if team['avg_epa_offense'] else 0
        print(f"  {i}. {team['team']:3s} ({record}): {ppg:.1f} PPG, {epa:.3f} EPA/play")
    
    # Validations
    assert response.status_code == 200, "Expected 200 OK"
    assert data['season'] == 2024, "Expected season 2024"
    assert data['total_teams'] > 0, "Expected at least 1 team"
    assert len(data['teams']) > 0, "Expected teams array"
    
    # Check required fields in first team
    first_team = data['teams'][0]
    required_fields = ['team', 'games_played', 'wins', 'losses', 'avg_ppg_for', 'avg_epa_offense']
    for field in required_fields:
        assert field in first_team, f"Expected field '{field}' in team data"
    
    print(f"\n✅ PASSED: Retrieved {data['total_teams']} teams successfully")
    return True

def test_get_team_overview():
    """Test 3: GET /api/teams/<abbr> - Team overview."""
    print_test_header("GET /api/teams/BAL - Team Overview")
    
    team = "BAL"
    response = requests.get(f"{BASE_URL}/api/teams/{team}?season=2024")
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    print(f"\nTeam: {data['team']}")
    print(f"Season: {data['season']}")
    print(f"Record: {data['record']} ({data['games_played']} games)")
    
    print(f"\nOffense:")
    print(f"  PPG: {data['offense']['avg_ppg']}")
    print(f"  EPA/play: {data['offense']['avg_epa_per_play']}")
    print(f"  Success Rate: {data['offense']['avg_success_rate']}")
    print(f"  Yards/play: {data['offense']['avg_yards_per_play']}")
    
    print(f"\nDefense:")
    print(f"  PPG Allowed: {data['defense']['avg_ppg_allowed']}")
    print(f"  EPA/play: {data['defense']['avg_epa_per_play']}")
    
    print(f"\nSplits:")
    print(f"  Home: {data['splits']['home']}")
    print(f"  Away: {data['splits']['away']}")
    
    # Validations
    assert response.status_code == 200, "Expected 200 OK"
    assert data['team'] == team, f"Expected team {team}"
    assert data['season'] == 2024, "Expected season 2024"
    assert 'offense' in data, "Expected offense stats"
    assert 'defense' in data, "Expected defense stats"
    assert 'splits' in data, "Expected home/away splits"
    
    print(f"\n✅ PASSED: Team overview loaded successfully")
    return True

def test_get_team_games():
    """Test 4: GET /api/teams/<abbr>/games - Team game history."""
    print_test_header("GET /api/teams/BAL/games - Game History")
    
    team = "BAL"
    response = requests.get(f"{BASE_URL}/api/teams/{team}/games?season=2024")
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    print(f"\nTeam: {data['team']}")
    print(f"Season: {data['season']}")
    print(f"Total Games: {data['total_games']}")
    
    print(f"\nGame-by-Game Results:")
    for game in data['games']:
        result = "W" if game['won'] else "L"
        location = "vs" if game['is_home'] else "@"
        score = f"{game['points_scored']}-{game['points_allowed']}"
        epa = game['epa_per_play']
        sr = game['success_rate']
        print(f"  Week {game['week']:2d} {result} {location} {game['opponent']:3s} ({score}): "
              f"EPA={epa:.3f}, SR={sr:.3f}")
    
    # Validations
    assert response.status_code == 200, "Expected 200 OK"
    assert data['team'] == team, f"Expected team {team}"
    assert data['season'] == 2024, "Expected season 2024"
    assert data['total_games'] > 0, "Expected at least 1 game"
    assert len(data['games']) > 0, "Expected games array"
    
    # Check required fields in first game
    first_game = data['games'][0]
    required_fields = ['game_id', 'week', 'opponent', 'is_home', 'points_scored', 
                      'points_allowed', 'won', 'epa_per_play', 'success_rate']
    for field in required_fields:
        assert field in first_game, f"Expected field '{field}' in game data"
    
    print(f"\n✅ PASSED: Retrieved {data['total_games']} games successfully")
    return True

def test_get_games_by_week():
    """Test 5: GET /api/games - Games by week."""
    print_test_header("GET /api/games - Games by Week")
    
    response = requests.get(f"{BASE_URL}/api/games?season=2024&week=7")
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    print(f"\nSeason: {data['season']}")
    print(f"Week: {data['week']}")
    print(f"Total Games: {data['total_games']}")
    
    print(f"\nSample Games:")
    for i, game in enumerate(data['games'][:5], 1):
        matchup = f"{game['away_team']} @ {game['home_team']}"
        score = f"{game['away_score']}-{game['home_score']}"
        print(f"  {i}. {matchup:15s} ({score}) - {game['game_date']}")
    
    # Validations
    assert response.status_code == 200, "Expected 200 OK"
    assert data['season'] == 2024, "Expected season 2024"
    assert data['week'] == 7, "Expected week 7"
    assert data['total_games'] > 0, "Expected at least 1 game"
    assert len(data['games']) > 0, "Expected games array"
    
    # Check required fields in first game
    first_game = data['games'][0]
    required_fields = ['game_id', 'home_team', 'away_team', 'home_score', 
                      'away_score', 'game_date']
    for field in required_fields:
        assert field in first_game, f"Expected field '{field}' in game data"
    
    print(f"\n✅ PASSED: Retrieved {data['total_games']} games for Week 7")
    return True

def test_error_handling():
    """Test 6: Error handling."""
    print_test_header("Error Handling Tests")
    
    # Test 1: Invalid team
    print("\nTest 1: Invalid team abbreviation")
    response = requests.get(f"{BASE_URL}/api/teams/XXX?season=2024")
    print(f"  Status: {response.status_code}")
    print(f"  Error: {response.json()['error']}")
    assert response.status_code == 404, "Expected 404 for invalid team"
    print("  ✅ Correctly returns 404")
    
    # Test 2: Missing week parameter
    print("\nTest 2: Missing required parameters")
    response = requests.get(f"{BASE_URL}/api/games?season=2024")
    print(f"  Status: {response.status_code}")
    print(f"  Error: {response.json()['error']}")
    assert response.status_code == 400, "Expected 400 for missing parameter"
    print("  ✅ Correctly returns 400")
    
    # Test 3: No data for season
    print("\nTest 3: No data for season")
    response = requests.get(f"{BASE_URL}/api/teams/KC?season=2020")
    print(f"  Status: {response.status_code}")
    print(f"  Error: {response.json()['error']}")
    assert response.status_code == 404, "Expected 404 for no data"
    print("  ✅ Correctly returns 404")
    
    print("\n✅ PASSED: All error handling working correctly")
    return True

def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("HC LOMBARDO HISTORICAL DATA API - TEST SUITE")
    print("Sprint 6: Endpoint Validation")
    print("="*70)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base URL: {BASE_URL}")
    
    tests = [
        ("Root Endpoint", test_root_endpoint),
        ("GET /api/teams", test_get_teams),
        ("GET /api/teams/<abbr>", test_get_team_overview),
        ("GET /api/teams/<abbr>/games", test_get_team_games),
        ("GET /api/games", test_get_games_by_week),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASSED"))
        except AssertionError as e:
            results.append((test_name, f"FAILED: {e}"))
            print(f"\n❌ FAILED: {e}")
        except Exception as e:
            results.append((test_name, f"ERROR: {e}"))
            print(f"\n❌ ERROR: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, status in results if status == "PASSED")
    total = len(results)
    
    for test_name, status in results:
        icon = "✅" if status == "PASSED" else "❌"
        print(f"{icon} {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! API is ready for frontend integration.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
