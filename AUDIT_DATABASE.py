#!/usr/bin/env python3
"""
COMPREHENSIVE DATABASE AUDIT
Audit the EC2 localhost PostgreSQL database
"""

import psycopg2
import os
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("🔍 COMPREHENSIVE DATABASE AUDIT")
print("="*80)

# Connect to database
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'nfl_analytics'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD')
)

cur = conn.cursor(cursor_factory=RealDictCursor)

print("\n📊 PART 1: SCHEMA TABLES")
print("-"*80)

# Get all tables in HCL schema
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'hcl'
    ORDER BY table_name
""")
tables = [r['table_name'] for r in cur.fetchall()]

print(f"\nHCL Schema tables: {', '.join(sorted(tables))}")

print("\n📋 PART 2: DATA COUNTS")
print("-"*80)

for table in sorted(tables):
    cur.execute(f"SELECT COUNT(*) as cnt FROM hcl.{table}")
    count = cur.fetchone()['cnt']
    
    print(f"{table:30} | {count:6,} records")

print("\n🎯 PART 3: CRITICAL 2025 SEASON DATA")
print("-"*80)

# Check 2025 games
cur.execute("SELECT COUNT(*) as cnt FROM hcl.games WHERE season = 2025")
games_2025 = cur.fetchone()['cnt']

print(f"\n2025 Games: {games_2025:3,}")

# Check Week 13 specifically
cur.execute("SELECT COUNT(*) as cnt FROM hcl.games WHERE season = 2025 AND week = 13")
wk13 = cur.fetchone()['cnt']

print(f"2025 Week 13 Games: {wk13:3,}")

if wk13 > 0:
    cur.execute("""
        SELECT game_id, home_team, away_team, home_score, away_score, spread_line
        FROM hcl.games 
        WHERE season = 2025 AND week = 13 
        ORDER BY game_id
        LIMIT 3
    """)
    print("\n  Sample Week 13 games:")
    for game in cur.fetchall():
        print(f"    {game['game_id']:20} | {game['home_team']} vs {game['away_team']} | Score: {game['home_score']}-{game['away_score']} | Spread: {game['spread_line']}")

print("\n📊 PART 4: EPA DATA CHECK")
print("-"*80)

# Check EPA columns exist and have data
cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(epa_per_play) as with_epa,
        AVG(epa_per_play) as avg_epa
    FROM hcl.team_game_stats
    WHERE season = 2025
""")
epa_stats = cur.fetchone()
print(f"\n2025 Season EPA Stats:")
print(f"  Total records: {epa_stats['total']:,}")
print(f"  With EPA data: {epa_stats['with_epa']:,}")
print(f"  Average EPA: {epa_stats['avg_epa']:.4f}" if epa_stats['avg_epa'] else "  Average EPA: None")
print(f"  Status: {'✅ ALL HAVE EPA' if epa_stats['total'] == epa_stats['with_epa'] else '⚠️  SOME MISSING EPA'}")

print("\n🔧 PART 5: COLUMN SCHEMA CHECK")
print("-"*80)

for table in ['games', 'team_game_stats']:
    cur.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'hcl' AND table_name = '{table}'
        ORDER BY ordinal_position
    """)
    cols = [r['column_name'] for r in cur.fetchall()]
    
    print(f"\n{table}: {len(cols)} columns")
    print(f"  Columns: {', '.join(cols[:10])}..." if len(cols) > 10 else f"  Columns: {', '.join(cols)}")

print("\n" + "="*80)
print("✅ AUDIT COMPLETE")
print("="*80)

conn.close()

print("\n" + "="*80 + "\n")
