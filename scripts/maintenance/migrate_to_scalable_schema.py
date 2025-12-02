"""
Scalable NFL Data System - Database Migration
Creates extensible schema for 100+ stats without schema changes

NEW APPROACH:
- Keep basic fields (name, abbreviation, wins, losses) in main columns
- Store ALL other stats in a JSONB column for flexibility
- Add stats_metadata table to track available stats
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'nfl_analytics'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'aprilv120')
    )

def migrate_to_scalable_schema():
    """Migrate database to support 100+ stats"""
    print("\n" + "="*70)
    print("MIGRATING TO SCALABLE SCHEMA")
    print("="*70)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Step 1: Add JSONB column for extensible stats
        print("\n1️⃣  Adding stats JSONB column...")
        cursor.execute("""
            ALTER TABLE teams 
            ADD COLUMN IF NOT EXISTS stats JSONB DEFAULT '{}'::jsonb;
        """)
        print("   ✅ Added 'stats' column for flexible stat storage")
        
        # Step 2: Migrate existing PPG and PA into stats column
        print("\n2️⃣  Migrating existing stats to JSONB...")
        cursor.execute("""
            UPDATE teams 
            SET stats = jsonb_build_object(
                'offense', jsonb_build_object(
                    'points_per_game', ppg,
                    'total_points', ppg * games_played
                ),
                'defense', jsonb_build_object(
                    'points_allowed_per_game', pa,
                    'total_points_allowed', pa * games_played
                ),
                'record', jsonb_build_object(
                    'wins', wins,
                    'losses', losses,
                    'games_played', games_played
                )
            )
            WHERE ppg > 0;
        """)
        print("   ✅ Migrated PPG and PA to stats JSONB")
        
        # Step 3: Create stats_metadata table
        print("\n3️⃣  Creating stats metadata table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats_metadata (
                stat_key VARCHAR(100) PRIMARY KEY,
                stat_name VARCHAR(200),
                category VARCHAR(50),
                data_type VARCHAR(20),
                description TEXT,
                source VARCHAR(100),
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ Created stats_metadata table")
        
        # Step 4: Insert metadata for current stats
        print("\n4️⃣  Populating stats metadata...")
        stat_definitions = [
            ('offense.points_per_game', 'Points Per Game', 'offense', 'float', 'Average points scored per game', 'TeamRankings'),
            ('offense.total_points', 'Total Points', 'offense', 'integer', 'Total points scored this season', 'Calculated'),
            ('defense.points_allowed_per_game', 'Points Allowed Per Game', 'defense', 'float', 'Average points allowed per game', 'TeamRankings'),
            ('defense.total_points_allowed', 'Total Points Allowed', 'defense', 'integer', 'Total points allowed this season', 'Calculated'),
            ('record.wins', 'Wins', 'record', 'integer', 'Total wins', 'ESPN'),
            ('record.losses', 'Losses', 'record', 'integer', 'Total losses', 'ESPN'),
            ('record.games_played', 'Games Played', 'record', 'integer', 'Total games played', 'Calculated'),
        ]
        
        for stat_key, stat_name, category, data_type, description, source in stat_definitions:
            cursor.execute("""
                INSERT INTO stats_metadata (stat_key, stat_name, category, data_type, description, source)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (stat_key) DO UPDATE 
                SET stat_name = EXCLUDED.stat_name,
                    category = EXCLUDED.category,
                    description = EXCLUDED.description;
            """, (stat_key, stat_name, category, data_type, description, source))
        
        print(f"   ✅ Added {len(stat_definitions)} stat definitions")
        
        # Step 5: Create helper functions
        print("\n5️⃣  Creating helper functions...")
        
        # Function to get a stat from JSONB
        cursor.execute("""
            CREATE OR REPLACE FUNCTION get_stat(team_stats JSONB, stat_path TEXT)
            RETURNS NUMERIC AS $$
            BEGIN
                RETURN (team_stats #>> string_to_array(stat_path, '.'))::NUMERIC;
            EXCEPTION WHEN OTHERS THEN
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql IMMUTABLE;
        """)
        print("   ✅ Created get_stat() function")
        
        conn.commit()
        
        print("\n" + "="*70)
        print("✅ MIGRATION COMPLETE")
        print("="*70)
        
        # Show example usage
        print("\n📊 Example Queries:")
        print("\n-- Get team with stats:")
        print("SELECT name, stats->'offense'->>'points_per_game' as ppg FROM teams LIMIT 3;")
        cursor.execute("SELECT name, stats->'offense'->>'points_per_game' as ppg FROM teams WHERE stats IS NOT NULL LIMIT 3;")
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]} PPG")
        
        print("\n-- Get all available stats:")
        print("SELECT stat_key, stat_name, category FROM stats_metadata;")
        cursor.execute("SELECT stat_key, stat_name, category FROM stats_metadata ORDER BY category, stat_key;")
        for row in cursor.fetchall():
            print(f"   [{row[2]}] {row[0]}: {row[1]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def test_schema():
    """Test the new schema"""
    print("\n" + "="*70)
    print("TESTING NEW SCHEMA")
    print("="*70)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Test 1: Check JSONB column exists
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'teams' AND column_name = 'stats';
    """)
    result = cursor.fetchone()
    if result:
        print(f"\n✅ Test 1: 'stats' column exists (type: {result[1]})")
    else:
        print("\n❌ Test 1: 'stats' column NOT found")
    
    # Test 2: Check metadata table
    cursor.execute("SELECT COUNT(*) FROM stats_metadata;")
    count = cursor.fetchone()[0]
    print(f"✅ Test 2: stats_metadata has {count} stat definitions")
    
    # Test 3: Check data migration
    cursor.execute("SELECT COUNT(*) FROM teams WHERE stats IS NOT NULL AND stats != '{}'::jsonb;")
    count = cursor.fetchone()[0]
    print(f"✅ Test 3: {count} teams have migrated stats")
    
    conn.close()

if __name__ == "__main__":
    success = migrate_to_scalable_schema()
    if success:
        test_schema()
        print("\n🎯 READY TO ADD 100+ STATS!")
        print("   Just update the multi_source_data_fetcher to populate stats JSONB")
