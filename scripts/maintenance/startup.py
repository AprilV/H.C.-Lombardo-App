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
    
    def ensure_database_schema(self) -> bool:
        """Ensure database has proper schema with unique constraints"""
        print("\n" + "="*70)
        print("🗄️  CHECKING DATABASE SCHEMA")
        print("="*70)
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'nfl_analytics'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'aprilv120')
            )
            cursor = conn.cursor()
            
            # Check if teams table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'teams'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                print("   ℹ️  Teams table doesn't exist, will be created by loader")
            else:
                # Check for unique constraint
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM pg_constraint
                    WHERE conname = 'teams_abbreviation_key'
                    AND conrelid = 'teams'::regclass;
                """)
                constraint_exists = cursor.fetchone()[0] > 0
                
                if not constraint_exists:
                    print("   🔧 Adding UNIQUE constraint on abbreviation...")
                    try:
                        cursor.execute("""
                            ALTER TABLE teams 
                            ADD CONSTRAINT teams_abbreviation_key 
                            UNIQUE (abbreviation);
                        """)
                        conn.commit()
                        print("   ✅ Unique constraint added")
                    except psycopg2.errors.UniqueViolation:
                        conn.rollback()
                        print("   ⚠️  Duplicate abbreviations found, cleaning up...")
                        # Remove duplicates keeping the first occurrence
                        cursor.execute("""
                            DELETE FROM teams a USING teams b
                            WHERE a.id > b.id 
                            AND a.abbreviation = b.abbreviation;
                        """)
                        conn.commit()
                        print("   ✅ Duplicates removed, adding constraint...")
                        cursor.execute("""
                            ALTER TABLE teams 
                            ADD CONSTRAINT teams_abbreviation_key 
                            UNIQUE (abbreviation);
                        """)
                        conn.commit()
                        print("   ✅ Unique constraint added")
                else:
                    print("   ✅ Schema is properly configured")
                
                # Count teams
                cursor.execute("SELECT COUNT(*) FROM teams")
                team_count = cursor.fetchone()[0]
                print(f"   📊 Database contains {team_count} teams")
                
                if team_count != 32:
                    print(f"   ⚠️  Expected 32 teams, found {team_count}")
            
            conn.close()
            print("   ✅ Database schema check complete")
            return True
            
        except Exception as e:
            print(f"   ❌ Database schema check failed: {e}")
            return True  # Don't fail startup, data loader will handle it
    
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
        
        # Check if port 5000 is available
        import socket
        print("\n🔍 Checking if port 5000 is available...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_in_use = sock.connect_ex(('127.0.0.1', 5000)) == 0
        sock.close()
        
        if port_in_use:
            print("   ⚠️  Port 5000 is already in use")
            print("   🔍 Checking if it's our API server...")
            already_running, msg = self.health_checker.check_api_endpoint(
                "http://127.0.0.1:5000/health",
                "API Server",
                retries=1
            )
            
            if already_running:
                print("   ✅ API server already running, using existing instance")
                return True
            else:
                print("   ❌ Port 5000 occupied by another process")
                print("   💡 Run shutdown.py first or kill the process using port 5000")
                return False
        
        print("   ✅ Port 5000 is available")
        print("   Starting new API server instance...")
        
        try:
            api_script = self.project_root / "api_server.py"
            
            if not api_script.exists():
                print(f"   ❌ API script not found: {api_script}")
                return False
            
            # Start API server in new window with full path
            process = subprocess.Popen(
                ["powershell", "-NoExit", "-Command",
                 f"cd '{self.project_root}' ; "
                 f"Write-Host 'API SERVER - {self.project_root}' -ForegroundColor Green ; "
                 f"python '{api_script}'"],
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
    
    def start_auto_update_service(self) -> bool:
        """Start automated data update service"""
        print("\n" + "="*70)
        print("🤖 STARTING AUTO-UPDATE SERVICE")
        print("="*70)
        
        try:
            auto_update_script = self.project_root / "auto_update_service.py"
            
            if not auto_update_script.exists():
                print(f"   ⚠️  Auto-update script not found: {auto_update_script}")
                print("   Skipping auto-updates (you can run manually)")
                return True  # Don't fail startup
            
            # Start auto-update service in new window (15 min interval)
            process = subprocess.Popen(
                ["powershell", "-NoExit", "-Command",
                 f"cd '{self.project_root}' ; "
                 f"Write-Host 'AUTO-UPDATE SERVICE - Updates every 15 minutes' -ForegroundColor Yellow ; "
                 f"python '{auto_update_script}' --continuous 15"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.processes['auto_update'] = process
            print(f"   ✅ Auto-update service started (PID: {process.pid})")
            print("   📅 Will update NFL data every 15 minutes")
            print("   💡 Close the auto-update window to stop")
            return True
                
        except Exception as e:
            print(f"   ⚠️  Could not start auto-update service: {str(e)}")
            print("   Continuing without auto-updates")
            return True  # Don't fail startup
    
    def start_react_frontend(self) -> bool:
        """Start React development server"""
        print("\n" + "="*70)
        print("🎨 STARTING REACT FRONTEND")
        print("="*70)
        
        # Check if port 3000 is available
        import socket
        print("\n🔍 Checking if port 3000 is available...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_in_use = sock.connect_ex(('127.0.0.1', 3000)) == 0
        sock.close()
        
        if port_in_use:
            print("   ⚠️  Port 3000 is already in use")
            print("   🔍 Checking if it's our React server...")
            already_running, msg = self.health_checker.check_react_frontend()
            
            if already_running:
                print("   ✅ React server already running, using existing instance")
                return True
            else:
                print("   ❌ Port 3000 occupied by another process")
                print("   💡 Run shutdown.py first or kill the process using port 3000")
                return False
        
        print("   ✅ Port 3000 is available")
        print("   Starting new React server instance...")
        
        try:
            frontend_dir = self.project_root / "frontend"
            
            if not frontend_dir.exists():
                print(f"   ❌ Frontend directory not found: {frontend_dir}")
                return False
            
            # Start React dev server in new window with full path
            process = subprocess.Popen(
                ["powershell", "-NoExit", "-Command",
                 f"cd '{frontend_dir}' ; "
                 f"Write-Host 'REACT FRONTEND - {frontend_dir}' -ForegroundColor Cyan ; "
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
        print("H.C. LOMBARDO APP - PRODUCTION STARTUP")
        print("="*70)
        
        # Step 1: Prerequisites
        if not self.check_prerequisites():
            print("\n❌ Startup aborted due to prerequisite failures")
            return False
        
        # Step 2: Ensure database schema
        if not self.ensure_database_schema():
            print("\n⚠️  Database schema check had issues, but continuing...")
        
        # Step 3: Update live data
        self.update_live_data()
        
        # Step 4: Start auto-update service (background)
        self.start_auto_update_service()
        
        # Step 5: Start API server
        if not self.start_api_server():
            print("\n❌ Startup aborted: API server failed to start")
            return False
        
        # Step 6: Start React frontend
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
            print("\n🤖 Auto-Update Service:")
            print("   • Updates NFL data every 15 minutes automatically")
            print("   • Runs in background window (close window to stop)")
            print("\n💡 To shutdown: Close the terminal windows or run shutdown.py")
            print("\n")
            
            # Open browser
            self.open_browser()
            
            return True
        else:
            print("\n❌ STARTUP COMPLETED WITH ERRORS")
            print("   Some services may not be functioning correctly")
            return False

def main():
    # Get project root (script is in project root now)
    project_root = Path(__file__).parent
    
    print(f"📁 Project root: {project_root}")
    
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
