#!/usr/bin/env python3
"""
One-time database setup script for Render deployment.
Populates the database with NFL data from NFLverse.
"""

import os
import sys
import psycopg2
from db_config import get_db_connection

def setup_database():
    """Create schema and load initial data."""
    print("🚀 Starting Render database setup...")
    
    try:
        conn = get_db_connection()
        print("✅ Connected to database")
        
        # Import schema creation
        print("📋 Creating production schema...")
        os.system('python recreate_production_schema.py')
        
        # Load NFL data
        print("🏈 Loading NFL data from NFLverse...")
        os.system('python nfl_database_loader.py')
        
        print("✅ Database setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
