#!/usr/bin/env python3
"""
Check if local database is intact or if I damaged it
"""

import psycopg2

conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password='aprilv120',
    host='localhost',
    port='5432'
)
cur = conn.cursor()

print("\n" + "="*80)
print("🔍 LOCAL DATABASE INTEGRITY CHECK")
print("="*80)

# Check tables
print("\n1️⃣ Tables in hcl schema:")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'hcl'
    ORDER BY table_name
""")
tables = [r[0] for r in cur.fetchall()]
print(f"   {tables}")

# Check counts
print("\n2️⃣ Record counts:")
for table in ['games', 'team_game_stats']:
    cur.execute(f"SELECT COUNT(*) FROM hcl.{table}")
    count = cur.fetchone()[0]
    print(f"   {table}: {count:,}")

# Check team_game_stats columns
print("\n3️⃣ team_game_stats schema:")
cur.execute("""
    SELECT COUNT(*) 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'team_game_stats'
""")
col_count = cur.fetchone()[0]
print(f"   Columns: {col_count}")

# Check for EPA columns
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'team_game_stats'
    AND column_name LIKE '%epa%'
    ORDER BY column_name
""")
epa_cols = [r[0] for r in cur.fetchall()]
print(f"   EPA columns: {epa_cols}")

# Check 2025 data
print("\n4️⃣ 2025 Season data:")
cur.execute("SELECT COUNT(*) FROM hcl.games WHERE season = 2025")
games_2025 = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM hcl.team_game_stats WHERE season = 2025")
stats_2025 = cur.fetchone()[0]

cur.execute("""
    SELECT COUNT(*) 
    FROM hcl.team_game_stats 
    WHERE season = 2025 AND epa_per_play IS NOT NULL
""")
stats_with_epa = cur.fetchone()[0]

print(f"   Games: {games_2025}")
print(f"   Team stats: {stats_2025}")
print(f"   Stats with EPA: {stats_with_epa}")

# Sample data
print("\n5️⃣ Sample 2025 data (to verify integrity):")
cur.execute("""
    SELECT game_id, team, points, total_yards, epa_per_play, pass_epa
    FROM hcl.team_game_stats
    WHERE season = 2025
    ORDER BY week, game_id
    LIMIT 5
""")
for row in cur.fetchall():
    print(f"   {row[0]:20} | {row[1]:3} | pts:{row[2]:2} | yds:{row[3]:3} | epa:{row[4]:.3f if row[4] else 'NULL'} | pass_epa:{row[5]:.2f if row[5] else 'NULL'}")

conn.close()

print("\n" + "="*80)
print("📋 VERDICT:")
print("="*80)

print("""
Expected values (if database is intact):
  - team_game_stats: 14,398 records, 64 columns
  - games: 7,263 records
  - 2025 games: 272
  - 2025 team stats: 356 with EPA
  - EPA columns: epa_per_play, pass_epa, rush_epa, etc.

If any of these are different, the local database was damaged.
""")
print("="*80 + "\n")
