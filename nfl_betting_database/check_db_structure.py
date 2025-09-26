#!/usr/bin/env python3
"""
Check Database Structure
"""

import sqlite3
import os

def check_database_structure():
    print("🔍 Checking Database Structure")
    print("=" * 40)
    
    databases = [
        "nfl_betting.db",
        "user_schema_nfl.db"
    ]
    
    for db_name in databases:
        if os.path.exists(db_name):
            print(f"\n📊 Database: {db_name}")
            try:
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                
                # Get tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                print(f"   Tables: {[t[0] for t in tables]}")
                
                # Check each table structure
                for table_name in [t[0] for t in tables]:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    print(f"   {table_name}: {len(columns)} columns")
                    for col in columns:
                        print(f"     - {col[1]} ({col[2]})")
                
                conn.close()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print(f"\n❌ Database not found: {db_name}")

if __name__ == "__main__":
    check_database_structure()