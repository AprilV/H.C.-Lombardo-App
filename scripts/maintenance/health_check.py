"""
Health Check Module - Verifies service availability with retries
Tests database, API endpoints, and React frontend
"""
import requests
import psycopg2
import time
from typing import Dict, Tuple

class HealthChecker:
    """Performs health checks on all system components"""
    
    def __init__(self, max_retries=10, retry_delay=2):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.results = {}
    
    def check_database(self, retries=5) -> Tuple[bool, str]:
        """Check PostgreSQL database connectivity"""
        print(f"\n🔍 Checking Database Connection...")
        
        for attempt in range(1, retries + 1):
            try:
                conn = psycopg2.connect(
                    host='localhost',
                    port=5432,
                    database='nfl_analytics',
                    user='postgres',
                    password='aprilv120',
                    connect_timeout=3
                )
                
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM teams;")
                count = cursor.fetchone()[0]
                conn.close()
                
                print(f"   ✅ Database connected: {count} teams found")
                return True, f"Connected ({count} teams)"
                
            except Exception as e:
                if attempt < retries:
                    print(f"   ⏳ Attempt {attempt}/{retries} failed, retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"   ❌ Database connection failed: {str(e)}")
                    return False, f"Failed: {str(e)}"
        
        return False, "Max retries exceeded"
    
    def check_api_endpoint(self, url: str, endpoint_name: str, retries=None) -> Tuple[bool, str]:
        """Check if API endpoint is responding"""
        if retries is None:
            retries = self.max_retries
            
        print(f"\n🔍 Checking {endpoint_name}...")
        
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(url, timeout=3)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ {endpoint_name} responding (Status: {response.status_code})")
                    return True, f"HTTP {response.status_code}"
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                if attempt < retries:
                    print(f"   ⏳ Attempt {attempt}/{retries}: Service not ready, waiting {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"   ❌ {endpoint_name} not responding after {retries} attempts")
                    return False, "Connection refused"
                    
            except Exception as e:
                if attempt < retries:
                    print(f"   ⏳ Attempt {attempt}/{retries} failed: {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"   ❌ {endpoint_name} failed: {str(e)}")
                    return False, str(e)
        
        return False, "Max retries exceeded"
    
    def check_api_health(self) -> Tuple[bool, str]:
        """Check API /health endpoint"""
        return self.check_api_endpoint(
            "http://127.0.0.1:5000/health",
            "API Health Endpoint"
        )
    
    def check_api_teams(self) -> Tuple[bool, str]:
        """Check API /api/teams endpoint"""
        success, msg = self.check_api_endpoint(
            "http://127.0.0.1:5000/api/teams",
            "API Teams Endpoint"
        )
        
        if success:
            # Verify data structure
            try:
                response = requests.get("http://127.0.0.1:5000/api/teams", timeout=3)
                data = response.json()
                if 'teams' in data and len(data['teams']) > 0:
                    print(f"   📊 Teams data verified: {len(data['teams'])} teams")
                    return True, f"{len(data['teams'])} teams available"
            except:
                pass
        
        return success, msg
    
    def check_react_frontend(self) -> Tuple[bool, str]:
        """Check React dev server"""
        return self.check_api_endpoint(
            "http://localhost:3000",
            "React Frontend",
            retries=15  # React takes longer to start
        )
    
    def run_all_checks(self) -> Dict[str, Tuple[bool, str]]:
        """Run all health checks and return results"""
        print("\n" + "="*70)
        print("🏥 SYSTEM HEALTH CHECK")
        print("="*70)
        
        checks = {
            'database': self.check_database(),
            'api_health': self.check_api_health(),
            'api_teams': self.check_api_teams(),
            'react_frontend': self.check_react_frontend()
        }
        
        print("\n" + "="*70)
        print("📋 HEALTH CHECK SUMMARY")
        print("="*70)
        
        all_passed = True
        for component, (status, message) in checks.items():
            icon = "✅" if status else "❌"
            print(f"{icon} {component.replace('_', ' ').title():20s}: {message}")
            if not status:
                all_passed = False
        
        print("="*70)
        
        if all_passed:
            print("✅ ALL SYSTEMS OPERATIONAL\n")
        else:
            print("❌ SOME SYSTEMS FAILED - CHECK LOGS\n")
        
        return checks

def wait_for_service(service_name: str, check_function, timeout=60) -> bool:
    """
    Wait for a service to become available
    
    Args:
        service_name: Name of service for logging
        check_function: Function that returns (bool, str) tuple
        timeout: Maximum seconds to wait
    
    Returns:
        True if service becomes available, False if timeout
    """
    print(f"\n⏳ Waiting for {service_name} to become available...")
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        success, msg = check_function()
        if success:
            elapsed = time.time() - start_time
            print(f"✅ {service_name} ready after {elapsed:.1f}s")
            return True
        time.sleep(2)
    
    print(f"❌ {service_name} failed to start within {timeout}s")
    return False

if __name__ == "__main__":
    checker = HealthChecker(max_retries=10, retry_delay=2)
    results = checker.run_all_checks()
    
    # Exit with error code if any checks failed
    if not all(status for status, _ in results.values()):
        exit(1)
    
    exit(0)
