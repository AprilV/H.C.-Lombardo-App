#!/usr/bin/env python3
"""
Daily NFL Data Updater
Runs once daily to refresh NFL data from ESPN APIs
"""

import asyncio
import schedule
import time
from datetime import datetime
import requests
import sys
import os

# Add the apis directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'apis'))

def update_nfl_data():
    """Update NFL data by calling the scrape-data endpoint"""
    try:
        print(f"🔄 Daily Update Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Call the existing data refresh endpoint
        response = requests.get('http://localhost:8004/api/scrape-data', timeout=30)
        
        if response.status_code == 200:
            print("✅ NFL data updated successfully!")
            print(f"   Teams, Games, and Stats refreshed from ESPN")
        else:
            print(f"❌ Update failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Daily update error: {e}")

def main():
    """Main scheduler function"""
    print("🚀 Starting Daily NFL Data Updater...")
    print("📅 Scheduled to run daily at 6:00 AM")
    
    # Schedule daily update at 6 AM (when most NFL updates are available)
    schedule.every().day.at("06:00").do(update_nfl_data)
    
    # Also schedule after typical game times
    schedule.every().monday.at("02:00").do(update_nfl_data)    # After Monday Night Football
    schedule.every().tuesday.at("08:00").do(update_nfl_data)   # Tuesday morning updates
    schedule.every().thursday.at("02:00").do(update_nfl_data)  # After Thursday Night Football
    
    print("⏰ Scheduler running... (Press Ctrl+C to stop)")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n🛑 Daily updater stopped")

if __name__ == "__main__":
    main()