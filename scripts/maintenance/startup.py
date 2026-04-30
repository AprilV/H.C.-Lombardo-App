"""
Production Startup Manager
Orchestrates sequential startup with health checks and retries
"""
import subprocess
import time
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Ensure both scripts/maintenance and project root are on the path
_HERE = Path(__file__).parent
_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_ROOT))

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
        print("[CHECK] CHECKING PREREQUISITES")
        print("="*70)
        
        checks = []
        
        # Check database
        print("\n1. Checking PostgreSQL database...")
        db_ok, db_msg = self.health_checker.check_database(retries=3)
        if db_ok:
            print(f"   [OK] Database ready: {db_msg}")
        else:
            print(f"   [ERROR] Database not available: {db_msg}")
            print("   >> Make sure PostgreSQL is running")
        checks.append(db_ok)
        
        # Check Python dependencies
        print("\n2. Checking Python dependencies...")
        try:
            import flask
            import psycopg2
            import requests
            print("   [OK] Python dependencies installed")
            checks.append(True)
        except ImportError as e:
            print(f"   [ERROR] Missing Python package: {e}")
            checks.append(False)
        
        # Check Node/npm
        print("\n3. Checking Node.js and npm...")
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True  # Windows needs shell=True for npm
            )
            if result.returncode == 0:
                print(f"   [OK] npm version: {result.stdout.strip()}")
                checks.append(True)
            else:
                print("   [ERROR] npm not working properly")
                checks.append(False)
        except Exception as e:
            print(f"   [ERROR] npm not found: {e}")
            print("   >> This is OK - React may already be running")
            checks.append(True)  # Don't fail startup if npm check fails
        
        # Check if ports are free
        print("\n4. Checking if ports are available...")
        import socket
        ports_ok = True
        for port, service in [(5000, "API"), (3000, "React")]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"   [WARN]  Port {port} ({service}) is already in use")
                print(f"      Will attempt to use existing service")
            else:
                print(f"   [OK] Port {port} ({service}) is available")
        
        checks.append(True)  # Don't fail on port check, we'll handle it
        
        print("\n" + "="*70)
        
        if all(checks):
            print("[OK] ALL PREREQUISITES MET")
            return True
        else:
            print("[ERROR] PREREQUISITES NOT MET - Cannot continue")
            return False
    
    def ensure_database_schema(self) -> bool:
        """Ensure database has proper schema with unique constraints"""
        print("\n" + "="*70)
        print("[DB]  CHECKING DATABASE SCHEMA")
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
                print("   [INFO]  Teams table doesn't exist, will be created by loader")
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
                    print("   [FIX] Adding UNIQUE constraint on abbreviation...")
                    try:
                        cursor.execute("""
                            ALTER TABLE teams 
                            ADD CONSTRAINT teams_abbreviation_key 
                            UNIQUE (abbreviation);
                        """)
                        conn.commit()
                        print("   [OK] Unique constraint added")
                    except psycopg2.errors.UniqueViolation:
                        conn.rollback()
                        print("   [WARN]  Duplicate abbreviations found, cleaning up...")
                        # Remove duplicates keeping the first occurrence
                        cursor.execute("""
                            DELETE FROM teams a USING teams b
                            WHERE a.id > b.id 
                            AND a.abbreviation = b.abbreviation;
                        """)
                        conn.commit()
                        print("   [OK] Duplicates removed, adding constraint...")
                        cursor.execute("""
                            ALTER TABLE teams 
                            ADD CONSTRAINT teams_abbreviation_key 
                            UNIQUE (abbreviation);
                        """)
                        conn.commit()
                        print("   [OK] Unique constraint added")
                else:
                    print("   [OK] Schema is properly configured")
                
                # Count teams
                cursor.execute("SELECT COUNT(*) FROM teams")
                team_count = cursor.fetchone()[0]
                print(f"   [DATA] Database contains {team_count} teams")
                
                if team_count != 32:
                    print(f"   [WARN]  Expected 32 teams, found {team_count}")
            
            conn.close()
            print("   [OK] Database schema check complete")
            return True
            
        except Exception as e:
            print(f"   [ERROR] Database schema check failed: {e}")
            return True  # Don't fail startup, data loader will handle it
    
    def update_live_data(self) -> bool:
        """Update database with latest NFL data"""
        print("\n" + "="*70)
        print("[DATA] UPDATING NFL DATA")
        print("="*70)
        
        updater = LiveDataUpdater()
        success = updater.run_update()
        
        if not success:
            print("\n[WARN]  Warning: Could not fetch latest data from ESPN")
            print("   Continuing with existing database data...")
        
        return True  # Don't fail startup if ESPN is down
    
    def start_api_server(self) -> bool:
        """Start Flask API server"""
        print("\n" + "="*70)
        print("[START] STARTING API SERVER")
        print("="*70)
        
        # Check if port 5000 is available
        import socket
        print("\n[CHECK] Checking if port 5000 is available...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_in_use = sock.connect_ex(('127.0.0.1', 5000)) == 0
        sock.close()
        
        if port_in_use:
            print("   [WARN]  Port 5000 is already in use")
            print("   [CHECK] Checking if it's our API server...")
            already_running, msg = self.health_checker.check_api_endpoint(
                "http://127.0.0.1:5000/health",
                "API Server",
                retries=1
            )
            
            if already_running:
                print("   [OK] API server already running, using existing instance")
                return True
            else:
                print("   [ERROR] Port 5000 occupied by another process")
                print("   >> Run shutdown.py first or kill the process using port 5000")
                return False
        
        print("   [OK] Port 5000 is available")
        print("   Starting new API server instance...")
        
        try:
            api_script = self.project_root / "api_server.py"
            
            if not api_script.exists():
                print(f"   [ERROR] API script not found: {api_script}")
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
            print(f"   [STARTING] Process started (PID: {process.pid})")
            
            # Wait for API to be ready
            print("\n[WAIT] Waiting for API server to become ready...")
            success = wait_for_service(
                "API Server",
                self.health_checker.check_api_health,
                timeout=30
            )
            
            if success:
                # Verify teams endpoint
                teams_ok, teams_msg = self.health_checker.check_api_teams()
                if teams_ok:
                    print(f"   [OK] API fully operational: {teams_msg}")
                    return True
                else:
                    print(f"   [WARN]  API started but teams endpoint failed: {teams_msg}")
                    return False
            else:
                print("   [ERROR] API server failed to start within timeout")
                return False
                
        except Exception as e:
            print(f"   [ERROR] Failed to start API server: {str(e)}")
            return False
    
    def start_auto_update_service(self) -> bool:
        """Start automated data update service"""
        print("\n" + "="*70)
        print("[AUTO] STARTING AUTO-UPDATE SERVICE")
        print("="*70)
        
        try:
            auto_update_script = self.project_root / "auto_update_service.py"
            
            if not auto_update_script.exists():
                print(f"   [WARN]  Auto-update script not found: {auto_update_script}")
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
            print(f"   [OK] Auto-update service started (PID: {process.pid})")
            print("   [SCHED] Will update NFL data every 15 minutes")
            print("   >> Close the auto-update window to stop")
            return True
                
        except Exception as e:
            print(f"   [WARN]  Could not start auto-update service: {str(e)}")
            print("   Continuing without auto-updates")
            return True  # Don't fail startup
    
    def start_log_watcher(self) -> bool:
        """Start dev log watcher (file changes + HTTP server on port 8765)"""
        print("\n" + "="*70)
        print("[LOG] STARTING DEV LOG WATCHER")
        print("="*70)

        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_in_use = sock.connect_ex(('127.0.0.1', 8765)) == 0
        sock.close()

        if port_in_use:
            print("   [OK] Log watcher already running on port 8765")
            return True

        try:
            log_script = self.project_root / "log_watcher.py"
            if not log_script.exists():
                print(f"   [WARN]  log_watcher.py not found, skipping")
                return True

            process = subprocess.Popen(
                ["powershell", "-NoExit", "-Command",
                 f"cd '{self.project_root}' ; "
                 f"Write-Host 'DEV LOG WATCHER - http://localhost:8765/' -ForegroundColor Magenta ; "
                 f"python '{log_script}'"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            self.processes['log_watcher'] = process
            print(f"   [STARTING] Process started (PID: {process.pid})")

            print("\n[WAIT] Waiting for log watcher to become ready...")
            success = wait_for_service(
                "Log Watcher",
                lambda: self.health_checker.check_api_endpoint(
                    "http://127.0.0.1:8765/", "Log Watcher", retries=1),
                timeout=15
            )

            if success:
                print("   [OK] Log watcher ready at http://localhost:8765/")
            else:
                print("   [WARN]  Log watcher may not be ready yet (non-critical)")
            return True

        except Exception as e:
            print(f"   [WARN]  Could not start log watcher: {str(e)}")
            return True  # Non-critical, don't fail startup

    def start_react_frontend(self) -> bool:
        """Start React development server"""
        print("\n" + "="*70)
        print("[UI] STARTING REACT FRONTEND")
        print("="*70)
        
        # Check if port 3000 is available
        import socket
        print("\n[CHECK] Checking if port 3000 is available...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_in_use = sock.connect_ex(('127.0.0.1', 3000)) == 0
        sock.close()
        
        if port_in_use:
            print("   [WARN]  Port 3000 is already in use")
            print("   [CHECK] Checking if it's our React server...")
            already_running, msg = self.health_checker.check_react_frontend()
            
            if already_running:
                print("   [OK] React server already running, using existing instance")
                return True
            else:
                print("   [ERROR] Port 3000 occupied by another process")
                print("   >> Run shutdown.py first or kill the process using port 3000")
                return False
        
        print("   [OK] Port 3000 is available")
        print("   Starting new React server instance...")
        
        try:
            frontend_dir = self.project_root / "frontend"
            
            if not frontend_dir.exists():
                print(f"   [ERROR] Frontend directory not found: {frontend_dir}")
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
            print(f"   [STARTING] Process started (PID: {process.pid})")
            
            # Wait for React to be ready (takes longer)
            print("\n[WAIT] Waiting for React server to compile and start...")
            print("   (This may take 15-30 seconds on first run)")
            success = wait_for_service(
                "React Frontend",
                self.health_checker.check_react_frontend,
                timeout=60
            )
            
            if success:
                print("   [OK] React frontend ready")
                return True
            else:
                print("   [ERROR] React frontend failed to start within timeout")
                return False
                
        except Exception as e:
            print(f"   [ERROR] Failed to start React frontend: {str(e)}")
            return False
    
    def open_browser(self):
        """Open React app in default browser"""
        print("\n[BROWSER] Opening application in browser...")
        try:
            subprocess.Popen(["start", "http://localhost:3000"], shell=True)
            print("   [OK] Browser opened to http://localhost:3000")
        except Exception as e:
            print(f"   [WARN]  Could not open browser automatically: {e}")
            print("   >> Please open http://localhost:3000 manually")
    
    def run_startup_sequence(self) -> bool:
        """Run complete startup sequence"""
        print("\n")
        print("="*70)
        print("H.C. LOMBARDO APP - PRODUCTION STARTUP")
        print("="*70)
        
        # Step 1: Prerequisites
        if not self.check_prerequisites():
            print("\n[ERROR] Startup aborted due to prerequisite failures")
            return False
        
        # Step 2: Ensure database schema
        if not self.ensure_database_schema():
            print("\n[WARN]  Database schema check had issues, but continuing...")
        
        # Step 3: Update live data
        self.update_live_data()
        
        # Step 4: Start auto-update service (background)
        self.start_auto_update_service()
        
        # Step 5: Start API server
        if not self.start_api_server():
            print("\n[ERROR] Startup aborted: API server failed to start")
            return False
        
        # Step 6: Start log watcher
        self.start_log_watcher()

        # Step 7: Start React frontend
        if not self.start_react_frontend():
            print("\n[ERROR] Startup aborted: React frontend failed to start")
            return False
        
        # Step 5: Final health check
        print("\n" + "="*70)
        print("[HEALTH] FINAL SYSTEM HEALTH CHECK")
        print("="*70)
        
        results = self.health_checker.run_all_checks()
        all_healthy = all(status for status, _ in results.values())
        
        if all_healthy:
            print("\n" + "="*70)
            print("[OK] STARTUP COMPLETE - ALL SYSTEMS OPERATIONAL")
            print("="*70)
            print("\n>> Access Points:")
            print("   • React Frontend: http://localhost:3000")
            print("   • API Server:     http://localhost:5000")
            print("   • API Health:     http://localhost:5000/health")
            print("\n[AUTO] Auto-Update Service:")
            print("   • Updates NFL data every 15 minutes automatically")
            print("   • Runs in background window (close window to stop)")
            print("\n>> To shutdown: Close the terminal windows or run shutdown.py")
            print("\n")
            
            # Open browser
            self.open_browser()
            
            return True
        else:
            print("\n[ERROR] STARTUP COMPLETED WITH ERRORS")
            print("   Some services may not be functioning correctly")
            return False

def main():
    # Get project root (script is in project root now)
    project_root = Path(__file__).parent
    
    print(f"[DIR] Project root: {project_root}")
    
    manager = StartupManager(str(project_root))
    success = manager.run_startup_sequence()
    
    if success:
        print("\n[PAUSE]  Press Ctrl+C to exit (servers will keep running)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n[BYE] Exiting startup manager (servers still running)")
            print("   Use shutdown.py to stop all services")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
