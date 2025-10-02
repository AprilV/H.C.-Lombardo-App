#!/usr/bin/env python3
"""
Test the database status functionality independently
"""
import sys
import os
import sqlite3

# Add the apis directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'apis'))

try:
    from live_data_collector import LiveNFLDataCollector
    
    print("✅ Import successful")
    
    collector = LiveNFLDataCollector()
    print("✅ Collector created")
    
    db_path = collector.db_path
    print(f"📍 Database path: {db_path}")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Check what tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tables: {tables}")
        
        # Get team count (try both Teams and teams tables)
        team_count = 0
        if 'Teams' in tables:
            cursor.execute("SELECT COUNT(*) FROM Teams")
            team_count = cursor.fetchone()[0]
            print(f"👥 Teams: {team_count}")
        elif 'teams' in tables:
            cursor.execute("SELECT COUNT(*) FROM teams")
            team_count = cursor.fetchone()[0]
            print(f"👥 Teams: {team_count}")
        
        # Get game count (try both Games and games tables)
        game_count = 0
        if 'Games' in tables:
            cursor.execute("SELECT COUNT(*) FROM Games")
            game_count = cursor.fetchone()[0]
            print(f"🏈 Games: {game_count}")
        elif 'games' in tables:
            cursor.execute("SELECT COUNT(*) FROM games")
            game_count = cursor.fetchone()[0]
            print(f"🏈 Games: {game_count}")
        
        # Get recent collection logs if table exists
        recent_logs = []
        if 'data_collection_log' in tables:
            cursor.execute("""
                SELECT source, records_processed, timestamp, notes 
                FROM data_collection_log 
                ORDER BY timestamp DESC LIMIT 5
            """)
            recent_logs = [dict(zip(['source', 'records', 'timestamp', 'notes'], row)) 
                          for row in cursor.fetchall()]
            print(f"📝 Recent logs: {len(recent_logs)} entries")
        
        # Get sample team data (try enhanced schema first)
        sample_teams = []
        if 'Teams' in tables:
            cursor.execute("""
                SELECT name, abbreviation, conference, division, logo_url 
                FROM Teams 
                ORDER BY name LIMIT 5
            """)
            sample_teams = [dict(zip(['name', 'abbr', 'conference', 'division', 'logo'], row)) 
                           for row in cursor.fetchall()]
            print(f"⭐ Sample teams: {[t['name'] for t in sample_teams]}")
        
        # Get last update time
        last_updated = "Never"
        if recent_logs:
            last_updated = recent_logs[0]['timestamp']
            print(f"🕒 Last updated: {last_updated}")
    
    print("🎉 Database status check completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()