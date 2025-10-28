"""
VERIFICATION SCRIPT: Test Complete Integration
Verify all components are working together
"""
import requests
import sys

def test_integration():
    """Test the complete React + Flask + PostgreSQL integration"""
    
    print("=" * 70)
    print("INTEGRATION VERIFICATION TEST")
    print("=" * 70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Flask Server Health
    print("\n[1/5] Testing Flask backend health...")
    try:
        response = requests.get("http://127.0.0.1:5003/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy" and data.get("database") == "connected":
                print("    ✓ PASS: Backend healthy, database connected")
                tests_passed += 1
            else:
                print(f"    ✗ FAIL: Unexpected response: {data}")
                tests_failed += 1
        else:
            print(f"    ✗ FAIL: Status code {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"    ✗ FAIL: {e}")
        tests_failed += 1
    
    # Test 2: Teams Count
    print("\n[2/5] Testing teams count endpoint...")
    try:
        response = requests.get("http://127.0.0.1:5003/api/teams/count", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get("count") == 32:
                print(f"    ✓ PASS: Correct team count: {data['count']}")
                tests_passed += 1
            else:
                print(f"    ✗ FAIL: Wrong count: {data.get('count')}")
                tests_failed += 1
        else:
            print(f"    ✗ FAIL: Status code {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"    ✗ FAIL: {e}")
        tests_failed += 1
    
    # Test 3: Teams Data
    print("\n[3/5] Testing teams data endpoint...")
    try:
        response = requests.get("http://127.0.0.1:5003/api/teams", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get("count") == 32 and len(data.get("teams", [])) == 32:
                sample_team = data["teams"][0]
                if all(key in sample_team for key in ["name", "abbreviation", "wins", "losses", "ppg"]):
                    print(f"    ✓ PASS: All teams data valid")
                    print(f"      Sample: {sample_team['name']} ({sample_team['abbreviation']})")
                    tests_passed += 1
                else:
                    print(f"    ✗ FAIL: Team data missing fields")
                    tests_failed += 1
            else:
                print(f"    ✗ FAIL: Wrong team count in response")
                tests_failed += 1
        else:
            print(f"    ✗ FAIL: Status code {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"    ✗ FAIL: {e}")
        tests_failed += 1
    
    # Test 4: CORS Headers
    print("\n[4/5] Testing CORS headers...")
    try:
        response = requests.get("http://127.0.0.1:5003/api/teams", timeout=3)
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        if cors_header:
            print(f"    ✓ PASS: CORS enabled: {cors_header}")
            tests_passed += 1
        else:
            print(f"    ✗ FAIL: CORS header not found")
            tests_failed += 1
    except Exception as e:
        print(f"    ✗ FAIL: {e}")
        tests_failed += 1
    
    # Test 5: React Dev Server
    print("\n[5/5] Testing React dev server...")
    try:
        response = requests.get("http://localhost:3000", timeout=3)
        if response.status_code == 200:
            if "H.C. Lombardo" in response.text or "root" in response.text:
                print(f"    ✓ PASS: React app responding")
                tests_passed += 1
            else:
                print(f"    ✗ FAIL: Unexpected content")
                tests_failed += 1
        else:
            print(f"    ✗ FAIL: Status code {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"    ✗ FAIL: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Passed: {tests_passed}/5")
    print(f"Tests Failed: {tests_failed}/5")
    
    if tests_passed == 5:
        print("\n🎉 ALL TESTS PASSED! Integration is fully functional.")
        print("\n✅ React Frontend: http://localhost:3000")
        print("✅ Flask Backend: http://127.0.0.1:5003")
        print("✅ PostgreSQL: nfl_analytics database")
        print("\n" + "=" * 70)
        return 0
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Check server status.")
        print("\n" + "=" * 70)
        return 1

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Installing requests library...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    sys.exit(test_integration())
