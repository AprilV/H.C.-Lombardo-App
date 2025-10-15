"""
Production Startup Manager
Orchestrates sequential startup with health checks and retries
"""
import subprocess
import time
import os
import sys
from pathlib import Path
from health_check import HealthChecker, wait_for_service
from live_data_updater import LiveDataUpdater

class StartupManager:
    """Manages sequential startup of all system components"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.processes = {}
        self.health_checker = HealthChecker(max_retries=10, retry_delay=2)
    
    def check_prerequisites(self) -> bool:
        """Check that all prerequisites are met"""
        print("\n" + "="*70)
        print("🔍 CHECKING PREREQUISITES")
        print("="*70)
        
        checks = []
        
        # Check database
        print("\n1️⃣ Checking PostgreSQL database...")
        db_ok, db_msg = self.health_checker.check_database(retries=3)
        if db_ok:
            print(f"   ✅ Database ready: {db_msg}")
        else:
            print(f"   ❌ Database not available: {db_msg}")
            print("   💡 Make sure PostgreSQL is running")
        checks.append(db_ok)
        
        # Check Python dependencies
        print("\n2️⃣ Checking Python dependencies...")
        try:
            import flask
            import psycopg2
            import requests
            print("   ✅ Python dependencies installed")
            checks.append(True)
        except ImportError as e:
            print(f"   ❌ Missing Python package: {e}")
            checks.append(False)
        
        # Check Node/npm
        print("\n3️⃣ Checking Node.js and npm...")
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True  # Windows needs shell=True for npm
            )
            if result.returncode == 0:
                print(f"   ✅ npm version: {result.stdout.strip()}")
                checks.append(True)
            else:
                print("   ❌ npm not working properly")
                checks.append(False)
        except Exception as e:
            print(f"   ❌ npm not found: {e}")
            print("   💡 This is OK - React may already be running")
            checks.append(True)  # Don't fail startup if npm check fails
        
        # Check if ports are free
        print("\n4️⃣ Checking if ports are available...")
        import socket
        ports_ok = True
        for port, service in [(5000, "API"), (3000, "React")]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"   ⚠️  Port {port} ({service}) is already in use")
                print(f"      Will attempt to use existing service")
            else:
                print(f"   ✅ Port {port} ({service}) is available")
        
        checks.append(True)  # Don't fail on port check, we'll handle it
        
        print("\n" + "="*70)
        
        if all(checks):
            print("✅ ALL PREREQUISITES MET")
            return True
        else:
            print("❌ PREREQUISITES NOT MET - Cannot continue")
            return False
    
    def update_live_data(self) -> bool:
        """Update database with latest NFL data"""
        print("\n" + "="*70)
        print("📊 UPDATING NFL DATA")
        print("="*70)
        
        updater = LiveDataUpdater()
        success = updater.run_update()
        
        if not success:
            print("\n⚠️  Warning: Could not fetch latest data from ESPN")
            print("   Continuing with existing database data...")
        
        return True  # Don't fail startup if ESPN is down
    
    def start_api_server(self) -> bool:
        """Start Flask API server"""
        print("\n" + "="*70)
        print("🚀 STARTING API SERVER")
        print("="*70)
        
        # Check if already running
        print("\n🔍 Checking if API is already running...")
        already_running, msg = self.health_checker.check_api_health()
        
        if already_running:
            print("   ℹ️  API server already running, using existing instance")
            return True
        
        print("   Starting new API server instance...")
        
        try:
            api_script = self.project_root / "api_server.py"
            
            # Start API server in new window
            process = subprocess.Popen(
                ["powershell", "-NoExit", "-Command",
                 f"cd '{self.project_root}' ; "
                 f"Write-Host '🚀 API SERVER' -ForegroundColor Green ; "
                 f"python api_server.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.processes['api'] = process
            print(f"   🔄 Process started (PID: {process.pid})")
            
            # Wait for API to be ready
            print("\n⏳ Waiting for API server to become ready...")
            success = wait_for_service(
                "API Server",
                self.health_checker.check_api_health,
                timeout=30
            )
            
            if success:
                # Verify teams endpoint
                teams_ok, teams_msg = self.health_checker.check_api_teams()
                if teams_ok:
                    print(f"   ✅ API fully operational: {teams_msg}")
                    return True
                else:
                    print(f"   ⚠️  API started but teams endpoint failed: {teams_msg}")
                    return False
            else:
                print("   ❌ API server failed to start within timeout")
                return False
                
        except Exception as e:
            print(f"   ❌ Failed to start API server: {str(e)}")
            return False
    
    def start_react_frontend(self) -> bool:
        """Start React development server"""
        print("\n" + "="*70)
        print("🎨 STARTING REACT FRONTEND")
        print("="*70)
        
        # Check if already running
        print("\n🔍 Checking if React is already running...")
        already_running, msg = self.health_checker.check_react_frontend()
        
        if already_running:
            print("   ℹ️  React server already running, using existing instance")
            return True
        
        print("   Starting new React server instance...")
        
        try:
            frontend_dir = self.project_root / "frontend"
            
            # Start React dev server in new window
            process = subprocess.Popen(
                ["powershell", "-NoExit", "-Command",
                 f"cd '{frontend_dir}' ; "
                 f"Write-Host '🎨 REACT FRONTEND' -ForegroundColor Cyan ; "
                 f"npm start"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.processes['react'] = process
            print(f"   🔄 Process started (PID: {process.pid})")
            
            # Wait for React to be ready (takes longer)
            print("\n⏳ Waiting for React server to compile and start...")
            print("   (This may take 15-30 seconds on first run)")
            success = wait_for_service(
                "React Frontend",
                self.health_checker.check_react_frontend,
                timeout=60
            )
            
            if success:
                print("   ✅ React frontend ready")
                return True
            else:
                print("   ❌ React frontend failed to start within timeout")
                return False
                
        except Exception as e:
            print(f"   ❌ Failed to start React frontend: {str(e)}")
            return False
    
    def open_browser(self):
        """Open React app in default browser"""
        print("\n🌐 Opening application in browser...")
        try:
            subprocess.Popen(["start", "http://localhost:3000"], shell=True)
            print("   ✅ Browser opened to http://localhost:3000")
        except Exception as e:
            print(f"   ⚠️  Could not open browser automatically: {e}")
            print("   💡 Please open http://localhost:3000 manually")
    
    def run_startup_sequence(self) -> bool:
        """Run complete startup sequence"""
        print("\n")
        print("="*70)
        print("🏈 H.C. LOMBARDO APP - PRODUCTION STARTUP")
        print("="*70)
        
        # Step 1: Prerequisites
        if not self.check_prerequisites():
            print("\n❌ Startup aborted due to prerequisite failures")
            return False
        
        # Step 2: Update live data
        self.update_live_data()
        
        # Step 3: Start API server
        if not self.start_api_server():
            print("\n❌ Startup aborted: API server failed to start")
            return False
        
        # Step 4: Start React frontend
        if not self.start_react_frontend():
            print("\n❌ Startup aborted: React frontend failed to start")
            return False
        
        # Step 5: Final health check
        print("\n" + "="*70)
        print("🏥 FINAL SYSTEM HEALTH CHECK")
        print("="*70)
        
        results = self.health_checker.run_all_checks()
        all_healthy = all(status for status, _ in results.values())
        
        if all_healthy:
            print("\n" + "="*70)
            print("✅ STARTUP COMPLETE - ALL SYSTEMS OPERATIONAL")
            print("="*70)
            print("\n📍 Access Points:")
            print("   • React Frontend: http://localhost:3000")
            print("   • API Server:     http://localhost:5000")
            print("   • API Health:     http://localhost:5000/health")
            print("\n💡 The system will automatically fetch live NFL data")
            print("   To shutdown: Close the terminal windows or run shutdown.py")
            print("\n")
            
            # Open browser
            self.open_browser()
            
            return True
        else:
            print("\n❌ STARTUP COMPLETED WITH ERRORS")
            print("   Some services may not be functioning correctly")
            return False

def main():
    # Get project root (2 levels up from testbed/production_system)
    project_root = Path(__file__).parent.parent.parent
    
    manager = StartupManager(str(project_root))
    success = manager.run_startup_sequence()
    
    if success:
        print("\n⏸️  Press Ctrl+C to exit (servers will keep running)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 Exiting startup manager (servers still running)")
            print("   Use shutdown.py to stop all services")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
