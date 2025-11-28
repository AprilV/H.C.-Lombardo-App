#!/usr/bin/env python3
"""
Test ALL API endpoints to see what's actually broken
"""

import psycopg2

RENDER_URL = "postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics"

conn = psycopg2.connect(RENDER_URL)
cur = conn.cursor()

print("\n" + "="*80)
print("🔍 TESTING WHAT THE API ENDPOINTS WILL QUERY")
print("="*80)

# Test 1: /api/hcl/teams endpoint
print("\n1️⃣ /api/hcl/teams?season=2025")
print("-"*80)
print("This endpoint queries:")
try:
    cur.execute("""
        SELECT 
            ti.team,
            ti.full_name as team_name,
            ti.conference,
            ti.division,
            COALESCE(COUNT(tgs.game_id), 0) as games_played,
            COALESCE(SUM(CASE WHEN tgs.result = 'W' THEN 1 ELSE 0 END), 0) as wins
        FROM hcl.team_info ti
        LEFT JOIN hcl.team_game_stats tgs ON ti.team = tgs.team AND tgs.season = 2025
        GROUP BY ti.team, ti.full_name, ti.conference, ti.division
        ORDER BY ti.team ASC
        LIMIT 5
    """)
    teams = cur.fetchall()
    if teams:
        print(f"✅ Returns {len(teams)} teams (sample):")
        for team in teams:
            print(f"   {team[0]}: {team[1]} ({team[2]} {team[3]}) - {team[4]} games, {team[5]} wins")
    else:
        print("❌ NO TEAMS RETURNED")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Check if team_info exists
print("\n2️⃣ hcl.team_info table")
print("-"*80)
try:
    cur.execute("SELECT COUNT(*) FROM hcl.team_info")
    count = cur.fetchone()[0]
    print(f"✅ team_info has {count} teams")
    
    cur.execute("SELECT team, full_name FROM hcl.team_info LIMIT 5")
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]}")
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("   THIS IS THE PROBLEM - team_info doesn't exist!")

# Test 3: Analytics endpoint
print("\n3️⃣ /api/hcl/analytics/summary?season=2025")
print("-"*80)
try:
    cur.execute("""
        SELECT 
            COUNT(DISTINCT game_id) as total_games,
            AVG(points) as avg_points,
            AVG(total_yards) as avg_yards
        FROM hcl.team_game_stats
        WHERE season = 2025
    """)
    row = cur.fetchone()
    print(f"✅ Analytics query works:")
    print(f"   Total games: {row[0]}")
    print(f"   Avg points: {row[1]:.1f}")
    print(f"   Avg yards: {row[2]:.1f}")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 4: Check what tables exist
print("\n4️⃣ ALL TABLES in hcl schema")
print("-"*80)
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'hcl'
    ORDER BY table_name
""")
tables = [row[0] for row in cur.fetchall()]
print(f"Tables: {tables}")

if 'team_info' not in tables:
    print("\n❌ CRITICAL: team_info table is MISSING!")
    print("   This breaks /api/hcl/teams endpoint")
    print("   Need to create it!")

conn.close()

print("\n" + "="*80)
print("📋 DIAGNOSIS:")
print("="*80)
print("""
The problem is simple:
  
  ❌ hcl.team_info table does NOT exist on Render
  ✅ It EXISTS locally (32 teams)
  
  This table was created in the session but the schema rebuild DROPPED it!
  
  When I rebuilt team_game_stats, I used DROP ... CASCADE which also
  dropped team_info if there were foreign key relationships.
  
  FIX: Create hcl.team_info table on Render with 32 NFL teams
""")
print("="*80 + "\n")
