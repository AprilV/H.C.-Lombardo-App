"""
Continuous Production Testing
Tests all systems every 30 seconds until stopped
"""
import requests
import psycopg2
from db_config import DATABASE_CONFIG
from datetime import datetime
import time
import sys

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Health: {data['status']} | DB: {data['database']} | CORS: {data['cors']}")
            return True
        else:
            print(f"  ❌ Health: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Health: {str(e)[:50]}")
        return False

def test_teams_api():
    """Test teams endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/teams', timeout=5)
        if response.status_code == 200:
            teams = response.json()
            print(f"  ✅ Teams API: {len(teams)} teams loaded")
            return True
        else:
            print(f"  ❌ Teams API: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Teams API: {str(e)[:50]}")
        return False

def test_single_team():
    """Test single team endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/teams/DAL', timeout=5)
        if response.status_code == 200:
            team = response.json()
            print(f"  ✅ Team DAL: {team['wins']}-{team['losses']}-{team['ties']} | PPG: {team['ppg']}")
            return True
        else:
            print(f"  ❌ Team DAL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Team DAL: {str(e)[:50]}")
        return False

def test_database():
    """Test database directly"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        
        cur.execute('SELECT COUNT(*) FROM teams')
        team_count = cur.fetchone()[0]
        
        cur.execute('SELECT MAX(last_updated) FROM teams')
        last_update = cur.fetchone()[0]
        
        time_diff = datetime.now() - last_update
        minutes_old = time_diff.total_seconds() / 60
        
        print(f"  ✅ Database: {team_count}/32 teams | Data age: {minutes_old:.1f} min")
        
        conn.close()
        return True
    except Exception as e:
        print(f"  ❌ Database: {str(e)[:50]}")
        return False

def run_test_cycle():
    """Run one complete test cycle"""
    print(f"\n{'='*60}")
    print(f"🔄 TEST CYCLE - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    results = []
    results.append(test_health())
    results.append(test_teams_api())
    results.append(test_single_team())
    results.append(test_database())
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"\n  ✅ ALL TESTS PASSED ({passed}/{total})")
    else:
        print(f"\n  ⚠️  SOME TESTS FAILED ({passed}/{total})")
    
    return passed == total

def main():
    print("="*60)
    print("🚀 CONTINUOUS PRODUCTION TESTING STARTED")
    print("   Press Ctrl+C to stop")
    print("="*60)
    
    test_count = 0
    pass_count = 0
    
    try:
        while True:
            test_count += 1
            if run_test_cycle():
                pass_count += 1
            
            print(f"\n📊 Summary: {pass_count}/{test_count} cycles passed")
            print(f"⏳ Next test in 30 seconds...\n")
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("🛑 TESTING STOPPED BY USER")
        print("="*60)
        print(f"Final Results: {pass_count}/{test_count} cycles passed")
        print(f"Success Rate: {(pass_count/test_count*100):.1f}%")
        print("="*60)
        sys.exit(0)

if __name__ == "__main__":
    main()
