#!/usr/bin/env python3
"""
Drop and recreate production HCL schema
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("PRODUCTION SCHEMA RECREATION")
print("=" * 80)

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'nfl_analytics'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD')
)

try:
    with conn.cursor() as cur:
        # Drop existing schema if exists
        print("Dropping existing 'hcl' schema (if exists)...")
        cur.execute("DROP SCHEMA IF EXISTS hcl CASCADE")
        print("✓ Old schema dropped")
        
    conn.commit()
    
    # Read and execute new schema
    print("\nCreating new production schema...")
    with open('production_hcl_schema.sql', 'r') as f:
        sql = f.read()
    
    with conn.cursor() as cur:
        cur.execute(sql)
        
        # Verify tables created
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'hcl'
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        
        print("✓ Production schema 'hcl' created")
        print("\nTables created:")
        for table in tables:
            print(f"  - hcl.{table[0]}")
        
        # Verify materialized view
        cur.execute("""
            SELECT matviewname 
            FROM pg_matviews 
            WHERE schemaname = 'hcl'
        """)
        views = cur.fetchall()
        
        if views:
            print("\nMaterialized views:")
            for view in views:
                print(f"  - hcl.{view[0]}")
        
        # Get row counts (should be 0)
        cur.execute("SELECT COUNT(*) FROM hcl.games")
        games_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM hcl.team_game_stats")
        stats_count = cur.fetchone()[0]
        
        print(f"\nCurrent data:")
        print(f"  Games: {games_count}")
        print(f"  Team-game stats: {stats_count}")
    
    conn.commit()
    print("\n✓ Production schema ready for data load")
    
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
    raise
finally:
    conn.close()

print("\n" + "=" * 80)
print("SCHEMA RECREATION COMPLETE")
print("Next: Run production data loader")
print("=" * 80)
