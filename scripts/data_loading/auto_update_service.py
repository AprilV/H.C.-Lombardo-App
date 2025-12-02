"""
Automated NFL Data Update Service
==================================
Continuously updates game data from nflverse every 15 minutes during NFL season.
Runs in background to keep predictions and scores current.

Usage:
    python auto_update_service.py                    # Run once
    python auto_update_service.py --continuous       # Run every 15 min
    python auto_update_service.py --continuous 5     # Run every 5 min
"""

import sys
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


class AutoUpdateService:
    """Automatic NFL data updater"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ingest_script = project_root / "ingest_historical_games.py"
        self.update_script = project_root / "update_prediction_results.py"
    
    def is_nfl_season(self) -> bool:
        """Check if we're in NFL season (September through February)"""
        now = datetime.now()
        month = now.month
        # NFL season: September (9) through February (2)
        return month >= 9 or month <= 2
    
    def is_game_day(self) -> bool:
        """Check if today is a typical NFL game day"""
        now = datetime.now()
        day_of_week = now.weekday()  # 0=Monday, 6=Sunday
        
        # Thursday (3), Sunday (6), Monday (0) are game days
        # But also run on Tuesday to catch Monday night games
        return day_of_week in [0, 1, 3, 6]
    
    def should_update(self) -> bool:
        """Determine if we should run an update now"""
        # Always update during NFL season on game days
        if self.is_nfl_season() and self.is_game_day():
            return True
        
        # Otherwise, still update but less frequently (handled by interval)
        return True
    
    def run_update_cycle(self) -> bool:
        """Run a complete update cycle: ingest games + update predictions"""
        print("\n" + "="*80)
        print(f"🔄 AUTO UPDATE CYCLE - {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
        print("="*80)
        
        if not self.should_update():
            print("⏸️  Not a game day or outside NFL season - skipping update")
            return True
        
        success = True
        
        # Step 1: Ingest latest game data from nflverse
        print("\n📥 Step 1: Fetching latest game data from nflverse...")
        try:
            result = subprocess.run(
                [sys.executable, str(self.ingest_script), "--production", "--seasons", "2025"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print("   ✅ Game data updated successfully")
                # Show key stats from output
                for line in result.stdout.split('\n'):
                    if 'Inserted' in line or 'games' in line.lower():
                        print(f"   {line.strip()}")
            else:
                print(f"   ⚠️  Game data update had issues (code {result.returncode})")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}")
                success = False
        except subprocess.TimeoutExpired:
            print("   ⚠️  Game data fetch timed out")
            success = False
        except Exception as e:
            print(f"   ❌ Error fetching game data: {e}")
            success = False
        
        # Step 2: Update prediction results
        print("\n📊 Step 2: Updating ML prediction results...")
        try:
            result = subprocess.run(
                [sys.executable, str(self.update_script)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("   ✅ Prediction results updated")
                # Show summary from output
                for line in result.stdout.split('\n'):
                    if 'Updated' in line or 'predictions' in line or 'Performance' in line:
                        print(f"   {line.strip()}")
            else:
                print(f"   ⚠️  Prediction update had issues (code {result.returncode})")
                success = False
        except subprocess.TimeoutExpired:
            print("   ⚠️  Prediction update timed out")
            success = False
        except Exception as e:
            print(f"   ❌ Error updating predictions: {e}")
            success = False
        
        print("\n" + "="*80)
        if success:
            print("✅ UPDATE CYCLE COMPLETE")
        else:
            print("⚠️  UPDATE CYCLE COMPLETED WITH WARNINGS")
        print("="*80 + "\n")
        
        return success
    
    def run_continuous(self, interval_minutes: int = 15):
        """Run continuous updates at specified interval"""
        print("\n" + "="*80)
        print("🤖 AUTOMATED NFL DATA UPDATE SERVICE")
        print("="*80)
        print(f"\n⚙️  Configuration:")
        print(f"   • Update interval: Every {interval_minutes} minutes")
        print(f"   • Project root: {self.project_root}")
        print(f"   • Data source: nflverse (nfl_data_py)")
        print(f"   • Active during: NFL season (Sep-Feb) on game days")
        print(f"\n💡 Press Ctrl+C to stop\n")
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                print(f"\n{'='*80}")
                print(f"🔄 CYCLE #{cycle_count}")
                print(f"{'='*80}")
                
                self.run_update_cycle()
                
                next_update = datetime.now() + timedelta(minutes=interval_minutes)
                print(f"\n⏰ Next update at: {next_update.strftime('%I:%M %p')}")
                print(f"⏸️  Sleeping for {interval_minutes} minutes...")
                print(f"   (Ctrl+C to stop)")
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n\n" + "="*80)
            print("🛑 AUTO UPDATE SERVICE STOPPED")
            print("="*80)
            print(f"\n📊 Statistics:")
            print(f"   • Total update cycles: {cycle_count}")
            print(f"   • Service ran for: {cycle_count * interval_minutes} minutes")
            print("\n👋 Service shutdown gracefully\n")


def main():
    project_root = Path(__file__).parent
    service = AutoUpdateService(project_root)
    
    # Check for continuous mode
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        service.run_continuous(interval)
    else:
        # Run once
        success = service.run_update_cycle()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
