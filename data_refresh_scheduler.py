"""
Automated Data Refresh Scheduler
Runs multi_source_data_fetcher.py every 15 minutes during NFL game hours
"""
import schedule
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime, time as dt_time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/data_refresh_scheduler.log'),
        logging.StreamHandler()
    ]
)

class DataRefreshScheduler:
    """Automatically refreshes NFL data on a schedule"""
    
    def __init__(self, refresh_interval_minutes=15):
        self.refresh_interval = refresh_interval_minutes
        self.project_root = Path(__file__).parent
        self.fetcher_script = self.project_root / "multi_source_data_fetcher.py"
        
    def is_game_hours(self):
        """Check if current time is during NFL game hours"""
        now = datetime.now()
        current_time = now.time()
        
        # NFL games typically:
        # Thursday: 8:15 PM ET (1 game)
        # Sunday: 1:00 PM, 4:05 PM, 4:25 PM, 8:20 PM ET
        # Monday: 8:15 PM ET (1 game)
        
        # Game hours: 12:00 PM - 12:00 AM ET (covers all games)
        game_start = dt_time(12, 0)  # 12:00 PM
        game_end = dt_time(23, 59)   # 11:59 PM
        
        # Only run on game days (Thursday, Sunday, Monday)
        game_days = [3, 6, 0]  # Thursday=3, Sunday=6, Monday=0
        is_game_day = now.weekday() in game_days
        
        is_game_time = game_start <= current_time <= game_end
        
        return is_game_day and is_game_time
    
    def refresh_data(self):
        """Run the data fetcher"""
        logging.info("="*70)
        logging.info("SCHEDULED DATA REFRESH")
        logging.info("="*70)
        
        # Check if it's game hours
        if not self.is_game_hours():
            logging.info("⏸️  Outside game hours - skipping refresh")
            logging.info("   (Refresh only runs Thu/Sun/Mon 12PM-12AM)")
            return
        
        try:
            logging.info(f"Running: {self.fetcher_script}")
            
            result = subprocess.run(
                [sys.executable, str(self.fetcher_script)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logging.info("✅ Data refresh successful")
                # Log summary
                if "32 teams" in result.stdout:
                    logging.info("   Updated: 32 teams")
            else:
                logging.error(f"❌ Data refresh failed: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            logging.error("❌ Data refresh timed out (>60 seconds)")
        except Exception as e:
            logging.error(f"❌ Data refresh error: {e}")
    
    def refresh_data_always(self):
        """Run data fetcher regardless of time (for testing)"""
        logging.info("="*70)
        logging.info("MANUAL DATA REFRESH (bypassing schedule)")
        logging.info("="*70)
        
        try:
            result = subprocess.run(
                [sys.executable, str(self.fetcher_script)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logging.info("✅ Data refresh successful")
            else:
                logging.error(f"❌ Data refresh failed")
                
        except Exception as e:
            logging.error(f"❌ Error: {e}")
    
    def start(self, test_mode=False):
        """Start the scheduler"""
        logging.info("\n" + "="*70)
        logging.info("DATA REFRESH SCHEDULER STARTED")
        logging.info("="*70)
        logging.info(f"Refresh interval: Every {self.refresh_interval} minutes")
        logging.info(f"Game hours: Thursday/Sunday/Monday 12PM-12AM")
        logging.info(f"Data source: {self.fetcher_script}")
        
        if test_mode:
            logging.info("\n⚠️  TEST MODE: Will refresh regardless of day/time")
            schedule.every(self.refresh_interval).minutes.do(self.refresh_data_always)
        else:
            logging.info("\n✅ PRODUCTION MODE: Only refreshes during game hours")
            schedule.every(self.refresh_interval).minutes.do(self.refresh_data)
        
        # Run once immediately on startup
        logging.info("\nRunning initial data refresh...")
        if test_mode:
            self.refresh_data_always()
        else:
            self.refresh_data()
        
        logging.info(f"\n📅 Next refresh in {self.refresh_interval} minutes")
        logging.info("Press Ctrl+C to stop\n")
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("\n\n⏹️  Scheduler stopped by user")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='NFL Data Refresh Scheduler')
    parser.add_argument(
        '--interval',
        type=int,
        default=15,
        help='Refresh interval in minutes (default: 15)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: refresh regardless of day/time'
    )
    
    args = parser.parse_args()
    
    scheduler = DataRefreshScheduler(refresh_interval_minutes=args.interval)
    scheduler.start(test_mode=args.test)

if __name__ == "__main__":
    main()
