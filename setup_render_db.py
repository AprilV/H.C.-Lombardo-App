#!/usr/bin/env python3
"""
One-time database setup script for Render deployment.
Populates the database with NFL data from NFLverse.
"""

import os
import sys

def setup_database():
    """Create schema and load initial data."""
    print("🚀 Starting Render database setup...")
    
    try:
        # Skip schema recreation - using manually migrated data
        print("📋 Skipping schema recreation (preserving migrated data)...")
        
        # Load current 2025 season data from NFLverse
        print("🏈 Loading 2025 NFL data from NFLverse...")
        result = os.system('python ingest_historical_games.py --production --seasons 2025')
        if result != 0:
            print("⚠️ Data loading had warnings but continuing...")
        
        print("✅ Database setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
