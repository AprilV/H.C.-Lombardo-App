#!/usr/bin/env python3
"""
Enhanced Database Viewer for H.C. Lombardo App
View tables, schema, and sample data
"""
import sqlite3
import os
from datetime import datetime

def view_database():
    """View the enhanced database with detailed information"""
    db_path = "nfl_betting_database/enhanced_nfl_betting.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    print("🗄️ H.C. LOMBARDO NFL DATABASE VIEWER")
    print("=" * 50)
    print(f"📍 Database: {db_path}")
    print(f"🕒 Viewing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Found {len(tables)} tables:")
        
        for table in tables:
            print(f"\n🗃️ TABLE: {table}")
            print("-" * 40)
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            # Get record count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            print(f"📊 Records: {count}")
            print(f"🔧 Columns: {len(columns)}")
            
            # Show column details
            print("📋 Schema:")
            for col in columns:
                col_id, name, data_type, not_null, default, pk = col
                pk_marker = " (PRIMARY KEY)" if pk else ""
                not_null_marker = " NOT NULL" if not_null else ""
                default_marker = f" DEFAULT {default}" if default else ""
                print(f"   • {name}: {data_type}{pk_marker}{not_null_marker}{default_marker}")
            
            # Show sample data if records exist
            if count > 0:
                print("🔍 Sample Data (first 3 records):")
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                
                # Get column names for headers
                col_names = [col[1] for col in columns]
                
                for i, row in enumerate(rows, 1):
                    print(f"   Record {i}:")
                    for j, value in enumerate(row):
                        # Truncate long values
                        display_value = str(value)
                        if len(display_value) > 50:
                            display_value = display_value[:47] + "..."
                        print(f"      {col_names[j]}: {display_value}")
                    print()
        
        print("=" * 50)
        print("🎯 Database viewing complete!")

if __name__ == "__main__":
    view_database()