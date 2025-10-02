import sqlite3
import os

# Check multiple possible database paths
db_paths = [
    "apis/nfl_dashboard.db",
    "apis/nfl_betting.db",
    "nfl_betting_database/enhanced_nfl_betting.db",
    "apis/../nfl_betting_database/enhanced_nfl_betting.db"
]

for db_path in db_paths:
    print(f"\n🔍 Checking database: {db_path}")
    if os.path.exists(db_path):
        print(f"✅ Database file exists")
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"Tables: {tables}")
                
                # If we have tables, get counts
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  {table}: {count} records")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"❌ Database file does not exist")
    if 'teams' in tables:
        cursor.execute("PRAGMA table_info(teams)")
        teams_columns = cursor.fetchall()
        print("teams columns:", teams_columns)
    
    # Check Games table columns if it exists
    if 'Games' in tables:
        cursor.execute("PRAGMA table_info(Games)")
        games_columns = cursor.fetchall()
        print("Games columns:", games_columns)
    
    conn.close()
else:
    print("Database file does not exist")