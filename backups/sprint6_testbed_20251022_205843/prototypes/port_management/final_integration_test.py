"""
Final Integration Test - Simulate Real Production Scenario
==========================================================
Test the complete workflow before moving to production.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_scenario_1_clean_start():
    """Scenario 1: Clean start, no conflicts"""
    print("\n" + "=" * 70)
    print("SCENARIO 1: Clean Start (No Conflicts)")
    print("=" * 70)
    
    from port_manager import PortManager
    pm = PortManager()
    
    port = pm.get_port_for_service('flask_api')
    print(f"✅ Flask API assigned to port: {port}")
    
    if port == 5000:
        print("✅ Got preferred port 5000")
    else:
        print(f"⚠️  Got alternative port {port}")
    
    print("=" * 70)
    return True

def test_scenario_2_with_database():
    """Scenario 2: Test with actual database connection"""
    print("\n" + "=" * 70)
    print("SCENARIO 2: Database Integration")
    print("=" * 70)
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname='nfl_analytics',
            user='postgres',
            password='aprilv120',
            host='localhost',
            port='5432'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ Database connected: {count} teams in database")
        print("✅ PostgreSQL on port 5432 accessible")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    print("=" * 70)
    return True

def test_scenario_3_flask_api():
    """Scenario 3: Full Flask API test"""
    print("\n" + "=" * 70)
    print("SCENARIO 3: Flask API Functionality")
    print("=" * 70)
    
    from test_full_api import app
    
    with app.test_client() as client:
        # Test all critical endpoints
        endpoints = [
            ('/', 'Home'),
            ('/health', 'Health'),
            ('/port-status', 'Port Status'),
            ('/api/teams', 'Teams List'),
            ('/api/teams/count', 'Team Count'),
            ('/api/teams/DET', 'Detroit Lions')
        ]
        
        for endpoint, name in endpoints:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"✅ {name:20} ({endpoint})")
            else:
                print(f"❌ {name:20} ({endpoint}) - Status {response.status_code}")
                return False
    
    print("=" * 70)
    return True

def test_scenario_4_port_diagnostics():
    """Scenario 4: Port diagnostics and monitoring"""
    print("\n" + "=" * 70)
    print("SCENARIO 4: Port Diagnostics")
    print("=" * 70)
    
    from port_manager import PortManager
    pm = PortManager()
    
    # Get port status
    status = pm.get_port_status()
    print(f"Port Range: {status['range']}")
    print(f"Total Ports: {status['total_ports']}")
    print(f"Available: {status['available']}")
    print(f"In Use: {status['in_use']}")
    
    # Check conflicts
    conflicts = pm.diagnose_port_conflicts()
    print(f"\nConflicts Detected: {len(conflicts)}")
    for conflict in conflicts:
        severity = "🔴" if conflict['severity'] == 'critical' else "🟡"
        print(f"  {severity} {conflict['service']} on port {conflict['port']}")
    
    # Verify we can get ports for all services
    print("\nService Port Assignments:")
    for service_name in ['flask_api', 'react_dev', 'postgresql']:
        try:
            port = pm.get_port_for_service(service_name)
            print(f"  ✅ {service_name:15} → port {port}")
        except Exception as e:
            print(f"  ❌ {service_name:15} → ERROR: {e}")
    
    print("=" * 70)
    return True

def run_all_scenarios():
    """Run complete test suite"""
    print("\n" + "=" * 70)
    print("TESTBED - FINAL INTEGRATION TEST SUITE")
    print("Testing all scenarios before production deployment")
    print("=" * 70)
    
    scenarios = [
        ("Clean Start", test_scenario_1_clean_start),
        ("Database Integration", test_scenario_2_with_database),
        ("Flask API", test_scenario_3_flask_api),
        ("Port Diagnostics", test_scenario_4_port_diagnostics)
    ]
    
    results = []
    for name, test_func in scenarios:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ {name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("=" * 70)
    if all_passed:
        print("✅ ALL SCENARIOS PASSED - READY FOR PRODUCTION DEPLOYMENT")
        print("\nNext Steps:")
        print("1. Copy port_manager.py to production directory")
        print("2. Update production api_server.py to use PortManager")
        print("3. Update production React startup to check ports")
        print("4. Document the port management system")
    else:
        print("❌ SOME TESTS FAILED - FIX ISSUES BEFORE PRODUCTION")
    print("=" * 70 + "\n")
    
    return all_passed

if __name__ == '__main__':
    success = run_all_scenarios()
    sys.exit(0 if success else 1)
