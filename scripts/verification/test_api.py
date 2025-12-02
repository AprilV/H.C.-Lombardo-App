"""
Quick API test script to verify endpoints are working
"""
import requests
import time
import json

def test_endpoint(url, name):
    """Test a single endpoint"""
    try:
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"URL: {url}")
        print(f"{'='*60}")
        
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS - Got {len(data) if isinstance(data, list) else 1} records")
            print(f"\nFirst record preview:")
            print(json.dumps(data[0] if isinstance(data, list) else data, indent=2)[:500] + "...")
            return True
        else:
            print(f"✗ FAILED - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ CONNECTION REFUSED - Server not responding")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("H.C. LOMBARDO NFL DASHBOARD API TEST")
    print("Testing production hcl schema endpoints")
    print("="*60)
    
    # Wait a moment for server to be ready
    print("\nWaiting 2 seconds for server...")
    time.sleep(2)
    
    base_url = "http://localhost:5000/api/hcl"
    
    tests = [
        (f"{base_url}/teams?season=2024", "Get all teams (2024)"),
        (f"{base_url}/teams/KC?season=2024", "Get KC team details"),
        (f"{base_url}/teams/KC/games?season=2024&limit=3", "Get KC games with betting data"),
        (f"{base_url}/games/2024_01_BAL_KC", "Get specific game details"),
        (f"{base_url}/games/week/2024/1", "Get all week 1 games"),
    ]
    
    results = []
    for url, name in tests:
        results.append(test_endpoint(url, name))
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print(f"{'='*60}\n")
    
    if all(results):
        print("✓ ALL TESTS PASSED - API is working correctly with production data!")
        print("\nYou can now view the dashboard at:")
        print("http://localhost:5000")
    else:
        print("✗ SOME TESTS FAILED - Check server logs for errors")

if __name__ == '__main__':
    main()
