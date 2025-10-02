#!/usr/bin/env python3
"""
Database Status Checker
Checks all 3 primary databases used in the H.C. Lombardo App system
"""

import sqlite3
import os
from datetime import datetime

def check_database_status(db_path, db_name):
    """Check the status of a specific database"""
    print(f"\n📋 Checking {db_name}")
    print("=" * 50)
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get file size
        file_size = os.path.getsize(db_path) / 1024  # KB
        print(f"📁 File: {db_path}")
        print(f"📊 Size: {file_size:.1f} KB")
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            print("⚠️  No tables found")
            conn.close()
            return False
        
        print(f"🗂️  Tables ({len(tables)}):")
        
        # Check each table
        total_records = 0
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                total_records += count
                print(f"   • {table}: {count} records")
            except Exception as e:
                print(f"   • {table}: ❌ Error - {e}")
        
        print(f"📈 Total Records: {total_records}")
        
        # Test a simple query
        if tables:
            try:
                cursor.execute(f"SELECT * FROM {tables[0]} LIMIT 1")
                sample = cursor.fetchone()
                if sample:
                    print("✅ Database is functional - sample data retrieved")
                else:
                    print("⚠️  Database functional but no data in main table")
            except Exception as e:
                print(f"❌ Query test failed: {e}")
                conn.close()
                return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Check all 3 primary databases"""
    print("🔍 H.C. Lombardo App - Database Status Check")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define the 3 primary databases
    databases = {
        "Enhanced NFL Database (Main)": "nfl_betting_database/enhanced_nfl_betting.db",
        "Dashboard Database": "apis/nfl_dashboard.db", 
        "Legacy Sports Betting DB": "nfl_betting_database/sports_betting.db"
    }
    
    results = {}
    
    # Check each database
    for db_name, db_path in databases.items():
        full_path = os.path.join(os.getcwd(), db_path)
        results[db_name] = check_database_status(full_path, db_name)
    
    # Summary
    print(f"\n🎯 DATABASE STATUS SUMMARY")
    print("=" * 60)
    
    working_count = 0
    for db_name, status in results.items():
        status_icon = "✅" if status else "❌"
        status_text = "WORKING" if status else "ISSUES"
        print(f"{status_icon} {db_name}: {status_text}")
        if status:
            working_count += 1
    
    print(f"\n📊 Overall Status: {working_count}/{len(databases)} databases working")
    
    if working_count == len(databases):
        print("🎉 ALL DATABASES ARE WORKING PERFECTLY!")
    elif working_count > 0:
        print("⚠️  Some databases need attention")
    else:
        print("🚨 CRITICAL: All databases have issues!")

if __name__ == "__main__":
    main()