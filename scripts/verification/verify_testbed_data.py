#!/usr/bin/env python3
"""
Verify testbed data load
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'nfl_analytics'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD')
)

print("="*80)
print("TESTBED DATA VERIFICATION")
print("="*80)

try:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Query 1: Row counts
        print("\n1. TABLE ROW COUNTS:")
        cur.execute("SELECT COUNT(*) as count FROM hcl_test.games")
        games_count = cur.fetchone()['count']
        print(f"   Games: {games_count}")
        
        cur.execute("SELECT COUNT(*) as count FROM hcl_test.team_game_stats")
        stats_count = cur.fetchone()['count']
        print(f"   Team-game stats: {stats_count}")
        
        # Query 2: Season breakdown
        print("\n2. GAMES BY SEASON:")
        cur.execute("""
            SELECT season, COUNT(*) as game_count 
            FROM hcl_test.games 
            GROUP BY season 
            ORDER BY season DESC
        """)
        for row in cur.fetchall():
            print(f"   {row['season']}: {row['game_count']} games")
        
        # Query 3: Sample game (Week 1 KC @ BAL)
        print("\n3. SAMPLE GAME (2024 Week 1):")
        cur.execute("""
            SELECT game_id, home_team, away_team, home_score, away_score, winner
            FROM hcl_test.v_game_matchup_display
            WHERE season = 2024 AND week = 1
            ORDER BY game_date
            LIMIT 3
        """)
        print("   First 3 games of Week 1:")
        for row in cur.fetchall():
            print(f"   {row['game_id']}: {row['away_team']} @ {row['home_team']} | Score: {row['away_score']}-{row['home_score']} | Winner: {row['winner']}")
        
        # Query 4: Check for NULLs
        print("\n4. DATA QUALITY CHECK:")
        cur.execute("""
            SELECT COUNT(*) as count 
            FROM hcl_test.team_game_stats 
            WHERE points IS NULL OR total_yards IS NULL
        """)
        null_count = cur.fetchone()['count']
        if null_count > 0:
            print(f"   ⚠️  WARNING: {null_count} records with NULL critical stats")
        else:
            print("   ✓ No NULL critical stats (good!)")
        
        # Query 5: Average stats
        print("\n5. AVERAGE STATS PER TEAM:")
        cur.execute("""
            SELECT 
                ROUND(AVG(points)::numeric, 1) as avg_points,
                ROUND(AVG(total_yards)::numeric, 0) as avg_yards,
                ROUND(AVG(completion_pct)::numeric, 1) as avg_comp_pct
            FROM hcl_test.team_game_stats
        """)
        row = cur.fetchone()
        print(f"   Average points: {row['avg_points']} PPG")
        print(f"   Average yards: {row['avg_yards']} YPG")
        print(f"   Average completion: {row['avg_comp_pct']}%")
        
        # Query 6: Check view works
        print("\n6. MATERIALIZED VIEW TEST:")
        cur.execute("SELECT COUNT(*) as count FROM hcl_test.v_game_matchup_display")
        view_count = cur.fetchone()['count']
        print(f"   View has {view_count} rows (should match games count: {games_count})")
        if view_count == games_count:
            print("   ✓ View working correctly!")
        else:
            print(f"   ⚠️  View count mismatch!")
        
except Exception as e:
    print(f"✗ Error: {e}")
finally:
    conn.close()

print("\n" + "="*80)
print("VERIFICATION COMPLETE!")
print("="*80)
