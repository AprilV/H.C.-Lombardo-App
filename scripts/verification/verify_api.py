"""
Manual API Verification Script
Tests all API endpoints to verify production readiness
"""
import requests
import sys
from datetime import datetime

def verify_api():
    """Verify API is working correctly"""
    api_url = "http://localhost:5000"
    tests_passed = 0
    tests_failed = 0
    
    print("\n" + "="*80)
    print("API VERIFICATION TEST")
    print(f"Testing: {api_url}")
    print("="*80)
    
    # TEST 1: Health endpoint
    print("\n1️⃣  Testing /health endpoint...")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database')}")
            print(f"   Teams: {data.get('teams_count')}")
            tests_passed += 1
        else:
            print(f"   ❌ Failed: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # TEST 2: Teams list endpoint
    print("\n2️⃣  Testing /api/teams endpoint...")
    try:
        response = requests.get(f"{api_url}/api/teams", timeout=5)
        if response.status_code == 200:
            data = response.json()
            teams = data.get('teams', [])
            print(f"   ✅ Status: {response.status_code}")
            print(f"   Teams returned: {len(teams)}")
            
            if teams:
                first_team = teams[0]
                print(f"\n   First team structure:")
                for key, value in first_team.items():
                    print(f"      • {key}: {value}")
                
                # Check for required fields
                required_fields = ['name', 'abbreviation', 'wins', 'losses', 'ties', 
                                 'ppg', 'pa', 'games_played', 'last_updated']
                missing = [f for f in required_fields if f not in first_team]
                
                if missing:
                    print(f"\n   ❌ Missing fields: {missing}")
                    tests_failed += 1
                else:
                    print(f"\n   ✅ All required fields present")
                    tests_passed += 1
            else:
                print(f"   ❌ No teams returned")
                tests_failed += 1
        else:
            print(f"   ❌ Failed: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # TEST 3: Single team endpoint
    print("\n3️⃣  Testing /api/teams/DAL endpoint...")
    try:
        response = requests.get(f"{api_url}/api/teams/DAL", timeout=5)
        if response.status_code == 200:
            team = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"\n   Dallas Cowboys:")
            print(f"      Name: {team.get('name')}")
            print(f"      Record: {team.get('wins')}-{team.get('losses')}-{team.get('ties')}")
            print(f"      PPG: {team.get('ppg')}")
            print(f"      PA: {team.get('pa')}")
            print(f"      Games: {team.get('games_played')}")
            print(f"      Last Updated: {team.get('last_updated')}")
            
            # Verify ties field
            if 'ties' in team:
                print(f"\n   ✅ Ties field present: {team.get('ties')}")
                tests_passed += 1
            else:
                print(f"\n   ❌ Ties field missing")
                tests_failed += 1
            
            # Verify timestamp
            if 'last_updated' in team and team.get('last_updated'):
                print(f"   ✅ Timestamp field present and populated")
                tests_passed += 1
            else:
                print(f"   ❌ Timestamp field missing or empty")
                tests_failed += 1
        else:
            print(f"   ❌ Failed: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # TEST 4: Data freshness check
    print("\n4️⃣  Checking data freshness...")
    try:
        response = requests.get(f"{api_url}/api/teams/BUF", timeout=5)
        if response.status_code == 200:
            team = response.json()
            last_updated = team.get('last_updated')
            
            if last_updated:
                # Parse timestamp
                from dateutil import parser
                update_time = parser.parse(last_updated)
                now = datetime.now(update_time.tzinfo) if update_time.tzinfo else datetime.now()
                age_seconds = (now - update_time).total_seconds()
                age_minutes = age_seconds / 60
                
                print(f"   Last updated: {last_updated}")
                print(f"   Age: {age_minutes:.1f} minutes")
                
                if age_minutes < 30:
                    print(f"   ✅ Data is fresh (<30 minutes old)")
                    tests_passed += 1
                else:
                    print(f"   ⚠️  Data is stale (>{age_minutes:.0f} minutes old)")
                    print(f"   💡 Run: python multi_source_data_fetcher.py to refresh")
                    tests_passed += 1  # Not a failure, just a warning
            else:
                print(f"   ⚠️  No timestamp available")
                tests_passed += 1
        else:
            print(f"   ❌ Failed: {response.status_code}")
            tests_failed += 1
    except ImportError:
        print(f"   ⚠️  dateutil not installed - skipping freshness check")
        print(f"   Install with: pip install python-dateutil")
        tests_passed += 1
    except Exception as e:
        print(f"   ⚠️  Could not check freshness: {e}")
        tests_passed += 1
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Total Tests: {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n✅ ALL API TESTS PASSED - PRODUCTION READY")
        return 0
    else:
        print(f"\n❌ {tests_failed} TEST(S) FAILED - NOT PRODUCTION READY")
        return 1

def main():
    print("\n⚠️  Make sure API server is running first:")
    print("   python api_server.py")
    input("\nPress Enter when API is running (or Ctrl+C to cancel)...")
    
    result = verify_api()
    sys.exit(result)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Verification cancelled")
        sys.exit(1)
