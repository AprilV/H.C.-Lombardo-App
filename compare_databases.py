#!/usr/bin/env python3
"""This script is obsolete - we only use EC2 localhost PostgreSQL database now.

To check database status, use:
- verify_2025.py
- check_2025_weeks.py  
- quick_check.py

Render database was deprecated and removed.
"""

print("⚠️  This script is obsolete. Render database no longer exists.")
print("Use verify_2025.py or check_2025_weeks.py instead.")


print("\n" + "="*80)
print("🔍 RENDER vs LOCAL DATABASE COMPARISON")
print("="*80)

# Connect to both
render_conn = psycopg2.connect(RENDER_URL)
render_cur = render_conn.cursor()

local_conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password='aprilv120',
    host='localhost',
    port='5432'
)
local_cur = local_conn.cursor()

# Compare team_game_stats columns
print("\n📊 TEAM_GAME_STATS COLUMNS:")
print("-"*80)

render_cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'team_game_stats'
    ORDER BY ordinal_position
""")
render_cols = {row[0] for row in render_cur.fetchall()}

local_cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'team_game_stats'
    ORDER BY ordinal_position
""")
local_cols = {row[0] for row in local_cur.fetchall()}

print(f"Render: {len(render_cols)} columns")
print(f"Local:  {len(local_cols)} columns")

if render_cols == local_cols:
    print("✅ SCHEMAS MATCH!")
else:
    missing = local_cols - render_cols
    extra = render_cols - local_cols
    if missing:
        print(f"\n❌ Missing on Render ({len(missing)}):")
        for col in sorted(missing):
            print(f"   • {col}")
    if extra:
        print(f"\n⚠️  Extra on Render ({len(extra)}):")
        for col in sorted(extra):
            print(f"   • {col}")

# Compare games columns
print("\n" + "="*80)
print("🏈 GAMES COLUMNS:")
print("-"*80)

render_cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'games'
    ORDER BY ordinal_position
""")
render_games_cols = {row[0] for row in render_cur.fetchall()}

local_cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'games'
    ORDER BY ordinal_position
""")
local_games_cols = {row[0] for row in local_cur.fetchall()}

print(f"Render: {len(render_games_cols)} columns")
print(f"Local:  {len(local_games_cols)} columns")

if render_games_cols == local_games_cols:
    print("✅ SCHEMAS MATCH!")
else:
    missing = local_games_cols - render_games_cols
    extra = render_games_cols - local_games_cols
    if missing:
        print(f"\n❌ Missing on Render ({len(missing)}):")
        for col in sorted(missing):
            print(f"   • {col}")
    if extra:
        print(f"\n⚠️  Extra on Render ({len(extra)}):")
        for col in sorted(extra):
            print(f"   • {col}")

# Compare data counts
print("\n" + "="*80)
print("📈 DATA COUNTS:")
print("-"*80)

render_cur.execute("SELECT COUNT(*) FROM hcl.games")
render_games = render_cur.fetchone()[0]
local_cur.execute("SELECT COUNT(*) FROM hcl.games")
local_games = local_cur.fetchone()[0]

render_cur.execute("SELECT COUNT(*) FROM hcl.team_game_stats")
render_stats = render_cur.fetchone()[0]
local_cur.execute("SELECT COUNT(*) FROM hcl.team_game_stats")
local_stats = local_cur.fetchone()[0]

print(f"\nGames:")
print(f"   Render: {render_games:,}")
print(f"   Local:  {local_games:,}")
print(f"   Status: {'✅ MATCH' if render_games == local_games else '⚠️  MISMATCH'}")

print(f"\nTeam Game Stats:")
print(f"   Render: {render_stats:,}")
print(f"   Local:  {local_stats:,}")
print(f"   Status: {'✅ MATCH' if render_stats == local_stats else '⚠️  MISMATCH'}")

# Check for NULL EPA values on Render
print("\n" + "="*80)
print("🔍 EPA DATA CHECK:")
print("-"*80)

render_cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(epa_per_play) as with_epa,
        COUNT(*) - COUNT(epa_per_play) as missing_epa
    FROM hcl.team_game_stats
""")
total, with_epa, missing = render_cur.fetchone()
print(f"\nRender EPA status:")
print(f"   Total records: {total:,}")
print(f"   With EPA: {with_epa:,}")
print(f"   Missing EPA: {missing:,}")
print(f"   Status: {'✅ ALL HAVE EPA' if missing == 0 else '⚠️  SOME MISSING EPA'}")

# Check 2025 specifically
render_cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(epa_per_play) as with_epa
    FROM hcl.team_game_stats
    WHERE season = 2025
""")
total_2025, epa_2025 = render_cur.fetchone()
print(f"\n2025 Season:")
print(f"   Total: {total_2025:,}")
print(f"   With EPA: {epa_2025:,}")
print(f"   Status: {'✅ ALL HAVE EPA' if total_2025 == epa_2025 else '⚠️  MISSING EPA'}")

render_conn.close()
local_conn.close()

print("\n" + "="*80)
print("✅ COMPARISON COMPLETE")
print("="*80 + "\n")
