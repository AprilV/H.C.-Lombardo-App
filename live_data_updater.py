"""
Live Data Updater - Fetches fresh NFL data from multiple sources
Uses multi-source aggregation for complete, accurate data
Runs on schedule or on-demand to keep database current
"""
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

class LiveDataUpdater:
    """Fetches and updates NFL data using multi-source approach"""
    
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent
        self.repo_root = self._resolve_repo_root()

    def _resolve_repo_root(self) -> Path:
        """Resolve repository root for consistent script lookup and execution."""
        if (self.project_root / "api_server.py").exists():
            return self.project_root

        candidate = self.project_root.parent.parent
        if (candidate / "api_server.py").exists():
            return candidate

        return self.project_root

    def _fetcher_candidates(self):
        return [
            self.repo_root / "multi_source_data_fetcher.py",
            self.repo_root / "scripts" / "maintenance" / "multi_source_data_fetcher.py",
            self.project_root / "multi_source_data_fetcher.py",
        ]

    def _resolve_fetcher_script(self):
        for candidate in self._fetcher_candidates():
            if candidate.exists():
                return candidate
        return None
    
    def run_update(self) -> bool:
        """Run multi-source data update"""
        print("\n" + "="*70)
        print(f"LIVE DATA UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        try:
            # Run the multi-source data fetcher
            fetcher_script = self._resolve_fetcher_script()
            
            if not fetcher_script:
                print("\n[ERROR] Multi-source fetcher not found. Checked:")
                for candidate in self._fetcher_candidates():
                    print(f"   - {candidate}")
                return False
            
            result = subprocess.run(
                [sys.executable, str(fetcher_script)],
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
                timeout=60
            )
            
            # Print output (but suppress the duplicate headers)
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                # Skip the first header lines since we print our own
                output_lines = [line for line in lines if not line.startswith('===')]
                if output_lines:
                    print('\n'.join(output_lines))
            
            if result.returncode == 0:
                print("\n" + "="*70)
                print("LIVE DATA UPDATE COMPLETE")
                print("="*70 + "\n")
                return True
            else:
                print(f"\n[ERROR] Update failed with code {result.returncode}")
                if result.stderr:
                    print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("\n[ERROR] Update timed out after 60 seconds")
            return False
        except Exception as e:
            print(f"\n[ERROR] Update error: {e}")
            return False
    
    def run_continuous(self, interval_minutes: int = 15):
        """Run continuous updates at specified interval"""
        print(f"\n[CONTINUOUS] Starting updates (every {interval_minutes} minutes)")
        print("   Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_update()
                
                print(f"\n[WAITING] Next update in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n\n[STOPPED] Continuous updates stopped by user")

if __name__ == "__main__":
    updater = LiveDataUpdater()
    
    # Check for continuous mode
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        updater.run_continuous(interval)
    else:
        success = updater.run_update()
        sys.exit(0 if success else 1)
