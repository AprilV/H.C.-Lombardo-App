#!/usr/bin/env python3
"""Check ALL columns in local database to see what nflverse data we have"""

import psycopg2

print("\n" + "="*80)
print("📊 COMPLETE LOCAL DATABASE COLUMN INVENTORY")
print("="*80)

# Local database
local_conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password='aprilv120',
    host='localhost',
    port='5432'
)
local_cur = local_conn.cursor()

# Get all columns from team_game_stats
print("\n🏈 HCL.TEAM_GAME_STATS COLUMNS:")
print("-"*80)
local_cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'team_game_stats'
    ORDER BY ordinal_position
""")
columns = local_cur.fetchall()
print(f"\nTotal columns: {len(columns)}\n")

# Group by category
basic_stats = []
passing_stats = []
rushing_stats = []
epa_stats = []
betting_stats = []
other_stats = []

for col, dtype in columns:
    col_lower = col.lower()
    if any(x in col_lower for x in ['epa', 'wpa', 'cpoe', 'success']):
        epa_stats.append((col, dtype))
    elif any(x in col_lower for x in ['pass', 'completion', 'sack', 'interception', 'qb']):
        passing_stats.append((col, dtype))
    elif any(x in col_lower for x in ['rush', 'run']):
        rushing_stats.append((col, dtype))
    elif any(x in col_lower for x in ['spread', 'total', 'moneyline', 'line', 'odd']):
        betting_stats.append((col, dtype))
    elif any(x in col_lower for x in ['game_id', 'team', 'opponent', 'season', 'week', 'is_home', 'created', 'updated']):
        basic_stats.append((col, dtype))
    else:
        other_stats.append((col, dtype))

print("📌 BASIC INFO:")
for col, dtype in basic_stats:
    print(f"   • {col}: {dtype}")

print(f"\n🎯 GENERAL STATS ({len(other_stats)}):")
for col, dtype in other_stats:
    print(f"   • {col}: {dtype}")

print(f"\n🏈 PASSING STATS ({len(passing_stats)}):")
for col, dtype in passing_stats:
    print(f"   • {col}: {dtype}")

print(f"\n🏃 RUSHING STATS ({len(rushing_stats)}):")
for col, dtype in rushing_stats:
    print(f"   • {col}: {dtype}")

print(f"\n📊 EPA/ADVANCED STATS ({len(epa_stats)}):")
for col, dtype in epa_stats:
    print(f"   • {col}: {dtype}")

print(f"\n💰 BETTING DATA ({len(betting_stats)}):")
for col, dtype in betting_stats:
    print(f"   • {col}: {dtype}")

# Check games table too
print("\n" + "="*80)
print("🏈 HCL.GAMES COLUMNS:")
print("-"*80)
local_cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'games'
    ORDER BY ordinal_position
""")
games_cols = local_cur.fetchall()
print(f"\nTotal columns: {len(games_cols)}\n")

for col, dtype in games_cols:
    print(f"   • {col}: {dtype}")

# Sample data
print("\n" + "="*80)
print("📋 SAMPLE DATA (2025 Season):")
print("-"*80)
local_cur.execute("""
    SELECT game_id, team, points, total_yards, passing_yards, rushing_yards,
           epa_per_play, pass_epa, rush_epa, success_rate, cpoe
    FROM hcl.team_game_stats
    WHERE season = 2025
    ORDER BY game_id
    LIMIT 3
""")
print("\nSample team_game_stats:")
for row in local_cur.fetchall():
    print(f"   {row[0]} | {row[1]} | pts:{row[2]} yds:{row[3]} pass:{row[4]} rush:{row[5]} epa:{row[6]}")

local_conn.close()

print("\n" + "="*80)
print("✅ COLUMN INVENTORY COMPLETE")
print("="*80 + "\n")
