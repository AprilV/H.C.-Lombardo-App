#!/usr/bin/env python3
"""
COMPREHENSIVE DATABASE AUDIT
Compare LOCAL (working) vs RENDER (broken) to create a proper migration plan
"""

import psycopg2
from psycopg2.extras import RealDictCursor

print("\n" + "="*80)
print("🔍 COMPREHENSIVE DATABASE AUDIT: LOCAL vs RENDER")
print("="*80)

# LOCAL (WORKING)
local_conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password='aprilv120',
    host='localhost',
    port='5432'
)

# RENDER (BROKEN)
render_conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='nfl_user',
    password='rzkKyzQq9pTas14pXDJU3fm8cCZObAh5',
    host='dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com',
    port='5432'
)

local_cur = local_conn.cursor(cursor_factory=RealDictCursor)
render_cur = render_conn.cursor(cursor_factory=RealDictCursor)

print("\n📊 PART 1: SCHEMA COMPARISON")
print("-"*80)

# Get all tables in HCL schema
local_cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'hcl'
    ORDER BY table_name
""")
local_tables = {r['table_name'] for r in local_cur.fetchall()}

render_cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'hcl'
    ORDER BY table_name
""")
render_tables = {r['table_name'] for r in render_cur.fetchall()}

print(f"\nLOCAL tables: {sorted(local_tables)}")
print(f"RENDER tables: {sorted(render_tables)}")

missing_render = local_tables - render_tables
extra_render = render_tables - local_tables

if missing_render:
    print(f"\n❌ MISSING on Render: {missing_render}")
if extra_render:
    print(f"\n⚠️  EXTRA on Render: {extra_render}")

print("\n📋 PART 2: DATA COUNTS")
print("-"*80)

for table in sorted(local_tables & render_tables):
    local_cur.execute(f"SELECT COUNT(*) as cnt FROM hcl.{table}")
    local_count = local_cur.fetchone()['cnt']
    
    render_cur.execute(f"SELECT COUNT(*) as cnt FROM hcl.{table}")
    render_count = render_cur.fetchone()['cnt']
    
    status = "✅" if local_count == render_count else "❌"
    print(f"{status} {table:20} | Local: {local_count:6,} | Render: {render_count:6,}")

print("\n🎯 PART 3: CRITICAL 2025 SEASON DATA")
print("-"*80)

# Check 2025 games
local_cur.execute("SELECT COUNT(*) as cnt FROM hcl.games WHERE season = 2025")
local_2025_games = local_cur.fetchone()['cnt']

render_cur.execute("SELECT COUNT(*) as cnt FROM hcl.games WHERE season = 2025")
render_2025_games = render_cur.fetchone()['cnt']

print(f"\n2025 Games:")
print(f"  Local:  {local_2025_games:3,}")
print(f"  Render: {render_2025_games:3,}")
print(f"  Status: {'✅ MATCH' if local_2025_games == render_2025_games else '❌ MISMATCH'}")

# Check Week 13 specifically
local_cur.execute("SELECT COUNT(*) as cnt FROM hcl.games WHERE season = 2025 AND week = 13")
local_wk13 = local_cur.fetchone()['cnt']

render_cur.execute("SELECT COUNT(*) as cnt FROM hcl.games WHERE season = 2025 AND week = 13")
render_wk13 = render_cur.fetchone()['cnt']

print(f"\n2025 Week 13 Games (FOR ML PREDICTIONS):")
print(f"  Local:  {local_wk13:3,}")
print(f"  Render: {render_wk13:3,}")
print(f"  Status: {'✅ MATCH' if local_wk13 == render_wk13 else '❌ MISSING - THIS BREAKS ML!'}")

if local_wk13 > 0:
    local_cur.execute("""
        SELECT game_id, home_team, away_team, home_score, away_score, spread_line
        FROM hcl.games 
        WHERE season = 2025 AND week = 13 
        ORDER BY game_id
        LIMIT 3
    """)
    print("\n  Sample Week 13 games in LOCAL:")
    for game in local_cur.fetchall():
        print(f"    {game['game_id']:20} | {game['home_team']} vs {game['away_team']} | Score: {game['home_score']}-{game['away_score']} | Spread: {game['spread_line']}")

print("\n📊 PART 4: EPA DATA CHECK")
print("-"*80)

# Check EPA columns exist and have data
local_cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(epa_per_play) as with_epa,
        AVG(epa_per_play) as avg_epa
    FROM hcl.team_game_stats
    WHERE season = 2025
""")
local_epa = local_cur.fetchone()

render_cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(epa_per_play) as with_epa,
        AVG(epa_per_play) as avg_epa
    FROM hcl.team_game_stats
    WHERE season = 2025
""")
render_epa = render_cur.fetchone()

print(f"\n2025 Team Stats with EPA:")
print(f"  Local:  {local_epa['with_epa']:3,} / {local_epa['total']:3,} (avg: {local_epa['avg_epa']})")
print(f"  Render: {render_epa['with_epa']:3,} / {render_epa['total']:3,} (avg: {render_epa['avg_epa']})")

print("\n🔧 PART 5: COLUMN SCHEMA CHECK")
print("-"*80)

for table in ['games', 'team_game_stats']:
    local_cur.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'hcl' AND table_name = '{table}'
        ORDER BY ordinal_position
    """)
    local_cols = {r['column_name'] for r in local_cur.fetchall()}
    
    render_cur.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'hcl' AND table_name = '{table}'
        ORDER BY ordinal_position
    """)
    render_cols = {r['column_name'] for r in render_cur.fetchall()}
    
    print(f"\n{table}:")
    print(f"  Local:  {len(local_cols)} columns")
    print(f"  Render: {len(render_cols)} columns")
    
    missing = local_cols - render_cols
    extra = render_cols - local_cols
    
    if missing:
        print(f"  ❌ Missing on Render: {missing}")
    if extra:
        print(f"  ⚠️  Extra on Render: {extra}")
    if not missing and not extra:
        print(f"  ✅ Schemas match")

print("\n" + "="*80)
print("📋 MIGRATION PLAN NEEDED:")
print("="*80)
print("""
Based on this audit, we need to:

1. ❌ PROBLEM: Render missing 2025 games
   → SOLUTION: Copy ALL games WHERE season = 2025 from local to Render

2. ❌ PROBLEM: Render missing 2025 team stats  
   → SOLUTION: Copy ALL team_game_stats WHERE season = 2025 from local to Render

3. ❌ PROBLEM: Render missing EPA data
   → SOLUTION: Ensure EPA columns populated (should come with team_game_stats copy)

4. ❌ PROBLEM: Missing team_info or wrong columns
   → SOLUTION: Verify team_info exists and has correct schema

5. ✅ VERIFY: All schemas match (games: 37 cols, team_game_stats: 64 cols)

6. ✅ VERIFY: ML predictions can query Week 13 games
""")

local_conn.close()
render_conn.close()

print("\n" + "="*80 + "\n")
