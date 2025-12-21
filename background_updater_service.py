#!/usr/bin/env python3
"""
Standalone Background Updater Service
Run this as a separate process from the API server
Updates NFL data every 30 minutes
"""
import logging
import time
import sys
import os
from datetime import datetime

# Add scripts/maintenance to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts', 'maintenance'))
from multi_source_data_fetcher import MultiSourceDataFetcher
from update_live_data import update_current_season_scores

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/H.C.-Lombardo-App/logs/background_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main update loop"""
    update_interval_minutes = 30
    
    logger.info("=" * 70)
    logger.info("🏈 NFL BACKGROUND DATA UPDATER SERVICE STARTED")
    logger.info(f"⏰ Update interval: {update_interval_minutes} minutes")
    logger.info("=" * 70)
    
    # Wait 60 seconds before first update (let API server fully start)
    logger.info("⏳ Waiting 60 seconds before first update...")
    time.sleep(60)
    
    while True:
        try:
            logger.info("=" * 70)
            logger.info(f"🔄 AUTOMATIC DATA UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 70)
            
            # 1. Update team standings (ESPN + TeamRankings)
            logger.info("📊 Updating team standings...")
            fetcher = MultiSourceDataFetcher()
            fetcher.run_full_update()
            
            # 2. Update game scores and stats (NFLverse)
            logger.info("🏈 Updating game scores and stats...")
            games_updated, stats_updated = update_current_season_scores()
            logger.info(f"   - Updated {games_updated} game scores")
            logger.info(f"   - Updated {stats_updated} team game stats")
            
            logger.info("✅ Automatic update complete")
            logger.info(f"⏰ Next update in {update_interval_minutes} minutes")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Background update failed: {e}", exc_info=True)
            
        # Sleep until next update
        time.sleep(update_interval_minutes * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Background updater stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}", exc_info=True)
        raise
