#!/usr/bin/env python3
"""
Clean User Schema Database
Remove duplicate teams and ensure exactly 32 teams
"""

import sqlite3

def clean_user_schema_teams():
    """Remove duplicates and ensure clean 32 teams"""
    print("🧹 Cleaning User Schema Database")
    print("Removing duplicate teams...")
    
    try:
        conn = sqlite3.connect("user_schema_nfl.db")
        cursor = conn.cursor()
        
        # Get current count
        cursor.execute("SELECT COUNT(*) FROM Teams")
        before_count = cursor.fetchone()[0]
        print(f"📊 Before: {before_count} teams")
        
        # Create temporary table with unique teams
        cursor.execute('''
            CREATE TEMPORARY TABLE temp_teams AS
            SELECT MIN(team_id) as team_id, name, abbreviation, conference, division
            FROM Teams
            GROUP BY name, abbreviation
        ''')
        
        # Clear original table
        cursor.execute("DELETE FROM Teams")
        
        # Insert unique teams back
        cursor.execute('''
            INSERT INTO Teams (name, abbreviation, conference, division)
            SELECT name, abbreviation, conference, division
            FROM temp_teams
            ORDER BY conference, division, name
        ''')
        
        conn.commit()
        
        # Get final count
        cursor.execute("SELECT COUNT(*) FROM Teams")
        after_count = cursor.fetchone()[0]
        print(f"📊 After: {after_count} teams")
        print(f"🗑️ Removed: {before_count - after_count} duplicates")
        
        if after_count == 32:
            print("✅ Perfect! Exactly 32 teams")
        else:
            print(f"⚠️ Expected 32, got {after_count}")
        
        # Show teams by conference
        print("\n📋 Final Team List:")
        cursor.execute('''
            SELECT conference, division, name, abbreviation
            FROM Teams
            ORDER BY conference, division, name
        ''')
        
        current_conf = None
        current_div = None
        
        for conf, div, name, abbr in cursor.fetchall():
            if conf != current_conf:
                print(f"\n🏈 {conf} Conference:")
                current_conf = conf
                current_div = None
                
            if div != current_div:
                print(f"   {div} Division:")
                current_div = div
                
            print(f"     {name} ({abbr})")
        
        conn.close()
        return after_count
        
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        return 0

def main():
    final_count = clean_user_schema_teams()
    
    if final_count == 32:
        print("\n🎉 SUCCESS! User schema database cleaned!")
        print("✅ Exactly 32 teams, no duplicates")
        print("🏆 Both databases now have complete NFL rosters!")
    else:
        print(f"\n⚠️ Final count: {final_count} (expected 32)")

if __name__ == "__main__":
    main()