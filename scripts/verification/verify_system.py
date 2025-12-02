"""
System Verification Script
Checks if everything is actually working
"""
import psycopg2
from db_config import DATABASE_CONFIG
from datetime import datetime
import sys

def verify_database():
    """Check database connection and data freshness"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        
        # Check team count
        cur.execute('SELECT COUNT(*) FROM teams')
        team_count = cur.fetchone()[0]
        
        # Check data freshness
        cur.execute('SELECT MAX(last_updated) FROM teams')
        last_update = cur.fetchone()[0]
        
        # Calculate age
        time_diff = datetime.now() - last_update
        minutes_old = time_diff.total_seconds() / 60
        
        print(f"✅ Database Connected")
        print(f"   Teams: {team_count}/32")
        print(f"   Last Update: {last_update}")
        print(f"   Data Age: {minutes_old:.1f} minutes")
        
        if minutes_old > 30:
            print(f"   ⚠️  WARNING: Data is stale (>{minutes_old:.0f} min old)")
            return False
        else:
            print(f"   ✅ Data is fresh")
            return True
            
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def verify_processes():
    """Check if required processes are running"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-Process python* -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        count = int(result.stdout.strip() or 0)
        print(f"\n🖥️  Python Processes Running: {count}")
        
        if count == 0:
            print(f"   ⚠️  WARNING: No updater or API server running")
            return False
        else:
            # Get details
            details = subprocess.run(
                ['powershell', '-Command',
                 "Get-Process python* -ErrorAction SilentlyContinue | ForEach-Object { (Get-CimInstance Win32_Process -Filter \"ProcessId = $($_.Id)\").CommandLine }"],
                capture_output=True,
                text=True,
                timeout=5
            )
            for line in details.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   - {line.strip()}")
            return True
            
    except Exception as e:
        print(f"❌ Process Check Error: {e}")
        return False

def main():
    print("=" * 60)
    print("H.C. LOMBARDO SYSTEM VERIFICATION")
    print(f"Time: {datetime.now()}")
    print("=" * 60)
    
    db_ok = verify_database()
    proc_ok = verify_processes()
    
    print("\n" + "=" * 60)
    if db_ok and proc_ok:
        print("✅ SYSTEM STATUS: HEALTHY")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ SYSTEM STATUS: ISSUES DETECTED")
        print("=" * 60)
        print("\nRecommended actions:")
        if not proc_ok:
            print("  1. Run: .\\START.bat")
        if not db_ok:
            print("  2. Run: python multi_source_data_fetcher.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
