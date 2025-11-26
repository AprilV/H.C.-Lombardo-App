"""
Background NFL Data Updater
Runs automatically in a separate thread to keep database current
Updates every 30 minutes during NFL season
"""
import threading
import time
import logging
from datetime import datetime
from multi_source_data_fetcher import MultiSourceDataFetcher

logger = logging.getLogger(__name__)

class BackgroundUpdater:
    """Automatically updates NFL data on a schedule"""
    
    def __init__(self, update_interval_minutes=30):
        self.update_interval = update_interval_minutes * 60  # Convert to seconds
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the background updater thread"""
        if self.running:
            logger.warning("Background updater already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        logger.info(f"🔄 Background updater started (updates every {self.update_interval // 60} minutes)")
        
    def stop(self):
        """Stop the background updater"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Background updater stopped")
        
    def _update_loop(self):
        """Main update loop that runs in background thread"""
        # Wait 60 seconds after startup before first update (let server fully start)
        time.sleep(60)
        
        while self.running:
            try:
                logger.info("=" * 70)
                logger.info(f"🏈 AUTOMATIC DATA UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info("=" * 70)
                
                # Run the data fetcher
                fetcher = MultiSourceDataFetcher()
                fetcher.run_update()
                
                logger.info("✅ Automatic update complete")
                logger.info(f"⏰ Next update in {self.update_interval // 60} minutes")
                logger.info("=" * 70)
                
            except Exception as e:
                logger.error(f"❌ Background update failed: {e}")
                
            # Sleep until next update
            time.sleep(self.update_interval)
            
    def update_now(self):
        """Trigger an immediate update (non-blocking)"""
        def _run_update():
            try:
                logger.info("🔄 Manual update triggered")
                fetcher = MultiSourceDataFetcher()
                fetcher.run_update()
                logger.info("✅ Manual update complete")
            except Exception as e:
                logger.error(f"❌ Manual update failed: {e}")
                
        thread = threading.Thread(target=_run_update, daemon=True)
        thread.start()

# Global instance
updater = BackgroundUpdater(update_interval_minutes=30)
